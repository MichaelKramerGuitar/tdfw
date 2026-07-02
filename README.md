![Coverage](https://codecov.io/gh/MichaelKramerGuitar/tdfw/branch/main/graph/badge.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)


# tdfw
TouchDesigner Framework CLI scaffold tool with an opinionated slant towards State Driven/Code Driven project architecture.

## About

Hi, I'm Michael. I play guitar and write code. I was introduced to TouchDesigner by my friend Andrew Zolty, who's also known as `BREAKFAST`. He's an incredible kinetic artist. 

Getting started with TouchDesigner as a GUI never really happened for me. I started a few YouTube courses on it but didn't have the time to follow through and learn how to use the interface. 

But the concept of a network of nodes and subnodes made sense to my programmer/software engineer brain. I thought "there must be a purely code driven way to architect these TouchDesinger apps". So I looked on YouTube and found [this](https://www.youtube.com/watch?v=nQT7EhYCVg0) video (read more about that in [BACKGROUND.md](./BACKGROUND.md)). I was thrilled and what has resulted is essentially this tool which abstracts out all the boilerplate he gives. 

# How To Use

```bash
# 1. Install prerequisites

# Make sure Python is installed and matches the TouchDesigner distributions version and a package manager like uv is available globally.

# 2. Install tdfw globally
uv pip install --upgrade tdfw

# 3. Confirm installation and explore options
tdfw help

# 4. Doctor check (optional but recommended)
# Ensures uv/pip/conda and TouchDesigner paths are set up correctly.
tdfw doctor

# 5. Scaffold a new TouchDesigner App
tdfw start-app <MyFirstApp>

# 6. Open your app in your editor
cd <MyFirstApp>
code .   # or cursor ., vim ., etc.

# 7. Create Python Extension stubs
# Run from your TouchDesigner Project Root (the dir with <MyFirstApp>.toe)
tdfw create-ext <MyFirstExt>

# 8. Manage environments
# Initialize a uv environment (falls back to pip if uv is missing)
tdfw init-env <MyAppEnv>

# Export reproducible requirements for TouchDesigner
tdfw export-env --manager uv --output requirements.txt

# Import environment from requirements.txt or environment.yml
tdfw import-env requirements.txt
```

# Philosophy

**Legibility first**: Every scaffolded app reads like a table of contents. Extensions are explicit, declarative, and easy to debug.

**Environment reproducibility**: uv.lock for developers, requirements.txt or environment.yml for TouchDesigner. Both humans and TD can bootstrap consistently.

**Cross‑platform ready**: .bat for Windows, .bash for macOS/Linux, with override support for TouchDesigner executable paths.

**Doctor mindset**: Always check your system before scaffolding — tdfw doctor ensures you’re ready.

**Iterative growth**: Start simple (one app, one extension), then evolve into complex state‑machine architectures without spaghetti networks.