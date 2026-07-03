import os
import click
import subprocess
import shutil

def check_tool(tool_name):
    """Return True if tool is available in PATH"""
    return shutil.which(tool_name) is not None

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

@click.group()
def cli():
    """TouchDesigner Framework CLI (tdfw)"""
    pass

# ----------------------------
# App scaffolding
# ----------------------------
@click.command()
@click.argument("app_name")
@click.option("--td-path", default=None,
              help="Override path to TouchDesigner executable")
@click.option("--ide", default="code",
              help="IDE to open (default: code, can override with cursor)")
def start_app(app_name, td_path, ide):
    """Scaffold a new TouchDesigner app"""
    base = os.path.abspath(app_name)
    ensure_dir(base)

    for folder in ["BAT", "DAT", "LOG"]:
        ensure_dir(os.path.join(base, folder))

    # Default TD path
    default_td_path = "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
    td_exec = td_path if td_path else default_td_path

    # Windows .bat
    bat_path = os.path.join(base, "BAT", f"{os.path.basename(app_name)}.bat")
    with open(bat_path, "w") as f:
        f.write(f"""@echo off
set NODE=DEV
cd ..
{ide} .
start "" "{td_exec}" "{app_name}.toe"
""")

    # Mac/Linux .bash
    bash_path = os.path.join(base, "BAT", f"{os.path.basename(app_name)}.bash")
    with open(bash_path, "w") as f:
        f.write(f"""#!/bin/bash
export NODE=DEV
cd ..
{ide} .
open -a "{td_exec}" "{app_name}.toe"
""")

    # Stub LoggerExt
    with open(os.path.join(base, "DAT", "LoggerExt.py"), "w") as f:
        f.write("""import datetime
import os

class LoggerExt:
    \"""
    LoggerExt writes timestamped messages to a per-run log file
    in the LOG/ directory. Each run gets its own file named
    app_<YYYYMMDD-HHMMSS>.log.
    \"""

    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        os.makedirs("LOG", exist_ok=True)
        run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.log_file = os.path.join("LOG", f"app_{run_id}.log")

    def Log(self, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        with open(self.log_file, "a", encoding="utf-8") as log_file:
            log_file.write(entry + "\\n")
""")

    # Stub SettingsExt
    with open(os.path.join(base, "DAT", "SettingsExt.py"), "w") as f:
        f.write("""class SettingsExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.nodeSettings = op('node_settings')

    def ConfigSettings(self):
        op.LOG.Log("SettingsExt.ConfigSettings()")
        node = var('NODE') or 'HWP_MAC'
        print(f"Settings: Running as node {node}")
        self.AssetPath = self.nodeSettings[node, 'asset_path'].val
        self.RecordingPath = self.nodeSettings[node, 'record_path'].val
""")

    # Stub StartupExt
    with open(os.path.join(base, "DAT", "StartupExt.py"), "w") as f:
        f.write("""class StartupExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp

    def AddDependenciesToPath(self):
        dep_path = f'{project.folder}/DEP/PYTHON/'
        norm_dep_path = os.path.normpath(dep_path)
        if norm_dep_path not in sys.path:
            sys.path.insert(0, norm_dep_path)

    def Startup(self):
        self.AddDependenciesToPath()
        op.LOG.Log('StartupExt.Startup()')
        op.SETTINGS.ConfigSettings()
""")

    # Stub StateExt
    with open(os.path.join(base, "DAT", "StateExt.py"), "w") as f:
        f.write("""class StateExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        # Valid examples YOU SHOULD OVERWRITE with your own states
        # or use an Enum or consider pytransitions https://github.com/pytransitions/transitions
        self.validStates = ['not_playing', 'is_playing']
        self.State = 'not_playing'

    def SetState(self, state: str):
        if state in self.validStates:
            self.State = state
            self.handleStateChange()
            op.LOG.Log(f"StateExt.SetState(): {state}")
        else:
            op.LOG.Log(f"StateExt.SetState(): invalid state: {state}")
            raise ValueError(f"Invalid state: {state}")

    def handleStateChange(self):
        match self.State:
            case 'is_playing':
                op.COMP.SetCaptureMode(True)
            case 'not_playing':
                op.COMP.SetCaptureMode(False)
""")

    # Stub StartupExecute (bridge to StartupExt)
    startup_dir = os.path.join(base, "DAT", "STARTUP")
    ensure_dir(startup_dir)
    with open(os.path.join(startup_dir, "StartupExecute.py"), "w") as f:
        f.write("""def onStart():
    # This Execute DAT stub bridges TouchDesigner startup to StartupExt
    op.STARTUP.Startup()
""")

    # Create README.md and .gitignore
    with open(os.path.join(base, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("""# Ignore TouchDesigner temp files and artifacts
*.toe
*.log
Backup/
LOG/
""")

    with open(os.path.join(base, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# {os.path.basename(app_name)}
Generated by tdfw

## How To Use

```bash
# 1. Install prerequisites
# Make sure Python is installed (matching TouchDesigner’s version) and a package manager like uv is available globally.

# 2. Install tdfw globally
uv pip install --upgrade tdfw

# 3. Confirm installation and explore options
tdfw help

# 4. Doctor check (optional but recommended)
tdfw doctor

# 5. Scaffold a new TouchDesigner App
tdfw start-app {os.path.basename(app_name)}

# 6. Open your app in your editor
cd {os.path.basename(app_name)}
code .   # or cursor ., vim ., etc.

# 7. Create Python Extension stubs
# Run from your TouchDesigner Project Root (the dir with {os.path.basename(app_name)}.toe)
tdfw create-ext <MyFirstExt>

# 8. Manage environments
tdfw init-env <MyAppEnv>
tdfw export-env --manager uv --output requirements.txt
tdfw import-env requirements.txt

# Next Steps

Open TouchDesigner and save a new project as {os.path.basename(app_name)}.toe in this directory.

The scaffold already includes DAT/STARTUP/StartupExecute.py with:

```python
def onStart():
    op.STARTUP.Startup()
```
So once you save the .toe, the startup hook is ready to bridge into StartupExt.py.
""")
    click.echo(f"""
    ============================================================
    🎶 TouchDesigner App Scaffold Created 🎶
    ============================================================

    ✅ Location: {base}

    ➡ Next Steps:
    1. Open TouchDesigner
    2. Save your project as: {os.path.basename(app_name)}.toe
    3. Double-click your launcher:
            • BAT/{os.path.basename(app_name)}.bat   (Windows)
            • BAT/{os.path.basename(app_name)}.bash  (Mac/Linux)
        → This sets NODE=DEV, opens your IDE ({ide}), 
            and launches TouchDesigner with your project.

    4. Extend your app from your project root:
            • Create new extensions with:
            tdfw create-ext <MyExt>
            • Implement your logic in DAT/MyExt.py

    ------------------------------------------------------------
    🎶  Happy coding — may your states be explicit, 
        your logs timestamped, and your kinetic renders elegant! 🎶
    ------------------------------------------------------------
    """)


# ----------------------------
# Extension stub
# ----------------------------
@click.command()
@click.argument("ext_name")
def create_ext(ext_name):
    """Create a new extension stub"""
    path = os.path.join("DAT", f"{ext_name}.py")
    if not os.path.exists("DAT"):
        click.echo("❌ No DAT directory found. Run start-app first.")
        return

    with open(path, "w") as f:
        f.write(f"""class {ext_name}:
    \"\"\"{ext_name} description\"\"\"
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
""")
    click.echo(f"✅ Created extension stub: {path}")

# ----------------------------
# Environment management
# ----------------------------
@click.command()
@click.argument("env_name")
def init_env(env_name):
    """Initialize a Python virtual environment using uv (fallback to pip)"""
    if check_tool("uv"):
        click.echo(f"📦 Creating uv environment: {env_name}")
        subprocess.run(["uv", "venv", env_name], check=True)
        click.echo("✅ uv environment created")
    elif check_tool("python"):
        click.echo("⚠️ uv not found, falling back to Python venv + pip")
        subprocess.run(["python", "-m", "venv", env_name], check=True)
        subprocess.run([f"{env_name}/Scripts/pip", "install", "--upgrade", "pip"], check=True)
        click.echo("✅ Python venv created and pip upgraded")
    else:
        click.echo("❌ Neither uv nor Python found. Please install one of them.")

@click.command()
@click.argument("env_name")
def init_conda(env_name):
    """Initialize a Conda environment"""
    if not check_tool("conda"):
        click.echo("❌ Conda is not installed. Please install Conda first.")
        return
    click.echo(f"📦 Creating Conda environment: {env_name}")
    subprocess.run(["conda", "create", "-y", "-n", env_name, "python=3.12"], check=True)
    click.echo("✅ Conda environment created")

@click.command()
def sync_env():
    """Export requirements for reproducibility"""
    click.echo("📤 Exporting requirements.txt")
    subprocess.run(["uv", "pip", "freeze", ">", "requirements.txt"], shell=True)
    click.echo("✅ requirements.txt exported")

@click.command()
@click.argument("env_file")
def import_env(env_file):
    """Import environment from requirements.txt or environment.yml"""
    if env_file.endswith(".yml"):
        click.echo(f"📥 Importing Conda environment from {env_file}")
        subprocess.run(["conda", "env", "create", "-f", env_file], check=True)
    else:
        click.echo(f"📥 Importing uv environment from {env_file}")
        subprocess.run(["uv", "pip", "install", "-r", env_file], check=True)
    click.echo("✅ Environment imported")


@click.command()
@click.option("--manager", type=click.Choice(["uv", "pip", "conda"]), default="uv",
              help="Environment manager to export from")
@click.option("--output", default="requirements.txt",
              help="Output file (requirements.txt or environment.yml)")
def export_env(manager, output):
    """Export environment for reproducibility (uv, pip, or conda)"""
    if manager == "uv":
        if not check_tool("uv"):
            click.echo("❌ uv not installed")
            return
        click.echo(f"📤 Exporting uv environment to {output}")
        subprocess.run(["uv", "pip", "freeze"], stdout=open(output, "w"), check=True)
        click.echo(f"✅ uv environment exported to {output}")

    elif manager == "pip":
        if not check_tool("pip"):
            click.echo("❌ pip not installed")
            return
        click.echo(f"📤 Exporting pip environment to {output}")
        subprocess.run(["pip", "freeze"], stdout=open(output, "w"), check=True)
        click.echo(f"✅ pip environment exported to {output}")

    elif manager == "conda":
        if not check_tool("conda"):
            click.echo("❌ conda not installed")
            return
        click.echo(f"📤 Exporting conda environment to {output}")
        subprocess.run(["conda", "env", "export"], stdout=open(output, "w"), check=True)
        click.echo(f"✅ conda environment exported to {output}")


@click.command()
def help():
    """Show comprehensive help for tdfw"""
    click.echo("""
TouchDesigner Framework CLI (tdfw)

Available commands:

  doctor                  Check system readiness for tdfw

  start-app <name>        Scaffold a new TouchDesigner app
    --td-path             Override TouchDesigner executable path
    --ide <ide>           IDE to open (default: code, can override with cursor)

  create-ext <name>       Create a new extension stub

  init-env <name>         Create a uv-managed Python environment
                          Falls back to Python venv if uv is not available

  init-conda <name>       Create a Conda environment

  sync-env                Export requirements.txt from current uv environment

  import-env <file>       Import environment from requirements.txt or environment.yml

  export-env              Export environment snapshot
    --manager [uv|pip|conda]   Choose environment manager (default: uv)
    --output <file>            Output file (requirements.txt or environment.yml)
""")

@click.command()
@click.option("--td-path", default=None,
              help="Override path to TouchDesigner executable")
def doctor(td_path):
    """Check system readiness for tdfw"""
    click.echo("🔎 Running tdfw system check...\n")

    # uv
    if check_tool("uv"):
        click.echo("✅ uv found")
    else:
        click.echo("⚠️ uv not found (tdfw will fall back to pip)")

    # pip
    if check_tool("pip"):
        click.echo("✅ pip found")
    else:
        click.echo("❌ pip not found — install Python with pip")

    # conda
    if check_tool("conda"):
        click.echo("✅ conda found")
    else:
        click.echo("⚠️ conda not found (optional, only needed if you want Conda envs)")

    # TouchDesigner executable
    default_td_path = "C:\\Program Files\\Derivative\\TouchDesigner\\bin\\TouchDesigner.exe"
    td_exec = td_path if td_path else default_td_path
    if os.path.exists(td_exec):
        click.echo(f"✅ TouchDesigner executable found at {td_exec}")
    else:
        click.echo(f"⚠️ TouchDesigner executable not found at {td_exec}. Use --td-path to override.")

    click.echo("\n🩺 System check complete.")

# ----------------------------
# Register commands
# ----------------------------
cli.add_command(help)
cli.add_command(doctor)
cli.add_command(start_app)
cli.add_command(create_ext)
cli.add_command(init_env)
cli.add_command(init_conda)
cli.add_command(sync_env)
cli.add_command(import_env)
cli.add_command(export_env)