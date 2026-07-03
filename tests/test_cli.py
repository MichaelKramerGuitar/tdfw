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
    assert (temp_app / "BAT" / "MyTestApp.bash").exists()
    for ext in ["StartupExt.py", "SettingsExt.py", "StateExt.py"]:
        assert (temp_app / "DAT" / ext).exists()

def test_start_app_echo_message(runner, temp_app):
    result = runner.invoke(cli.start_app, [str(temp_app)])
    assert "Scaffold Created" in result.output

def test_create_ext_adds_file(runner, temp_app):
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

# ----------------------------
# New command tests
# ----------------------------

def test_help_command(runner):
    result = runner.invoke(cli.help)
    assert result.exit_code == 0
    assert "TouchDesigner Framework CLI" in result.output
    assert "start-app" in result.output
    assert "init-env" in result.output

def test_doctor_command_defaults(runner, tmp_path):
    # Run doctor with no override
    result = runner.invoke(cli.doctor)
    assert result.exit_code == 0
    assert "System check complete" in result.output

def test_init_env_fallback(runner, tmp_path, monkeypatch):
    # Patch inside cli module
    monkeypatch.setattr(cli, "check_tool", lambda tool: tool == "python")
    env_dir = tmp_path / "venvtest"
    result = runner.invoke(cli.init_env, [str(env_dir)])
    assert "falling back to Python venv" in result.output

def test_init_conda_missing(runner, monkeypatch):
    # Patch inside cli module
    monkeypatch.setattr(cli, "check_tool", lambda tool: False)
    result = runner.invoke(cli.init_conda, ["myenv"])
    assert "❌ Conda is not installed" in result.output

def test_init_env_no_tools(runner, monkeypatch):
    # Simulate neither uv nor python available
    monkeypatch.setattr(cli, "check_tool", lambda tool: False)
    result = runner.invoke(cli.init_env, ["envX"])
    assert "❌ Neither uv nor Python found" in result.output

def test_sync_env_runs(runner, monkeypatch):
    # Patch subprocess.run to avoid actually running uv
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    result = runner.invoke(cli.sync_env)
    assert result.exit_code == 0
    assert "requirements.txt exported" in result.output

def test_import_env_yml(runner, tmp_path, monkeypatch):
    env_file = tmp_path / "env.yml"
    env_file.write_text("name: testenv")
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    result = runner.invoke(cli.import_env, [str(env_file)])
    assert "Importing Conda environment" in result.output

def test_import_env_txt(runner, tmp_path, monkeypatch):
    env_file = tmp_path / "requirements.txt"
    env_file.write_text("click")
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    result = runner.invoke(cli.import_env, [str(env_file)])
    assert "Importing uv environment" in result.output

def test_doctor_missing_td_path(runner, tmp_path):
    # Point doctor to a non-existent path
    fake_path = tmp_path / "TouchDesigner.exe"
    result = runner.invoke(cli.doctor, ["--td-path", str(fake_path)])
    assert "TouchDesigner executable not found" in result.output

def test_export_env_uv(runner, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "check_tool", lambda tool: tool == "uv")
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    output_file = tmp_path / "req.txt"
    result = runner.invoke(cli.export_env, ["--manager", "uv", "--output", str(output_file)])
    assert result.exit_code == 0
    assert "uv environment exported" in result.output

def test_export_env_pip(runner, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "check_tool", lambda tool: tool == "pip")
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    output_file = tmp_path / "req.txt"
    result = runner.invoke(cli.export_env, ["--manager", "pip", "--output", str(output_file)])
    assert result.exit_code == 0
    assert "pip environment exported" in result.output

def test_export_env_conda(runner, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "check_tool", lambda tool: tool == "conda")
    monkeypatch.setattr(cli.subprocess, "run", lambda *a, **k: None)
    output_file = tmp_path / "env.yml"
    result = runner.invoke(cli.export_env, ["--manager", "conda", "--output", str(output_file)])
    assert result.exit_code == 0
    assert "conda environment exported" in result.output

def test_export_env_missing_tool(runner, monkeypatch):
    # Simulate no tool installed
    monkeypatch.setattr(cli, "check_tool", lambda tool: False)
    result = runner.invoke(cli.export_env, ["--manager", "uv"])
    assert "❌ uv not installed" in result.output
