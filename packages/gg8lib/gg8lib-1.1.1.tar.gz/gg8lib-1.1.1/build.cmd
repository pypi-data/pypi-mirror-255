@echo off
echo Using TestPyPi
echo Use buildfinal for PyPi
timeout /t -1
py -m build
py -m twine upload --repository testpypi dist/*