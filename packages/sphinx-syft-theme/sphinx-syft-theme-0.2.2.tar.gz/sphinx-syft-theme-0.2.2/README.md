# Sphinx Syft Theme

This is Sphinx Syft Theme package. You can contribute via
[Github](https://github.com/callezenwaka/sphinx-syft-theme/).

Build files
```
jupyter-book build .
```

Build all files
```
jupyter-book build --all .
```

To delete the .jupyter_cache folder as well, add the --all flag like so
```
jupyter-book clean . --all
```

Install dependencies
```
pip install -r requirements.txt

```

```
pip install build

python3 -m build --sdist

python3 -m build --wheel

twine check dist/*

twine upload dist/*
```