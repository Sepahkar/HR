import shutil
import os
dir_name = os.path.join(os.path.dirname(__file__),"HR")
output_file = os.path.join(os.path.dirname(__file__),"django-hr","dist","hr-pkg")
shutil.make_archive(output_file, 'zip', dir_name)


