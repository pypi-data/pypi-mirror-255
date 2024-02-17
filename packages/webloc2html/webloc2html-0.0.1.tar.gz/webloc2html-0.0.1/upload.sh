python3 -m pip install --upgrade twine
python3 -m pip install --upgrade build
rm -rf dist/*
python3 -m build
python3 -m twine upload --repository pypi dist/* --user __token__