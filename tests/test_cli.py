# tests/test_cli.py
import os
import shutil
import pytest
from click.testing import CliRunner
from tdfw import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def temp_app(tmp_path):
    """Create a temporary app directory for testing."""
    app_dir = tmp_path / "MyTestApp"
    yield app_dir
    if app_dir.exists():
        shutil.rmtree(app_dir)

def test_start_app_creates_structure(runner, temp_app):
    result = runner.invoke(cli.start_app, [str(temp_app)])
    assert result.exit_code == 0
    assert (temp_app / "BAT").exists()
    assert (temp_app / "DAT").exists()
    assert (temp_app / "LOG").exists()
    assert (temp_app / "README.md").exists()
    assert (temp_app / ".gitignore").exists()
    assert (temp_app / "BAT" / "MyTestApp.bat").exists()
    for ext in ["StartupExt.py", "SettingsExt.py", "StateExt.py"]:
        assert (temp_app / "DAT" / ext).exists()

def test_start_app_echo_message(runner, temp_app):
    result = runner.invoke(cli.start_app, [str(temp_app)])
    assert "✅ Created TouchDesigner app scaffold" in result.output

def test_create_ext_adds_file(runner, temp_app):
    # First scaffold the app
    runner.invoke(cli.start_app, [str(temp_app)])
    cwd = os.getcwd()
    os.chdir(temp_app)
    result = runner.invoke(cli.create_ext, ["CameraExt"])
    os.chdir(cwd) 
    assert result.exit_code == 0
    ext_file = temp_app / "DAT" / "CameraExt.py"
    assert ext_file.exists()
    content = ext_file.read_text()
    assert "class CameraExt" in content

def test_create_ext_without_dat(runner, tmp_path):
    os.chdir(tmp_path)
    result = runner.invoke(cli.create_ext, ["FooExt"])
    assert result.exit_code == 0
    assert "❌ No DAT directory found" in result.output
