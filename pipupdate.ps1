python3 -m build
cd dist
$var=ls | sort -V | Select-Object -last 1
pip install $var --force-reinstall
cd ..
python3 -m twine upload --skip-existing dist/*