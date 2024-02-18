@echo off
echo Using PyPi
echo Use build for TestPyPi
timeout /t -1
cls
color 0c
echo Have you incremented the version number?
timeout /t -1
cls
color 0c
echo Have you incremented the version number?
timeout /t -1
cls
color 0f
py -m build
py -m twine upload --repository pypi dist/*