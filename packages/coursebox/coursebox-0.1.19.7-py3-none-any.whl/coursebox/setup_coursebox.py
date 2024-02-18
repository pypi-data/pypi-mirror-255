from coursebox.core import info_paths

def _no_such_function(*args, **kwargs):
    raise NotImplementedError("The function does nto exist. You muast pass it to coursebox setup_coursebox(..) for this to work")

funcs = {'setup_student_files': _no_such_function,
         'fix_all_shared_files' : _no_such_function
         }

def setup_coursebox(working_dir, course_number="02450", semester='spring', year=2019,
    slides_showsolutions=True,
    slides_includelabels=False,
    continuing_education_mode = False,
    slides_shownotes=False,
    continuing_education_month = "March", post_process_info=None,
                    setup_student_files=None,
                    fix_all_shared_files=None,
                    **kwargs):
    funcs['setup_student_files'] = setup_student_files
    funcs['fix_all_shared_files'] = fix_all_shared_files

    info_paths.core_conf['working_dir'] = working_dir
    info_paths.core_conf['course_number'] = course_number
    info_paths.core_conf['semester'] = semester
    info_paths.core_conf['year'] = year
    info_paths.core_conf['slides_showsolutions'] = slides_showsolutions
    info_paths.core_conf['slides_includelabels'] = slides_includelabels
    info_paths.core_conf['continuing_education_mode'] = continuing_education_mode
    info_paths.core_conf['continuing_education_month'] = continuing_education_month
    info_paths.core_conf['slides_shownotes'] = slides_shownotes
    info_paths.core_conf['post_process_info'] = post_process_info

    for a, val in kwargs.items():
        info_paths.core_conf[a] = val
