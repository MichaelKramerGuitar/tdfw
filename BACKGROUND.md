# Touch Designer State Machine Architecture

MAIN Resource: https://www.youtube.com/watch?v=nQT7EhYCVg0

## AI Summary

In this video, Noah from ThirdWave Arcade outlines his approach to building complex, maintainable applications in TouchDesigner as of 2025. He advocates for moving away from "spaghetti" node networks in favor of a structured, Python-extension-driven architecture (1:16, 3:35).

Key Architectural Principles:

State Machines: The core of his applications is a central state object that dictates the flow of the program, acting as a single source of truth (3:00, 11:17).
Extension-Driven Development: He uses Python extensions to keep logic legible and diffable, allowing him to work primarily in an IDE (e.g., Cursor) rather than the node interface (3:36, 5:35).
Explicit Logic: He emphasizes that the application should read like a table of contents, avoiding implicit dependencies and the use of the run method for delayed execution (12:20, 16:04).
Project Structure: Standardizing folder layouts (bat, dat, log), using environment variables to distinguish between developer and production machines, and utilizing global operator shortcuts for modularity (4:00, 7:00).
Practical Application (The Photo Booth Example):

The video walks through building a photo booth app, demonstrating how the state base governs components like capture, playback, and UI without those components needing to know about each other (1:36, 20:48).
He shows how to drive transitions explicitly (18:59) and introduces the concept of using PyTransitions for more granular, robust state machine control (29:15, 30:15).
Conclusion:

The focus is on legibility, maintainability, and collaboration over raw, early-stage optimization. By treating the code as a contract between modules, developers can create complex, professional-grade systems that are easy to debug and extend (16:36, 24:59).

## From the description

In this video I show you:
STATE MACHINES: how to use Finite State Machines to control application flow and act as a single source of truth, with explicit, declarative, legible code
EXTENSION-DRIVEN DEVELOPMENT: how to use Python extensions and minimal nodes to keep code legible, maintainable, and diffable (great for collaboration)
PROJECT STRUCTURE: how to structure the root level of the app and your file system in a way that any old dummy would understand in 5 minutes
STARTUP FLOW: centralize app boostrapping in one logical place
GLOBAL OP SHORTCUTS: this one weird trick to make code infinitely more modular, legible, and portable doctors hate!
ENVIRONMENT VARIABLES: use launch scripts and env settings to feature-flag one app to work on many systems
BONUS: a little bit about Pytransitions for fully-featured state machine shenanigans

## My Notes

Example he gives: 

Client Request: Photo booth
Requirements:
- Record a brief video
- Play it back
- Call to action: Go to website to purchase or buy video they just made

How he organizes EVERY Touch Designer App he builds:

