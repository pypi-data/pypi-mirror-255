[![pipeline status](https://gitlab.com/Thaodan/private-fork/badges/master/pipeline.svg)](https://gitlab.com/Thaodan/private-fork/-/commits/master)
# Datapack Visualizer

This is a very scuffed tool I made mostly for myself. So if you find madman-logic please let me know - I've probably just grown too used to it to notice myself.

### Installation
- Python 3.9.5 or greater is required.
- Install [Graphviz](https://graphviz.org/download/) and add it to PATH.
- Install DatapackVisualizer from pypi:
```bash
pip install dpvisu
```
### Use
Call `dpvisu` and follow the instructions. If everything is set up right, a `.svg` file should get generated and displayed.\
Alternatively you can provide the full path to any of the following folders as a command-line argument (only 1).
 - `../datapack/` - Generates call graph for all contained datapacks in a single `.svg` (Useful in case of multiple inter-connected datapacks)
 - `../datapack/<datapack_name>/` - Generates a call graph for the given datapack
 - `../datapack/<datapack_name>/data/` - Generates a call graph for the given datapack
