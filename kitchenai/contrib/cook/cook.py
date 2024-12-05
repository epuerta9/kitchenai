from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from asgiref.sync import sync_to_async
import os
import django
import hashlib
import asyncio
import nest_asyncio
from llama_index.llms.openai import OpenAI

from contextlib import redirect_stdout, redirect_stderr
import io

# Setup Django and nest_asyncio
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")
django.setup()
nest_asyncio.apply()

from kitchenai.core.models import CodeFunction,Notebook, CodeImport, CodeSetup
from llama_index.core import PromptTemplate
from django.template import loader


@magics_class
class Cook(Magics):

    def __init__(self, shell):
        super().__init__(shell)  # Initialize the base class
        self.project_name = ""  # Define the class attribute here


    async def get_notebook(self):
            from kitchenai.core.models import Notebook

            try:
                existing_entry = await sync_to_async(Notebook.objects.filter(name=self.project_name).first)()
            except Notebook.DoesNotExist:
                raise Notebook.DoesNotExist

            return existing_entry 
    

    @line_magic
    def kitchenai_get_project(self, line):
        from kitchenai.core.models import Notebook

        async def process_code():
            # Check if a CodeFunction with this label exists
            try:
                existing_entry = await sync_to_async(Notebook.objects.filter(name=self.project_name).first)()
            except Notebook.DoesNotExist:
                return "notebook does not exist"

            return existing_entry


        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_code())  

    @line_magic
    def kitchenai_set_project(self, line):
        """
        Set the project name for the Cook magic commands.
        Usage: %set_project_name MyProject
        """
        
        if not line.strip():
            return "Error: Project name cannot be empty."

        self.project_name = line.strip()
        async def process_code():
            # Check if a CodeFunction with this label exists
            existing_entry = await sync_to_async(Notebook.objects.filter(name=self.project_name).first)()

            if existing_entry:
                # If the hash matches, do nothing
                return f"Project {self.project_name} already exists."

            # Create a new entry
            new_entry = Notebook(name=self.project_name)
            await sync_to_async(new_entry.save)()
            return f"Registered new project {self.project_name}"

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_code())
        else:
            result = asyncio.run(process_code())


        return f"Project name set to '{self.project_name}'."


    @cell_magic
    def kitchenai_register(self, line, cell):
        """
        Custom magic command to register a code block with a type (storage, query, etc.)
        and a user-defined label.
        """

        # Parse the type and label from the line (e.g., %%kitchen_register storage my-label)
        parts = line.strip().split(" ")
        if len(parts) != 2:
            return "Usage: %%kitchen_register <type> <label>"

        func_type, label = parts
        func_type = func_type.lower()
        if func_type not in CodeFunction.FuncType.values:
            return f"Invalid function type '{func_type}'. Must be one of: {', '.join(CodeFunction.FuncType.values)}"

        # Hash the cell content
        cell_hash = hashlib.sha256(cell.encode()).hexdigest()

        async def process_code():
            # Check if a CodeFunction with this label exists
            existing_entry = await sync_to_async(CodeFunction.objects.filter(type=func_type, label=label, notebook__name=self.project_name).first)()

            if existing_entry:
                # If the hash matches, do nothing
                if existing_entry.hash == cell_hash:
                    return f"Function '{label}' of type '{func_type}' is already registered with the same code."

                # Otherwise, update the existing entry
                existing_entry.hash = cell_hash
                existing_entry.raw_code = cell
                await sync_to_async(existing_entry.save)()
                return f"Updated function '{label}' of type '{func_type}' with new code."

            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."


            # Create a new entry
            new_entry = CodeFunction(hash=cell_hash, raw_code=cell, label=label, type=func_type, notebook=notebook)
            await sync_to_async(new_entry.save)()
            return f"Registered new function '{label}' of type '{func_type}' with hash {cell_hash}."

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_code())
        else:
            result = asyncio.run(process_code())

        print(f"kitchenai_result: {result}")

        ipython = get_ipython()
        ipython.run_cell(cell)



    @cell_magic
    def kitchenai_import(self, line, cell):
        """
        Custom magic command to handle code imports by checking the hash.
        If the hash matches an existing entry, do nothing.
        If the hash differs or the entry doesn't exist, save it.
        """

        # Hash the cell content
        cell_hash = hashlib.sha256(cell.encode()).hexdigest()

        label =  line.strip()

        async def process_import():
            # Check if a CodeImport entry with this hash exists
            existing_entry = await sync_to_async(CodeImport.objects.filter(hash=cell_hash, label=label, notebook__name=self.project_name).first)()

            if existing_entry:
                # If the hash matches, do nothing
                # If the hash matches, do nothing
                if existing_entry.hash == cell_hash:
                    return f"import '{label}' is already registered with the same code."

                # Otherwise, update the existing entry
                existing_entry.hash = cell_hash
                existing_entry.code = cell

                await sync_to_async(existing_entry.save)()
                return f"Updated import '{label}'with new code."
            
            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."

            # Create a new entry
            new_entry = CodeImport(hash=cell_hash, code=cell, notebook=notebook, label=label)
            await sync_to_async(new_entry.save)()
            return f"Registered new CodeImport with hash {cell_hash}."

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_import())
        else:
            result = asyncio.run(process_import())

        print(f"kitchenai_result: {result}")

        ipython = get_ipython()
        ipython.run_cell(cell)

    


    @cell_magic
    def kitchenai_setup(self, line, cell):
        """
        Custom magic command to handle code setups by checking the hash.
        If the hash matches an existing entry, do nothing.
        If the hash differs or the entry doesn't exist, save it.
        """

        # Hash the cell content
        cell_hash = hashlib.sha256(cell.encode()).hexdigest()

        label = line.strip()

        async def process_setup():
            # Check if a CodeSetup entry with this hash exists
            existing_entry = await sync_to_async(CodeSetup.objects.filter(hash=cell_hash, label=label, notebook__name=self.project_name).first)()

            if existing_entry:
                # If the hash matches, do nothing
                # If the hash matches, do nothing
                if existing_entry.hash == cell_hash:
                    return f"setup '{label}' is already registered with the same code."

                # Otherwise, update the existing entry
                existing_entry.hash = cell_hash
                existing_entry.code = cell

                await sync_to_async(existing_entry.save)()
                return f"Updated setup '{label}'with new code."
            
            # Ensure the associated notebook exists
            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."

            # Create a new CodeSetup entry
            new_entry = CodeSetup(hash=cell_hash, code=cell, notebook=notebook)
            await sync_to_async(new_entry.save)()
            return f"Registered new CodeSetup with hash {cell_hash}."

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_setup())
        else:
            result = asyncio.run(process_setup())

        # Execute the code in the current namespace
        print(f"kitchenai_result: {result}")

        ipython = get_ipython()
        ipython.run_cell(cell)


    @line_magic
    def kitchenai_create_module(self, line):

        async def process_setup():
            # Check if a CodeSetup entry with this hash exists
            code_setups = await sync_to_async(list)(
                CodeSetup.objects.filter(notebook__name=self.project_name).select_related('notebook')
            )
            code_imports = await sync_to_async(list)(
                CodeImport.objects.filter(notebook__name=self.project_name).select_related('notebook')
            )
            code_functions = await sync_to_async(list)(
                CodeFunction.objects.filter(notebook__name=self.project_name).select_related('notebook')
            )


            context = {
                "code_setups" : code_setups,
                "code_imports": code_imports,
                "code_functions" : code_functions
            }

            llm = OpenAI(model="gpt-4")
            kitchenai_few_shot = loader.get_template('build_templates/app.tmpl')
            prompt = loader.get_template('build_templates/cook.tmpl')

            kitchenai_module = loader.get_template("build_templates/cook_jupyter.tmpl")

            #this gets us to the comments with the saved code sections.
            kitchenai_module_rendered = await sync_to_async(kitchenai_module.render)(context=context)


            few_shot_rendered = kitchenai_few_shot.render()

            prompt_rendered = prompt.render()

            cook_prompt_template = PromptTemplate(
                prompt_rendered,
            )

            prompt_with_context = cook_prompt_template.format(context_str=kitchenai_module_rendered, few_shot_example=few_shot_rendered)

            response = llm.complete(prompt_with_context)

            # Save as .py file
            with open("app.py", "w", encoding="utf-8") as f:
                f.write(response.text)


            # Create a new CodeSetup entry
            return f"Created app.py"

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_setup())
        else:
            result = asyncio.run(process_setup())

        print(f"kitchenai_result: {result}")
