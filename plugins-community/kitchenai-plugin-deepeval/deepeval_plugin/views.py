from django.db.models import Avg, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import (
    DataSet, Data, AnswerRelevance, Faithfulness, 
    ContextualRelevancy, Hallucination, Toxicity, Settings
)
from django.http import HttpResponse

from falco_toolbox.types import HttpRequest
import logging

logger = logging.getLogger(__name__)

@login_required
def home(request: HttpRequest):
    # Get all datasets with their metrics in one query
    datasets = DataSet.objects.annotate(
        avg_answer_relevance=Coalesce(Avg('data__answerrelevance__score'), 0.0),
        avg_faithfulness=Coalesce(Avg('data__faithfulness__score'), 0.0),
        avg_contextual_relevancy=Coalesce(Avg('data__contextualrelevancy__score'), 0.0),
        avg_hallucination=Coalesce(Avg('data__hallucination__score'), 0.0),
        avg_toxicity=Coalesce(Avg('data__toxicity__score'), 0.0),
    )

    datasets_data = []
    for dataset in datasets:
        # Get recent evaluations for this dataset
        recent_data = Data.objects.filter(
            dataset_id=dataset.id
        ).order_by('-created_at')[:5].values(
            'source_id', 'input', 'created_at'
        )

        # Get all metric scores for these recent evaluations in one query
        recent_metrics = Data.objects.filter(
            dataset_id=dataset.id,
            source_id__in=[d['source_id'] for d in recent_data]
        ).values(
            'source_id',
            'answerrelevance__score',
            'faithfulness__score',
            'contextualrelevancy__score',
            'hallucination__score',
            'toxicity__score'
        )

        # Create a lookup of scores by source_id
        metrics_by_source = {
            m['source_id']: [
                score for score in [
                    m['answerrelevance__score'],
                    m['faithfulness__score'],
                    m['contextualrelevancy__score'],
                    m['hallucination__score'],
                    m['toxicity__score']
                ] if score is not None
            ] for m in recent_metrics
        }

        # Calculate average scores for recent evaluations
        for eval in recent_data:
            scores = metrics_by_source.get(eval['source_id'], [])
            eval['avg_score'] = sum(scores) / len(scores) if scores else 0

        datasets_data.append({
            'id': dataset.id,
            'name': dataset.name,
            'enabled': dataset.enabled,
            'metrics': {
                'answer_relevance': dataset.avg_answer_relevance,
                'faithfulness': dataset.avg_faithfulness,
                'contextual_relevancy': dataset.avg_contextual_relevancy,
                'hallucination': dataset.avg_hallucination,
                'toxicity': dataset.avg_toxicity,
            },
            'recent_evaluations': list(recent_data),
        })

    total_evaluations = Data.objects.count()
    active_datasets = DataSet.objects.filter(enabled=True).count()

    return TemplateResponse(
        request,
        'deepeval_plugin/pages/home.html',
        {
            'datasets': datasets_data,
            'total_evaluations': total_evaluations,
            'active_datasets': active_datasets,
        }
    )

@login_required
@require_http_methods(["GET", "POST"])
def settings(request):
    if request.method == "POST":
        settings = Settings.get_settings()
        
        # Update settings based on form data
        settings.is_answer_relevance_enabled = request.POST.get('is_answer_relevance_enabled') == 'on'
        settings.is_faithfulness_enabled = request.POST.get('is_faithfulness_enabled') == 'on'
        settings.is_contextual_relevancy_enabled = request.POST.get('is_contextual_relevancy_enabled') == 'on'
        settings.is_hallucination_enabled = request.POST.get('is_hallucination_enabled') == 'on'
        settings.is_toxicity_enabled = request.POST.get('is_toxicity_enabled') == 'on'
        
        settings.save()
        
        # If it's an HTMX request, return a success response
        if request.headers.get('HX-Request'):
            response = TemplateResponse(
                request,
                'deepeval_plugin/components/toast.html',
                {'message': 'Settings updated successfully!'}
            )
            # Clear any existing messages
            storage = messages.get_messages(request)
            for _ in storage:
                pass  # Iterate through to mark messages as used
            storage.used = True
            return response
        
        # For regular requests, add message and redirect
        messages.success(request, "Settings updated successfully!")
        return redirect('deepeval:settings')

    # GET request handling
    from django.conf import settings as django_settings
    plugin_descriptions = django_settings.KITCHENAI["plugins"]

    for plugin in plugin_descriptions:
        if plugin["name"] == "deepeval_plugin":
            plugin_descriptions = plugin
            break

    plugin_settings = django_settings.DEEPEVAL_PLUGIN
    test_settings = Settings.get_settings()

    return TemplateResponse(
        request,
        'deepeval_plugin/pages/settings.html',
        {
            "plugin_settings": plugin_settings,
            "plugin_descriptions": plugin_descriptions,
            "test_settings": test_settings,
        }
    )