- Everything is a BAS except nodes that need a display are CTN (containers)
- Everything that "needs to be told what to do" has an extension (python code) 
- Top level of the application can be looked at as a table of contents
- Everything internal is ignorant of the state of the application except for the BAS
- State:
	- where the application gets told what to do 
	- where the application drives itself forward
	- doesn't itself communicate or write to db's or to disk
		- that happens in specialized components (BAS's) that are told what to do VIA state and their python extensions
	- Python usage FOR EVERYTHING THAT DRIVES BUSINESS LOGIC FORWARD
		- Think: Human readability IN AN IDE
- Use OPS VERY SPARINGLY

Application DIR structure

```bash
.git
Backup
BAT
|- A <app-name>.bat file (see .bat example below)
DAT
|- Where python extensions live
|- Also where SETTINGS Dir lives
LOG
|- log text file outputs from Log component (for debugging)
.gitignore
README.md
<app-name>.toe
```


# .bat file example

```bat
@echo off

# set an env var called NODE that allows us to make distinctions between machines we're running this app from (development machine vs. prod machine, for example)
set NODE=HWP
cd ..
# start your IDE (I use VSCode but he uses cursor here)
start cursor .
# for me that above line would be `code .`
start "" "PATH TO EXACT TOUCH DESIGNER EXECUTABLE VERSION ON DISK" "<app-name>.toe"
```

The purpose of this file is TO RUN THE TOUCH DESIGNER APPLICATION BY DOUBLE CLICKING the .bat file in that directory

This set up allows us to basically write python code in an IDE (like normal software developers like myself do) instead of creating nodes in the Touch Designer GUI

- It's maintainable, legible (for a human AND LLM), version controlled, and easy to iterate and collaborate on. 
- It has all the benefits of modern software development best practices
- It allows us to be declarative and explicit treating our Extensions as tables of contents for "what our app does"

# First thing that happens in this Design Pattern

One execute DAT set up like this:

```python
def onStart():
    
    op.STARTUP.Startup()
```

so this is calling into an Extension that has a class something like this:

# imports go here

```python
class StartupExt:
    """
        Startup description
    """

    def __init__(self, ownerComp):
        # the component to which this extension is attached
        self.ownerComp = ownerComp

    def AddDependenciesToPath(self):
	dep_path = f'{project.folder}/DEP/PYTHON/'
	norm_dep_path - os.path.normpath(dep_path)
	if norm_dep_path not in sys.path:
		sys.path.insert(0, norm_dep)path)

    def Startup(self):
	self.AddDependenciesToPath()
	op.LOG.Log('StartupExt.Startup()')
	op.SETTINGS.ConfigSettings()
```

These are all using the Global Operator shortcut on the op level

so saying something like op.SETTINGS.<whatever-attribute-or-method> is a way for me ANYWHERE in my application to access anything in my SettingsExt class which might look SOMETHING like this (his example)

```python
class SettingsExt:
    """
	SettingsExt description
    """

    def __init__(self, ownerComp) -> None:
        # the component to which this extension is attached
        self.ownerComp = ownerComp
	self.nodeSettings = op('node_settings')
	
	# What's TDF? he doesn't explain and it's not shown what this import is or how it's defined
	TDF.createProperty(self, 'AssetPath', value=""...)
	TFF.createProperty(self, 'RecordingPath....)


    def ConfigSettings(self):
	op.LOG.Log('SettingsExt.ConfigSettings()')
	print('Settings: Running Config')
	node = var('NODE')  # this was set in the .bat file, remember?
	if node == '':
		node = 'HWP_MAC'  # This is an assumption he makes when working from a Mac because he doesn't take the time to set up an .bash similar to .bat
	print(f'Settings: Running as node {node}')
	
	# these are configurable values that obviously can be configured depending on what NODE equals (i.e. local dev vs. prod server)
	self.AssetPath = self.nodeSettings[node, 'asset_path'].val
	print("Settings: AssetPath {self.AssetPath}")
	
	# so from here project to project, for loading a particular asset in the Touch Designer GUI he'll 
	# open his local ASSETS folder and drag his asset (like an .mp3 or whatever) into the GUI
	# Then in the dialog on the node he says f'op.SETTINGS.AssetPath/<myasset>.mp3' > best practice for this configuration pattern per varying NODE values (prod vs local for example)

	self.RecordingPath = self.nodeSettings[node, 'record_path'].val
	print("Settings: RecordingPath {self.RecordingPath}")
	
	# here you can configure as many useful settings like resolutionX and resolutionY which might have differing vals for prod vs. local (think for renders or output) > need to create respective properties for these in this class to store these vals but this is how you'd get access to these anywhere in your app
	
	# Especially useful for Portability of Code (probably MBs) SEPARATE from Assets (probably GBs) -> decouple these!
```

So the STATE object is "driving the show" - this is the whole point DON'T USE the Timer CHOP for STATE! Use a StateExt class!

Here's his first example state extension:

```python
class StateExt:
    """
	StateExt description
    """

    def __init__(self, ownerComp) -> None:
        # the component to which this extension is attached
        self.ownerComp = ownerComp
	self.validStates = [a, list, of, valid, states]  # this was a really simple explicit example - he uses a more complex one later - could use ENUM or custom type like a DataClass too
	self.State = 'one of the validStates list elements'  # set public attribute to some valid state on init


    def SetState(self, state: str) -> None:
	"""
	    THIS IS THE MOST IMPORTANT METHOD OF THE WHOLE DEMO
	"""
	if state in self.validStates: # here's where you're gating and ONLY allowing the app to be in a state you've defined
	    self.State = state
            self.hanleStateChange()
	else: # don't let the app progress
	    op.LOG.Log(f'StateExt.SetState(): invalid state: {state}')
	    raise ValueError(f'Invalid state: {state}') 
        op.LOG.Log(f'StateExt.SetState(): {state}')

    def handleStateChange(self) -> None: 
	match self.State: 
	   case 'some valid state': 
		op.COMP.SetLEDSource('some valid state')
		op.COMP.setFoldbackSource('cam')
		op.COMP.SetCaptureMode(False)
		op.TEXT.SetCountdownVisible(False)
	   # explicitly handle like a table of contents ALL possible states and don't be afraid of explicitly repeating yourself here - it's about readability here
```


> So this is really solid OOP, contract driven, API-like development, it's really beautiful 

When going from Python > Touch Designer > Python he follows PEP mantra EXPLICIT IS BETTER THAN IMPLICIT

Huge focus on Readability of his applications like this - top level Table of Contents style -> EXPLICIT -> DECLARATIVE (as few as possible IMPLICIT business logic code)

Avoid delayed executions at all cost > This obscures STATE from the places you go to do your reading and debugging of code, your application understanding 

His top 3 most important things in Touch Designer Python code:
1. Legibility
2. Legibility
3. Legibility

THEN you can think about performance etc. > Selective optimization for performance can almost always come LATER 

# Dependable PROPERTIES drive business logic inside the application

He does this by going into nodes in the Touch Designer UI > Cross Fades normally in some kind of SWITCH

^^^ This statement I don't quite understand 

But He explains he does this as a linkage between the Operator Network and his Python Extensions But he considers this to still be EXPLICIT > he also says this might be a misuse of a constant CHOP, better would be to use a Script CHOP (more explicit)

# State pattern: Maestro, Conductor, Command and Control Pattern, Table of Contents > All you need to know in order to know how the app works


then he runs the app in his example from the command line like this (he would ordinarily lay this out in a Window COMP but he didn't know the customers Window arrangement was)

```bash
>>> op.STATE.SetState('first valid state')
>>> op.STATE.SetState('next valid state where there's the flow of the app...etc')
```

> He says violating DRY (Don't Repeat Yourself) is actually DESIREABLE HERE for "EXPLICIT-NESS"

COUPLING is bad for business logic > each STATE implementation shouldn't have to know about any other STATE > No Side Effects > Surface properties to the Business Logic (Controller, Maestro, Conductor, Table of Contents) level > Implementation SHOULD BE ABLE TO CHANGE without the Command and Control/Top Level Table of Contents CHANGING AT ALL!


So in this way you could STUB out the WHOLE PROGRAM at the Table of Contents/Command and Control Top Layer WITHOUT CARING HOW IT'S IMPLEMENTED!

# TODO: Understand HOW to go from IDEA to STUBBING OUT A PROGRAM for ANY IDEA!

Once STUBBED with prints() you can DEBUG the application flow/business logic of the program by nudging state ensuring the things that you expect to happen occur in the proper order

From there you can FOCUS ON THE ACTUAL MECHANICS with the knowledge that the app is DONE all you need to do is "assemble" 

AND FROM THERE you can focus on UI > Driving the application from a GUI or keyboard input or whatever! This could be ANOTHER EXTENSION like class KeyExt: that handles which keys nudge which states etc. 

Externalize ALL CODE immediately (use case: you create a Key In DAT listener node from the Touch Designer GUI > Save it to file immediate and customize it immediately) that way there's only ever ONE VERSION of the code

# Pytransitions

Towards the end of the Video he talks about using Pytransitions library for full featured batteries included STATE MACHINE "stuff" 

Gives GRANULAR control over how you
-set up for
-execute
-clean up from
Transitions in state

All about sequencing! Which can be REALLY important in complex applications

# My First Example App using this Pattern

- I want to be able to listen to audio input from my Kemper Profiler through my Focusrite Audio interface
- States could be REALLY SIMPLE at first like: 'is_playing', 'not_playing' but could progress to more complex states like 'is_playing_loud', 'is_playing_soft', 'is_playing_chords', 'is_playing_single_notes' etc. whatever, just examples. 
- I need a camera "listener"
- When 'is_playing' the camera takes my image and shows it as if a 'relief' (or imprint) on some particular/magnetic field 
- When 'not_playing' the particular/magnetic field is gently swaying
- I have some interface to "start" the program and "stop" the program

How do I stub this out further?

# SECONDARY Resource 

    Python Environment Manager for Touch Designer Basics Resource: https://www.youtube.com/watch?v=dxWIliLYa-Q

AI Summary 

This video provides an introduction to the **TouchDesigner Python Environment Manager (tdPyEnvManager)**, a new component released with **TouchDesigner 2025.31550** that simplifies how developers work with third-party Python libraries and side-loaded environments (0:00 - 0:34).

**Key Takeaways and Features:**
* **Background:** Previously, integrating custom Python packages required manual installation and linking of external Python versions, which varied significantly between operating systems and was difficult to deploy across different machines (2:20 - 4:25).
* **Purpose:** The *tdPyEnvManager* acts as a centralized "home base" for managing these environments, making the setup process consistent, repeatable, and easier to share between projects (4:25 - 6:00).
* **Environment Types:**
    * **Python Virtual Environments:** The default, streamlined approach for per-project setups (5:56 - 6:13).
    * **Conda Environments:** A more flexible option that supports *Conda* packages and multiple environment instances, often used for data science and machine learning applications (6:13 - 6:58).

**Workflow Highlights:**
* **Setup:** The component is located in the *Palette* under the *Tools* folder (9:05). Users can create environments with a single pulse button and use standard `pip` or `conda` commands via the built-in command line interface (9:57 - 11:15, 17:11 - 18:50).
* **Deployment:** The tool allows users to export `requirements.txt` or `environment.yml` files, making it easy to recreate an identical environment on another machine simply by placing the file in the project directory (12:46 - 15:30, 20:44 - 22:23).
* **Advanced Use Case:** The video concludes by showcasing the *TDDepthAnythingRT* component, a practical application that uses this tool to run the *Depth Anything V2* model for real-time depth generation from textures (1:07 - 1:21, 25:12 - 26:38).