from django.shortcuts import render

# Create your views here.


from django.template.response import TemplateResponse

from falco_toolbox.types import HttpRequest
import json

from .models import AnswerRelevance
from .utils import format_deepeval_logs
import logging

logger = logging.getLogger(__name__)
# Create your views here.

async def home(request: HttpRequest):
    return TemplateResponse(
        request,
        "deepeval_plugin/pages/home.html",
    )


async def chat_widget_for_source(request: HttpRequest, source_id: int):
    try:
        answer_relevance = await AnswerRelevance.objects.aget(data__source_id=source_id)
    except AnswerRelevance.DoesNotExist:
        answer_relevance = None
        return TemplateResponse(
            request,
            "deepeval_plugin/widgets/chat_widget.html",
            {"answer_relevance": answer_relevance, "source_id": source_id},
            headers={"HX-Reswap": "none"}  # Prevents content update but continues polling
        )
    # Format the logs for display
    return TemplateResponse(
        request,
        "deepeval_plugin/widgets/chat_widget.html",
        {"answer_relevance": answer_relevance, "source_id": source_id, "formatted_logs": format_deepeval_logs(answer_relevance.verbose_logs)},
    )