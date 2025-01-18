from typer.testing import CliRunner
from whisk.whisk.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "KitchenAI Whisk v" in result.stdout 