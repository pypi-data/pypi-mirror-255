# pastebin-replace

Small, simple python package to replace a file with raw code from Pastebin.

## Installation

### From Source

```bash
pip install .
```

### With pip (PyPI)

```bash
pip install pastebin-replace
```

## Usage

```python
pbreplace(path, link)
```

## Example

Suppose you have an empty file named `test.txt` located in `C:\Users\Yourname\Downloads\test.txt`. And you know a public Pastebin `https://pastebin.com/hcv2WRnX` containing some text.

```python
from pastebin_replace import pbreplace

pbreplace("C:\Users\Yourname\Downloads\test.txt", "https://pastebin.com/hcv2WRnX")
```

### Note
Replaced file can't be recovered. Be careful on the path you provided.

### Background
Why did I make this? I need this package for a specific usage in my Google Colab workflow.

### Special Thanks
[pastebin-as-file](https://github.com/K0IN/pastebin-as-file) repo for the PyPI directory format. I'm a noob and just learned about Python package stuff tonight :D