@login_required
def dataset(request, dataset_id: int):
    # Get dataset
    dataset = DataSet.objects.get(id=dataset_id)

    # Get page number from request
    page = request.GET.get('page', 1)
    
    # Get all data entries for this dataset with metrics and their reasons
    entries = Data.objects.filter(
        dataset_id=dataset_id
    ).values(
        'source_id',
        'input',
        'output',
        'created_at',
    ).annotate(
        answer_relevance=Coalesce(
            Subquery(
                AnswerRelevance.objects.filter(data_id=OuterRef('id')).values('score')[:1]
            ), None
        ),
        answer_relevance_reason=Coalesce(
            Subquery(
                AnswerRelevance.objects.filter(data_id=OuterRef('id')).values('reason')[:1]
            ), None
        ),
        faithfulness=Coalesce(
            Subquery(
                Faithfulness.objects.filter(data_id=OuterRef('id')).values('score')[:1]
            ), None
        ),
        faithfulness_reason=Coalesce(
            Subquery(
                Faithfulness.objects.filter(data_id=OuterRef('id')).values('reason')[:1]
            ), None
        ),
        contextual_relevancy=Coalesce(
            Subquery(
                ContextualRelevancy.objects.filter(data_id=OuterRef('id')).values('score')[:1]
            ), None
        ),
        contextual_relevancy_reason=Coalesce(
            Subquery(
                ContextualRelevancy.objects.filter(data_id=OuterRef('id')).values('reason')[:1]
            ), None
        ),
        hallucination=Coalesce(
            Subquery(
                Hallucination.objects.filter(data_id=OuterRef('id')).values('score')[:1]
            ), None
        ),
        hallucination_reason=Coalesce(
            Subquery(
                Hallucination.objects.filter(data_id=OuterRef('id')).values('reason')[:1]
            ), None
        ),
        toxicity=Coalesce(
            Subquery(
                Toxicity.objects.filter(data_id=OuterRef('id')).values('score')[:1]
            ), None
        ),
        toxicity_reason=Coalesce(
            Subquery(
                Toxicity.objects.filter(data_id=OuterRef('id')).values('reason')[:1]
            ), None
        )
    ).order_by('-created_at')

    # Set up pagination
    paginator = Paginator(entries, 10)  # Show 10 entries per page
    try:
        pagination = paginator.page(page)
    except PageNotAnInteger:
        pagination = paginator.page(1)
    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)
    
    return TemplateResponse(
        request,
        'deepeval_plugin/pages/dataset.html',
        {
            'dataset': dataset,
            'entries': pagination,
            'pagination': pagination,
        }
    )

@login_required
async def chat_widget_for_source(request: HttpRequest, source_id: int):
    # Check if this is a chat send event
    #this means the user has sent a message and we need to run the tests. we now know which tests we need to poll for
    is_chat_send = request.GET.get('event') == 'chat_send'

    # Get settings and create a map of enabled tests
    settings = await Settings.objects.aget_or_create(defaults={'name': 'Default Settings'})
    settings = settings[0]
    
    enabled_tests = {
        'answer_relevance': settings.is_answer_relevance_enabled,
        'faithfulness': settings.is_faithfulness_enabled,
        'contextual_relevancy': settings.is_contextual_relevancy_enabled,
        'hallucination': settings.is_hallucination_enabled,
        'toxicity': settings.is_toxicity_enabled
    }
    
    # If all tests are disabled, return disabled widget
    if not any(enabled_tests.values()):
        return TemplateResponse(
            request,
            "deepeval_plugin/widgets/disabled_widget.html",
            {}
        )
    
    if is_chat_send:
        #send back the htmx poller for that specific test
        #find the enabled tests only
        enabled_tests = {k: v for k, v in enabled_tests.items() if v}
        return TemplateResponse(
            request,
            "deepeval_plugin/htmx/evaluation_test.html",
            {
                "source_id": source_id,
                "enabled_tests": enabled_tests,
            }
        )
    results = {
        "source_id": source_id,
        "enabled_tests": enabled_tests,
        "answer_relevance": await AnswerRelevance.objects.filter(data__source_id=source_id).afirst() if enabled_tests['answer_relevance'] else None,
        "faithfulness": await Faithfulness.objects.filter(data__source_id=source_id).afirst() if enabled_tests['faithfulness'] else None,
        "contextual_relevancy": await ContextualRelevancy.objects.filter(data__source_id=source_id).afirst() if enabled_tests['contextual_relevancy'] else None,
        "hallucination": await Hallucination.objects.filter(data__source_id=source_id).afirst() if enabled_tests['hallucination'] else None,
        "toxicity": await Toxicity.objects.filter(data__source_id=source_id).afirst() if enabled_tests['toxicity'] else None
    }

    return TemplateResponse(
        request,
        "deepeval_plugin/widgets/chat_widget.html",
        results
    )
@login_required
def check_results(request: HttpRequest, source_id: int, test_name: str):
    # a poller will check this endpoint and return the test result for that section
    # if the test result is not ready, it will return a loading message
    # if the test result is ready, it will return the test result

    # get the data instance
    data = Data.objects.filter(source_id=source_id).first()

    if not data:
        return HttpResponse("")
    
    evaluation = data.get_test_result(test_name)


    if evaluation is None:
        return TemplateResponse(
            request,
            "deepeval_plugin/htmx/check_results.html",
            {
                "source_id": source_id,
                "test_name": test_name,
                "evaluation": None,
            }
        )
    component_name = data.get_component_name(test_name)

    return TemplateResponse(
        request,
        component_name,
        {
            "source_id": source_id,
            "test_name": test_name,
            "evaluation": evaluation,
        }
    )