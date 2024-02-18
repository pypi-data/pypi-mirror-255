# How to publish PIP package
1. python3 -m pip install --upgrade build
2. python3 -m build
3. python3 -m pip install --upgrade twine
4. python3 -m twine upload --repository testpypi dist/*
5. python3 -m twine upload dist/*
