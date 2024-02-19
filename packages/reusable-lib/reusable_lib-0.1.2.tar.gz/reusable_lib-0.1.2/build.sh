rm dist/*
python -m build
ls dist -l
python3 -m twine upload dist/*
