#!/bin/bash 
python -m build
cd dist
var=$(ls | sort -V | tail -n 1)
pip install $var --force-reinstall
# do tests here
cd ..
python3 -m twine upload --skip-existing dist/*