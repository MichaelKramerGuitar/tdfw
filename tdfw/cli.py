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
start "{td_exec}" "{app_name}.toe"
{ide} .
""")

    # Mac/Linux .bash
    bash_path = os.path.join(base, "BAT", f"{os.path.basename(app_name)}.bash")
    with open(bash_path, "w") as f:
        f.write(f"""#!/bin/bash
export NODE=DEV
cd ..
open -a "{td_exec}" "{app_name}.toe"
{ide} .
""")

    # Stub LoggerExt
    with open(os.path.join(base, "DAT", "LoggerExt.py"), "w") as f:
        f.write("""from TDStoreTools import StorageManager
import TDFunctions as TDF

import datetime
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
        f.write("""from TDStoreTools import StorageManager
import TDFunctions as TDF


settings = {
    # example settings - make these your own
    # these are settings you can use to configure your project for different nodes or environments
    'DEV': {
        'asset_path': '<path_to_assets>',
        'record_path': '<path_to_recordings>',
    },
    'PROD': {
        'asset_path': '<path_to_assets>',
        'record_path': '<path_to_recordings>',
    },
}

class SettingsExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.nodeSettings = op('node_settings')

    def ConfigSettings(self):
        op.LOG.Log("SettingsExt.ConfigSettings()")
        node = var('NODE') or 'DEV'  
        op.LOG.Log(f"SettingsExt.ConfigSettings(): Running as node {node}")
        print(f"SettingsExt.ConfigSettings(): Running as node {node}")
        self.AssetPath = settings.get(node, {}).get('asset_path', '')
        # from here you can reference the settings in your project like this:
        #  f"{op.SETTINGS.AssetPath}/<my-asset>.<file-type>"
        #  and you should ensure any file you bring into TD is referenced
        #  relatively as shown above so that you can switch between nodes
        #  or environments easily (i.e. separate code and assets for PORTABILITY)
        self.RecordingPath = settings.get(node, {}).get('record_path', '')
        op.LOG.Log(f"SettingsExt.ConfigSettings(): Asset Path: {self.AssetPath}")
        op.LOG.Log(f"SettingsExt.ConfigSettings(): Recording Path: {self.RecordingPath}")
        op.LOG.Log(f"SettingsExt.ConfigSettings(): Node: {node}")
""")

    # Stub StartupExt
    with open(os.path.join(base, "DAT", "StartupExt.py"), "w") as f:
        f.write("""from TDStoreTools import StorageManager
import TDFunctions as TDF
import os
import sys


class StartupExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp

    def AddDependenciesToPath(self):
        dep_path = f'{project.folder}/DEP/PYTHON/'
        norm_dep_path = os.path.normpath(dep_path)
        op.LOG.Log(f"StartupExt.AddDependenciesToPath(): Adding {norm_dep_path} to sys.path")
        if norm_dep_path not in sys.path:
            sys.path.insert(0, norm_dep_path)
            op.LOG.Log(f"StartupExt.AddDependenciesToPath(): Added {norm_dep_path} to sys.path")

    def Startup(self):
        self.AddDependenciesToPath()
        op.LOG.Log('StartupExt.Startup()')
        op.SETTINGS.ConfigSettings()
""")

    # Stub AppExt
    with open(os.path.join(base, "DAT", "AppExt.py"), "w") as f:
        f.write("""\"""
Application extension for handling application states.

This Extension is "Driving the Application"
\"""

from TDStoreTools import StorageManager
import TDFunctions as TDF


class AppExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        # Valid examples YOU SHOULD OVERWRITE with your own states
        # or use an Enum or consider pytransitions https://github.com/pytransitions/transitions
        self.validStates = ['not_playing', 'is_playing']
        self.State = 'not_playing'

    def SetState(self, state: str):  # you may need to change the type hint depending on your state representation (e.g., Enum)
        \"""
        Set the application state to the given state if it is valid.

        This method is the main entry point for changing the application state. It checks if the provided state is valid and updates the current state accordingly. If the state is invalid, it raises a ValueError.
        \"""
        if state in self.validStates:
            self.State = state
            self._handleStateChange()
            op.LOG.Log(f"AppExt.SetState(): {state}")
        else:
            op.LOG.Log(f"AppExt.SetState(): invalid state: {state}")
            raise ValueError(f"Invalid state: {state}")

    def _handleStateChange(self):
        \"""
        This is where you should be able to read everything that happens
        in your application like a Table of Contents. 

        Avoid using dependable members (i.e. run()) in this method or methods called from here
        as much as possible to truly be able to read the state
        of your application from the top down - keeping every
        state change and all logic EXPLICIT and LEGIBLE. 

        delayed executions represent a "hidden" state change
        and should be avoided whenever possible. If you must use them,
        be sure to document them well and consider using a state machine
        library like pytransitions to manage your states more explicitly.
        \"""
        match self.State:
            case 'is_playing':
                op.LOG.Log("AppExt._handleStateChange(): is_playing")
                # Add your logic for when the state is 'is_playing'
            case 'not_playing':
                op.LOG.Log("AppExt._handleStateChange(): not_playing")
                # Add your logic for when the state is 'not_playing'

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

Open TouchDesigner > 

File > Create Project Folder 

In dialog: 
  - Path: 
    > Use the file system nav to select ONE LEVEL BACK FROM THE ROOT 
        of Project you just created 
  - Project Folder:
    > name it EXACTLY this: {os.path.basename(app_name)}
   
  - Rename File: 
    > ENSURE CHECKED

  - Media Folders: 
    > Select/Unselect whatever Media Folders you want to create


The scaffold already includes DAT/STARTUP/StartupExecute.py with:

```python
def onStart():
    op.STARTUP.Startup()
```
So once you save the .toe, the startup hook is ready to bridge into StartupExt.py.

> Now hook the rest of the boilerplate into TouchDesigner (once project is open in TD)

    - Delete the TouchDesigner built in boilerplate

    - Right Click > Add Operator > COMP > Base and re-name for each in [STARTUP, SETTINGS, LOG, APP]

    - Then for each <NAME> in [STARTUP, SETTINGS, LOG, APP]
        - Ensure the Base > Common "Parent Shortcut" and "Global OP Shortcut" are set to <NAME> (i.e. STARTUP, SETTINGS, LOG, APP)
        - Right click on <NAME>
        - > Customize Component
        - > Expand "Extensions"
        - give <Name>Ext as the Extension Class Name (for LOG use LoggerExt)
        - click "into" <NAME> (shortcut "i")
        - use the Text DAT's File Tab to choose the DAT/<Name>Ext.py file 
        - ensure "Sync to File" is selected

    - Right Click > Add Operator > DAT > Execute 
        - within this DAT (shortcut "i") attatch the STARTUP/StartupExecute.py script

> Now you can open up a TextPort in TouchDesigner and test everything is working by running:
```python
python >>> op.STARTUP.Startup()

# expected output in TextPort:
SettingsExt.ConfigSettings(): Running as node DEV

python >>> op.APP.SetState('is_playing')
# check LOG directory for timestamped log entries
```
**...and when you're all set up get rid of these notes and make this README.md your own!**
""")
    click.echo(f"""
    ============================================================
    🎶 TouchDesigner App Scaffold Created 🎶
    ============================================================

    ✅ Location: {base}

    ➡ Next Steps:
    1. 
        Open TouchDesigner > 

        File > Create Project Folder 

        In dialog: 
        - Path: 
            > Use the file system nav to select one level back from {base}
                (so just take the /{os.path.basename(app_name)} away 
                and select that parent folder)
        - Project Folder:
            > name it EXACTLY this: {os.path.basename(app_name)}
        
        - Rename File: 
            > ENSURE CHECKED

        - Media Folders: 
            > Select/Unselect whatever Media Folders you want to create
    2. Save and close TouchDesigner then in you File Explorer or Finder,
       navigate to the {os.path.basename(app_name)} directory
    3. Find then Double-click your launcher:
            • BAT/{os.path.basename(app_name)}.bat   (Windows)
            • BAT/{os.path.basename(app_name)}.bash  (Mac/Linux)
        → This sets NODE=DEV, opens your IDE ({ide}), 
            and launches TouchDesigner with your project.

            - Delete the TouchDesigner built in boilerplate

            - Right Click > Add Operator > COMP > Base and re-name for each in [STARTUP, SETTINGS, LOG, APP]

            - Then for each <NAME> in [STARTUP, SETTINGS, LOG, APP]
                - Right click on <NAME>
                - > Customize Component
                - > Expand "Extensions"
                - give <Name>Ext as the Extension Class Name
                - click "into" <NAME> (shortcut "i")
                - use the Text DAT's File Tab to choose the DAT/<Name>Ext.py file 
                - ensure "Sync to File" is selected

            - Right Click > Add Operator > DAT > Execute 
                - within this DAT (shortcut "i") attatch the STARTUP/StartupExecute.py script

    4. Extend your app from your project root:
            • Create new extensions with:
            tdfw create-ext <MyExt>
            • Implement your logic in DAT/MyExt.py and repeat these steps to attach it to a Base COMP in TouchDesigner.
                - Right Click > Add Operator > COMP > Base
                - Right click on <NAME>
                - > Customize Component
                - > Expand "Extensions"
                - give <Name>Ext as the Extension Class Name
                - click "into" <NAME> (shortcut "i")
                - use the Text DAT's File Tab to choose the DAT/<Name>Ext.py file 
                - ensure "Sync to File" is selected

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