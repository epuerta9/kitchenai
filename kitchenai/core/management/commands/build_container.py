import logging
import pathlib

import yaml
from django.core.management.base import BaseCommand
from django.template import loader


logger = logging.getLogger("kitchenai.core.commands")


class Command(BaseCommand):
    help = 'Builds kitchenai'

    def handle(self, *args, **options):
        """Checks to see if there is a kitchen.yml in the root directory, loads and initializes the db"""

        config = pathlib.Path.cwd() / "kitchenai.yml"
        config_data = self.read_yaml_config(config)

        if config_data:
            # Save the configuration to the database
            template_name = 'build_templates/Dockerfile.tmpl'

            # Context data to pass into the template
            context = {
                'title': 'Django Template Rendering',
                'message': 'This is rendered via a custom management command!'
            }

            try:
                # Load the template
                template = loader.get_template(template_name)

                # Render the template with the context data
                rendered_content = template.render(context)

                # Output to standard output
                self.stdout.write(self.style.SUCCESS(rendered_content))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error rendering template: {e}"))
        else:
            self.stdout.write(self.style.ERROR('No config file for kitchenai.'))

    def read_yaml_config(self, yaml_file_path):

        # Check if the file exists
        if not yaml_file_path.is_file():
            self.stdout.write(self.style.ERROR("YAML config file kitchenai.yml not found."))
            return None

        # Read the YAML file
        with open(yaml_file_path) as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                self.stdout.write(self.style.ERROR(f"Error reading YAML file: {e}"))
                return None
