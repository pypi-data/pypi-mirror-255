# import thtools
import os
import shutil
from datetime import datetime
from warnings import warn

# don't remove this one. Set by setup_toolbox
core_conf = {}

def get_paths():
    cd = core_conf['working_dir']
    cd = os.path.basename( os.path.dirname( os.path.dirname(cd) ) )
    num = cd[:-6] # course number
    # num = cd[:cd.find("public")]
    CDIR = core_conf['working_dir']
    course_number = core_conf['course_number']

    root_02450public = os.path.normpath(CDIR + "/../..")
    root_02450private = os.path.normpath(root_02450public + "/../%sprivate"%num)
    root_02450instructors = os.path.normpath(root_02450private + "/../%sinstructors"%num)
    root_02450students = os.path.normpath(root_02450private + "/../%sstudents" % num)

    root_02450public = root_02450public.replace("\\", "/")
    root_02450private = root_02450private.replace("\\", "/")
    semester_path = root_02450private + "/semesters/" + semester_id()

    if not os.path.isdir(semester_path):
        os.makedirs(semester_path)

    main_conf = semester_path + "/" + semester_id() + ".xlsx"

    if not os.path.exists(main_conf):
        main_conf = f"{semester_path}/{course_number}_{semester_id()}.xlsx"
    if not os.path.exists(main_conf):
        # cf = _info_cache_file()
        # print("Information configuration file not found. Loading from cache:", cf)
        # if not os.path.isfile(cf):
        #     raise Exception("No configuration found. Please set up configuration file at: " + paths['information.xlsx'])
        pass
        # raise Exception("Main config file not found " + main_conf)

    _files = []
    sCE = "CE" if core_conf['continuing_education_mode'] else ""

    paths ={
        # 'docs':
        # 'docs':
        '02450private': root_02450private,
        '02450public': root_02450public,
        '02450instructors': root_02450instructors,
        'instructors': root_02450instructors,
        '02450students': root_02450students,
        'shared': root_02450public+"/shared",
        'exams': root_02450private+"/Exam",
        'course_number': course_number,
        'semester': semester_path,
        'information.xlsx': main_conf,
        'homepage_template': "%s/WEB/index_partial23.html"%root_02450public,
        'homepage_out': "%s/WEB/%sindex.html"%(root_02450public, sCE),
        'pdf_out': "%s/%spdf_out"%(root_02450public, sCE),
        'exercises': root_02450public + "/Exercises", # this does not seem correct.
        'shared_latex_compilation_dir': root_02450public + "/Exercises/LatexCompilationDir/Latex",
        'book': root_02450public + "/MLBOOK/Latex",
        'lectures': root_02450public + "/Lectures",
        'instructor_project_evaluations': "%s/project_evaluations_%s" % (root_02450instructors, semester_id()),
        'project_evaluations_template.xlsx': root_02450private +"/ReportEvaluation/%s_project_template.xlsx"%num,
        'collected_project_evaluations.xlsx': semester_path + "/"+course_number+"_project_" + semester_id() + ".xlsx",
        'electronic_exam_handin_dir': semester_path + "/exam/electronic_handin",
        'exam_results_template.xlsx': root_02450private +"/Exam/%s_results_TEMPLATE.xlsx"%num,
        'exam_instructions': root_02450public + "/ExamInstructions",
        'docs': root_02450public +"/src/docs",
        'src': root_02450public + "/src",
    }
    if not os.path.isdir(paths['book']):
        paths['book'] =  root_02450public + "/Notes/Latex"

    # if 'book' in paths and os.path.isdir(paths['book']):
    #     pass

    if os.path.exists(os.path.dirname(paths['instructor_project_evaluations'])):
        if not os.path.isdir(paths['instructor_project_evaluations']):
            os.mkdir(paths['instructor_project_evaluations'])
    else:
        pass
    for (key, loc, template) in _files:
        if not os.path.exists(os.path.dirname(loc)):
            os.makedirs(os.path.dirname(loc))
        if not os.path.exists(loc):
            shutil.copyfile(template, loc)
        paths[key] = loc
    return paths


def semester():
    continuing_education_mode = core_conf['continuing_education_mode']
    continuing_education_month = core_conf['continuing_education_month']
    semester = core_conf['semester']

    if continuing_education_mode:
        month = continuing_education_month.lower()
        return month
    else:
        return semester.lower()

def year():
    return core_conf['year']

def semester_id():
    s = "CE" if core_conf['continuing_education_mode'] else ""
    return "%s%i%s"%(s, year(), semester())

def today():
    return datetime.today()