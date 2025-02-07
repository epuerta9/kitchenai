import sys

import django
import warnings
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2", category=UserWarning)

def main() -> None:
    from pathlib import Path
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")
    current_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(current_path))
    django.setup()
    from kitchenai.cli.main import app

    app()


if __name__ == "__main__":
    main()
