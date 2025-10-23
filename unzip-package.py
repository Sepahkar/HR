import shutil
import os
file_name = os.path.join(os.path.dirname(__file__),"hr-pkg.zip")
des = os.path.join(os.path.dirname(__file__),"venv","Lib","site-packages","HR")
migrations_des = os.path.join(os.path.dirname(__file__),"venv","Lib","site-packages","HR","migrations")
shutil.unpack_archive(file_name,des,"zip")
try:
    shutil.rmtree(migrations_des)
except OSError as e:
    print("not delete migrations")