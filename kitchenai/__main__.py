import sys

import django


def main() -> None:
    from pathlib import Path
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kitchenai.settings")
    current_path = Path(__file__).parent.parent.resolve()
    sys.path.append(str(current_path))

    django.setup()
    from kitchenai.cli.main import app

    app()


# def _run_gunicorn(argv: list) -> None:
#     """
#     Run gunicorn the wsgi server.
#     https://docs.gunicorn.org/en/stable/settings.html
#     https://adamj.eu/tech/2021/12/29/set-up-a-gunicorn-configuration-file-and-test-it/
#     """
#     import multiprocessing
#     from gunicorn.app import wsgiapp

#     workers = multiprocessing.cpu_count() * 2 + 1
#     gunicorn_args = [
#         "kitchenai.wsgi:application",
#         "--bind",
#         "0.0.0.0:8000",
#         # "unix:/run/kitchenai.gunicorn.sock", # uncomment this line and comment the line above to use a socket file
#         "--max-requests",
#         "1000",
#         "--max-requests-jitter",
#         "50",
#         "--workers",
#         str(workers),
#         "--access-logfile",
#         "-",
#         "--error-logfile",
#         "-",
#     ]
#     argv.extend(gunicorn_args)
#     wsgiapp.run()

if __name__ == "__main__":
    main()
