from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from asgiref.sync import sync_to_async
import os
import django
import hashlib
import asyncio
import nest_asyncio


# Setup Django and nest_asyncio
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")
django.setup()
nest_asyncio.apply()

from kitchenai.notebooks.models import CodeFunction,Notebook, CodeImport, CodeSetup
from django.template import loader
from django.conf import settings
from django.template import Template, Context



@magics_class
class NotebookMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell)  # Initialize the base class
        self.project_name = ""  # Define the class attribute here
        self.llm_provider = settings.KITCHENAI_LLM_PROVIDER
        self.llm_model = settings.KITCHENAI_LLM_MODEL


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
            existing_entry = await sync_to_async(CodeFunction.objects.filter(
                type=func_type, label=label, notebook__name=self.project_name
            ).first)()

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
            new_entry = CodeFunction(
                hash=cell_hash, raw_code=cell, label=label, type=func_type, notebook=notebook
            )
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

        # Execute the cell code and add variables to the IPython namespace
        ipython = get_ipython()
        ipython.run_cell(cell)


    @line_magic
    def kitchenai_register_previous_cell(self, line):
        """
        Custom magic command to register a code block with a type (storage, query, etc.)
        and a user-defined label.
        """
        ipython = get_ipython()

        # Get the actual previous cell content by looking two steps back in the history
        history = ipython.history_manager.input_hist_parsed
        if len(history) < 2:
            return "No previous cell content found to register."
        previous_cell = history[-2]  # The second-to-last entry is the previous cell

        # Calculate the hash of the previous cell's content
        cell_hash = hashlib.sha256(previous_cell.encode()).hexdigest()
        label = line.strip()


        # Parse the type and label from the line (e.g., %%kitchen_register storage my-label)
        parts = line.strip().split(" ")
        if len(parts) != 2:
            return "Usage: %%kitchen_register <type> <label>"

        func_type, label = parts
        func_type = func_type.lower()
        if func_type not in CodeFunction.FuncType.values:
            return f"Invalid function type '{func_type}'. Must be one of: {', '.join(CodeFunction.FuncType.values)}"


        async def process_code():
            # Check if a CodeFunction with this label exists
            existing_entry = await sync_to_async(CodeFunction.objects.filter(
                type=func_type, label=label, notebook__name=self.project_name
            ).first)()

            if existing_entry:
                # If the hash matches, do nothing
                if existing_entry.hash == cell_hash:
                    return f"Function '{label}' of type '{func_type}' is already registered with the same code."

                # Otherwise, update the existing entry
                existing_entry.hash = cell_hash
                existing_entry.raw_code = previous_cell
                await sync_to_async(existing_entry.save)()
                return f"Updated function '{label}' of type '{func_type}' with new code."

            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."

            # Create a new entry
            new_entry = CodeFunction(
                hash=cell_hash, raw_code=previous_cell, label=label, type=func_type, notebook=notebook
            )
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


    @line_magic
    def kitchenai_import_previous_cell(self, line):
        """
        Custom magic command to handle code imports by checking the hash.
        If the hash matches an existing entry, do nothing.
        If the hash differs or the entry doesn't exist, save it.
        """
        ipython = get_ipython()

        # Get the actual previous cell content by looking two steps back in the history
        history = ipython.history_manager.input_hist_parsed
        if len(history) < 2:
            return "No previous cell content found to register."
        previous_cell = history[-2]  # The second-to-last entry is the previous cell

        # Calculate the hash of the previous cell's content
        cell_hash = hashlib.sha256(previous_cell.encode()).hexdigest()
        label = line.strip()

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
                existing_entry.code = previous_cell

                await sync_to_async(existing_entry.save)()
                return f"Updated import '{label}'with new code."
            
            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."

            # Create a new entry
            new_entry = CodeImport(hash=cell_hash, code=previous_cell, notebook=notebook, label=label)
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

    @line_magic
    def kitchenai_llm_model(self, line):
        """
        Set the LLM model for the Cook magic commands.
        Usage: %kitchenai_llm_model openai
        """
        config = line.strip().split(" ")
        if config and config[0] not in ["openai", "ollama"]:
            return f"Invalid LLM model '{line.strip()}'. Must be one of: {', '.join(['openai', 'ollama'])}"

        self.llm_provider = config[0] if config else settings.KITCHENAI_LLM_MODEL
        self.llm_model = config[1] if config else settings.KITCHENAI_LLM_PROVIDER
    


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
    def kitchenai_setup_previous_cell(self, line):
        """
        Custom magic command to register the contents of the previous cell.
        Usage:
            %kitchenai_setup_previous_cell <label>
        """
        # Access the IPython instance
        ipython = get_ipython()

        # Get the actual previous cell content by looking two steps back in the history
        history = ipython.history_manager.input_hist_parsed
        if len(history) < 2:
            return "No previous cell content found to register."
        previous_cell = history[-2]  # The second-to-last entry is the previous cell

        # Calculate the hash of the previous cell's content
        cell_hash = hashlib.sha256(previous_cell.encode()).hexdigest()
        label = line.strip()

        async def process_setup():
            # Check if a CodeSetup entry with this hash exists
            existing_entry = await sync_to_async(
                CodeSetup.objects.filter(hash=cell_hash, label=label, notebook__name=self.project_name).first
            )()

            if existing_entry:
                # If the hash matches, do nothing
                if existing_entry.hash == cell_hash:
                    return f"setup '{label}' is already registered with the same code."

                # Otherwise, update the existing entry
                existing_entry.hash = cell_hash
                existing_entry.code = previous_cell
                await sync_to_async(existing_entry.save)()
                return f"Updated setup '{label}' with new code."

            # Ensure the associated notebook exists
            try:
                notebook = await sync_to_async(Notebook.objects.get)(name=self.project_name)
            except Notebook.DoesNotExist:
                return f"No notebook found with name '{self.project_name}'. Please create it first."

            # Create a new CodeSetup entry
            new_entry = CodeSetup(hash=cell_hash, code=previous_cell, label=label, notebook=notebook)
            await sync_to_async(new_entry.save)()
            return f"Registered new CodeSetup with hash {cell_hash}."

        # Run the async process
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
            result = loop.run_until_complete(process_setup())
        else:
            result = asyncio.run(process_setup())

        # Output the result
        print(f"kitchenai_result: {result}")

    @line_magic
    def kitchenai_create_module(self, line):
        """
        Create a kitchenai app.py file from the registered code.
        """
        from llama_index.core import PromptTemplate

        verbose = line.strip() == "verbose"

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
            if self.llm_provider == "openai":
                from llama_index.llms.openai import OpenAI
                llm = OpenAI(model=self.llm_model)
            else:
                from llama_index.llms.ollama import Ollama
                llm = Ollama(model=self.llm_model)

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
            
            if verbose:
                print(f"kitchenai_prompt_with_context: {prompt_with_context}")
                print("--------------------------------")

            response = llm.complete(prompt_with_context)

            if verbose: 
                print(f"kitchenai_response: {response.text}")
                print("--------------------------------")

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



    @line_magic
    def kitchenai_template(self, line):
        """
        Magic command to dynamically replace the current cell content with a Django-rendered template.
        If the generated content already exists in the next cell, it skips creating a new cell.
        Usage:
            %kitchenai_template <function_name>
        """
        from django.template import Context
        from IPython import get_ipython

        # Parse the function name from the line
        parts = line.strip().split(" ")
        if len(parts) > 2:
            return "Usage: %%kitchen_register <type> <label> | %%kitchenai_register <type>"

        func_type = parts[0].lower()
        label = parts[1] if len(parts) == 2 else self.project_name
        import random
        import string

        # Generate func_name based on label or random string
        if len(parts) == 2:
            func_name = label
        else:
            random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
            func_name = f"{self.project_name.replace('-', '_')}_{random_str}"

        # Define your Django templat
        template = loader.get_template(f"notebooks/{func_type}.tmpl")

        # Render the template
        rendered_code = template.render({"label": label, "func_type": func_type, "func_name": func_name, "project_name": self.project_name})

        # Access the notebook's cell content
        ipython = get_ipython()
        # If no matching cell is found, create a new one
        ipython.set_next_input(rendered_code)

    @line_magic
    def kitchenai_help(line):
        """Display help for KitchenAI magic commands"""
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title="KitchenAI Magic Commands")
        
        # Add columns
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Example", style="yellow")

        # Add rows
        table.add_row(
            "%load_env", 
            "Line", 
            "Load environment variables from .env file",
            "%load_env"
        )
        table.add_row(
            "%connect_db", 
            "Line", 
            "Connect to the database specified in environment",
            "%connect_db"
        )
        table.add_row(
            "%%sql", 
            "Cell", 
            "Execute SQL query and return results as DataFrame",
            "%%sql\nSELECT * FROM users"
        )
        table.add_row(
            "%sql", 
            "Line", 
            "Execute single line SQL query",
            "%sql SELECT count(*) FROM users"
        )
        table.add_row(
            "%%rag", 
            "Cell", 
            "Execute RAG query with custom prompt",
            "%%rag\nFind documents about machine learning"
        )
        table.add_row(
            "%rag", 
            "Line", 
            "Quick RAG query with default prompt",
            "%rag What are the latest sales figures?"
        )
        table.add_row(
            "%kitchenai_config", 
            "Line", 
            "Display current KitchenAI configuration",
            "%kitchenai_config"
        )
        table.add_row(
            "%upload_file", 
            "Line", 
            "Upload file to KitchenAI storage",
            "%upload_file path/to/file.pdf"
        )
        table.add_row(
            "%list_files", 
            "Line", 
            "List all files in KitchenAI storage",
            "%list_files"
        )
        table.add_row(
            "%embed", 
            "Line", 
            "Create embeddings for a file",
            "%embed file_id"
        )

        # Print the table
        console.print(table)

        return None
