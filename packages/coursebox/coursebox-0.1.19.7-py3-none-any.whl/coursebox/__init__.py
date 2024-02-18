##
# Set configuration file.
# conf = "point to main caller file that defines year, semester, etc."

from coursebox.setup_coursebox import setup_coursebox
from coursebox.core.info_paths import get_paths
from coursebox.core.info import class_information
from coursebox.admin.gitlab import sync_tas_with_git

# from coursebox.core import info_paths


def setup_student_files(*args, **kwargs):
    from coursebox.setup_coursebox import funcs

    funcs['setup_student_files'](*args, **kwargs)
    funcs['fix_all_shared_files'](*args, **kwargs)
