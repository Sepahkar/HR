@echo off
cmd /k "cd /d %CD%\venv\Scripts & activate & cd /d %CD% & pip install django-hr-0.1.tar.gz & python unzip-package.py
pause