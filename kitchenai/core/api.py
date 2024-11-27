from ninja import File
from ninja import Router
from ninja import Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile
import nbformat
from nbconvert import PythonExporter
from llama_index.llms.groq import Groq
from llama_index.core import PromptTemplate
from django.template import loader
import requests
from urllib.request import urlopen
from .models import FileObject, EmbedObject
router = Router()

# Create a Schema that represents FileObject
class FileObjectSchema(Schema):
    name: str
    ingest_label: str | None = None
    metadata: dict[str, str] | None = None
    # Add any other fields from your FileObject model that you want to include
class FileObjectResponse(Schema):
    id: int
    name: str
    ingest_label: str
    metadata: dict[str,str]
    status: str

@router.get("/health")
async def default(request):
    return {"msg": "ok"}


@router.post("/file", response=FileObjectResponse)
async def file_upload(request, data: FileObjectSchema,file: UploadedFile = File(...)):
    """main entry for any file upload. Will upload via django storage and emit signals to any listeners"""
    file_object = await FileObject.objects.acreate(
        name=data.name,
        file=file,
        ingest_label=data.ingest_label,
        metadata=data.metadata if data.metadata else {},
        status=FileObject.Status.PENDING
    )
    return file_object


@router.get("/file/{pk}", response=FileObjectResponse)
async def file_get(request, pk: int):
    """get a file"""
    try:
        file_object = await FileObject.objects.aget(pk=pk)
        return file_object
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")



@router.delete("/file/{pk}")
async def file_delete(request, pk: int):
    """delete a file"""
    try:    
        await FileObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except FileObject.DoesNotExist:
        raise HttpError(404, "File not found")

@router.get("/file", response=list[FileObjectResponse])
def files_get(request):
    """get all files"""
    file_objects = FileObject.objects.all()
    return file_objects



class EmbedSchema(Schema):
    text: str
    ingest_label: str | None = None
    metadata: dict[str, str] | None = None

    # Add any other fields from your FileObject model that you want to include
class EmbedObjectResponse(Schema):
    id: int
    text: str
    ingest_label: str
    metadata: dict[str,str]
    status: str

#Embed Object API
@router.post("/embed", response=EmbedObjectResponse)
async def embed_create(request, data: EmbedSchema):
    """Create a new embed from text"""
    embed_object = await EmbedObject.objects.acreate(
        text=data.text,
        ingest_label=data.ingest_label,
        metadata=data.metadata if data.metadata else {},
        status=EmbedObject.Status.PENDING,
    )
    return embed_object

@router.get("/embed/{pk}", response=EmbedObjectResponse)
async def embed_get(request, pk: int):
    """Get an embed"""
    try:
        embed_object = await EmbedObject.objects.aget(
            pk=pk,
        )
        return embed_object
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")
    
@router.get("/embed", response=list[EmbedObjectResponse])
def embeds_get(request):
    """Get all embeds"""
    embed_objects = EmbedObject.objects.all()
    return embed_objects    

@router.delete("/embed/{pk}")
async def embed_delete(request, pk: int):
    """Delete an embed"""
    try:
        await EmbedObject.objects.filter(pk=pk).adelete()
        return {"msg": "deleted"}
    except EmbedObject.DoesNotExist:
        raise HttpError(404, "Embed not found")

@router.post("/module/upload")
def upload_notebook(request):

    base_url = "http://localhost:8888/api/contents"
    directory = "/notebook.ipynb"
    headers = {'Authorization': 'Token b6b795c663906f688727081ad75c3cae97d398bb156c0297'}

    response = requests.get(f"{base_url}{directory}", headers=headers)

    if response.status_code == 200:
        print(response.json())
        # notebooks = response.json()['content']
        # for notebook in notebooks:
        #     print(notebook['name'])
    else:
        print("Error:", response.status_code)

    print(response.json())

    # notebook = nbformat.reads(response.json(), as_version=4)
    # print(notebook.cells[0])
    # notebook_path = "playground.ipynb"
    # with open(notebook_path, "r", encoding="utf-8") as f:
    #     notebook = nbformat.read(f, as_version=4)

    # # Export to Python script
    # exporter = PythonExporter()
    # (script, resources) = exporter.from_notebook_node(notebook)



    # # api_key = os.environ.get("GROQ_API_KEY")
    # # if not api_key:
    # #     raise("error GROQ_API_KEY NEEDED")
    # # llm = Groq(model="llama3-70b-8192", api_key=api_key)
    # kitchenai_few_shot = loader.get_template('build_templates/app.tmpl')
    # prompt = loader.get_template('build_templates/cook.tmpl')

    # few_shot_rendered = kitchenai_few_shot.render()

    # prompt_rendered = prompt.render()

    # cook_prompt_template = PromptTemplate(
    #     prompt_rendered,
    # )

    # prompt_with_context = cook_prompt_template.format(context_str=script, few_shot_example=few_shot_rendered)

    # response = llm.complete(prompt_with_context)

    # Save as .py file
    # with open("app.py", "w", encoding="utf-8") as f:
    #     f.write(response.text)
    # with open("app-generate.py", "w", encoding="utf-8") as f:
    #     f.write(response.text)

    # print(prompt_with_context)
    return {"prompt" : "ok"}

@router.post("/pip/upload")
def upload_pip(request):

    url = "https://jakevdp.github.io/downloads/notebooks/XKCD_plots.ipynb"
    response = urlopen(url).read().decode()
    response[0:60] + " ..."

    notebook = nbformat.reads(response, as_version=4)
    print(notebook.cells[0])
    # notebook_path = "playground.ipynb"
    # with open(notebook_path, "r", encoding="utf-8") as f:
    #     notebook = nbformat.read(f, as_version=4)

    # Export to Python script
    exporter = PythonExporter()
    (script, resources) = exporter.from_notebook_node(notebook)



    # api_key = os.environ.get("GROQ_API_KEY")
    # if not api_key:
    #     raise("error GROQ_API_KEY NEEDED")
    # llm = Groq(model="llama3-70b-8192", api_key=api_key)
    kitchenai_few_shot = loader.get_template('build_templates/app.tmpl')
    prompt = loader.get_template('build_templates/cook.tmpl')

    few_shot_rendered = kitchenai_few_shot.render()

    prompt_rendered = prompt.render()

    cook_prompt_template = PromptTemplate(
        prompt_rendered,
    )

    prompt_with_context = cook_prompt_template.format(context_str=script, few_shot_example=few_shot_rendered)

    # response = llm.complete(prompt_with_context)

    # Save as .py file
    # with open("app.py", "w", encoding="utf-8") as f:
    #     f.write(response.text)
    # with open("app-generate.py", "w", encoding="utf-8") as f:
    #     f.write(response.text)

    # print(prompt_with_context)
    return {"prompt" : prompt_with_context}