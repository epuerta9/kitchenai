"""
License
=======

Do whatever you like.

Usage
=====

1. put it in your project

  manage.py
  base/
    management/
      commands/
        __init__.py
        runserver.py
"""

from django.conf import settings
from django.core.management.commands.runserver import Command as RunserverCommand
import os



class Command(RunserverCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--module',
            dest='module_path',
            default=None,
            help='Specifies the kitchenai module to load'
        )

    def run(self, *args, **options):
        """Runs the server"""
        # Check if this is the main process
        if os.environ.get('RUN_MAIN') == 'true':
            if settings.KITCHENAI_DEBUG or settings.DEBUG:
                from kitchenai.api import api
                from kitchenai.core.utils import setup
                from kitchenai.bento.models import Bento

                module = options.get('module_path')
                if module:
                    setup(api, module=module)
                    self.stdout.write(self.style.SUCCESS(f"Loaded module: {module}"))
                else:
                    try:
                        bento_box = Bento.objects.first()
                        if not bento_box:
                            self.stdout.write(self.style.ERROR("No bento box loaded. Please run 'bento select' to select a bento box."))
                            raise Exception("No bento box loaded. Please run 'bento select' to select a bento box.")
                        bento_box.add_to_core()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error loading bento box: {e}"))
                        raise Exception(f"Error loading bento box: {e}")
            else:
                raise Exception("KitchenAI is not in debug mode when running dev server. Please set KITCHENAI_DEBUG=True in your settings.py file.")

        # Always call the parent run method to start the server
        super().run(*args, **options)