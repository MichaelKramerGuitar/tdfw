![Coverage](https://codecov.io/gh/MichaelKramerGuitar/tdfw/branch/main/graph/badge.svg)


# tdfw
TouchDesigner Framework CLI scaffold tool with an opinionated slant towards State Driven/Code Driven project architecture.

## About

Hi, I'm Michael. I play guitar and write code. I was introduced to TouchDesigner by my friend Andrew Zolty, who's also known as `BREAKFAST`. He's an incredible kinetic artist. 

Getting started with TouchDesigner as a GUI never really happened for me. I started a few YouTube courses on it but didn't have the time to follow through and learn how to use the interface. 

But the concept of a network of nodes and subnodes made sense to my programmer/software engineer brain. I thought "there must be a purely code driven way to architect these TouchDesinger apps". So I looked on YouTube and found [this](https://www.youtube.com/watch?v=nQT7EhYCVg0) video (read more about that in [BACKGROUND.md](./BACKGROUND.md)). I was thrilled and what has resulted is essentially this tool which abstracts out all the boilerplate he gives. 

# How To Use

```bash
# Install 
uv pip install tdfw

# Start a TouchDesigner App
tdfw start-app <MyFirstApp>

# Create a Python Extension stub (from your TouchDesigner Project Root i.e. the dir with the <MyFirstApp>.toe file)
tdfw create-ext <MyFirstExt>
```
