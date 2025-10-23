robocopy .\HR .\django-hr\HR /E &
@RD /S /Q django-hr\HR\migrations\
cd django-hr &
python setup.py sdist &
cd ../
python zip-package.py





