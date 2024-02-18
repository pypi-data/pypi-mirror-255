import time
import PIL.Image
import os
import shutil
from slider.legacy_importer import slide_to_image
import glob
import re
import pickle
import datetime
import subprocess
from unitgrade_private.run import run
from coursebox.material.homepage_lectures_exercises import fix_shared
from coursebox.core.info_paths import get_paths

def setup_notes(paths=None, dosvg=True):
    from coursebox.material.homepage_lectures_exercises import fix_shared
    if paths is None:
        paths = get_paths()
    # setup_student_files(run_files=True, cut_files=True, censor_files=False, setup_lectures=True, week=[],
    #                     projects=[], verbose=False, convert_svg=False)
    fix_shared(paths, output_dir=paths['02450public'] + "/Notes/Latex", dosvg=dosvg)



def build_sphinx_documentation(cut_files=False, open_browser=True, build_and_copy_censored=True, CE=False, languages=('en', 'da'), show_all_solutions=False,
                        tolerate_problems=False, # If False, WARNINGS and ERRORS in the spinx build process will lead to a compile error. Set to True during local development.
                        sphinx_cache=False,  # If False, disable the Sphinx cache, i.e. include the -a (slightly longer rebuilds but all errors are caught & more reliable; recommended on stackexchange).
                        update_translations=False,
                        CE_public=False,
                        ):

    from coursebox.core.info_paths import get_paths
    paths = get_paths()
    if CE:
        languages = ("en",)

    if CE:
        SPHINX_TAG = " -t ce"

        if CE_public:
            SPHINX_TAG += " -t ce_public"
            PUBLIC_BUILD_DEST = f"{paths['02450public']}/public/ce_public"
        else:
            PUBLIC_BUILD_DEST = f"{paths['02450public']}/public/ce"

    else:
        SPHINX_TAG = ""
        PUBLIC_BUILD_DEST = f"{paths['02450public']}/public"

    # This will build the student documentation (temporary).
    # The functionality here should match the gitlab ci file closely.
    # from irlc_box.material.student_files import fix_all_shared_files

    # from cp_box.material.student_files import setup_student_files
    # from coursebox.material.homepage_lectures_exercises import set
    from coursebox.student_files.student_files import setup_student_files

    if os.path.isfile(d_ := f"{paths['book']}/{paths['course_number']}_Notes.pdf"):
        book_frontpage_png = paths['shared']+"/figures/book.png"
        slide_to_image(d_, book_frontpage_png, page_to_take=1)
        image = PIL.Image.open(book_frontpage_png)
        im = _makeShadow(image, iterations=100, offset=(25,)*2, shadowColour="#aaaaaa")
        im.save(book_frontpage_png)

    fix_all_shared_files(dosvg=True)

    """ Return extra information required for building the documentation.
    """
    # from coursebox.core.info_paths import get_paths
    from coursebox.core.info import class_information
    from coursebox.core import info_paths
    # paths = get_paths()
    info = class_information()
    # {{ (date1|to_datetime - date2|to_datetime).days < lecture['show_slides_after'] }}
    # (info['lectures'][2]['date'].now() - info['lectures'][2]['date']).days < lecture['show_slides_after'] }}
    source = _get_source(paths)
    PACKAGE = info.get('package', 'cp')

    x = {}
    for f in glob.glob(f"{source}/projects/project*.rst"):
        k = int(re.findall(r'\d+', f)[-1])
        x[k] = {}

        exfiles = []
        for g in glob.glob(f"{paths['02450students']}/{PACKAGE}/project{k}/*.py"):
            with open(g, 'r') as ff:
                if "TODO" in ff.read():
                    exfiles.append(g)
        files = [os.path.relpath(ff, paths['02450students']) for ff in exfiles]
        x[k]['files'] = files
        # print(">>> k class is: ")
        # print(info_paths.core_conf['projects_all'][k])
        f = info_paths.core_conf['projects_all'][k]['class'].mfile()
        with open(f.split("_grade.py")[0], 'r') as ff:
            l = [l for l in ff.read().splitlines() if "(Report)" in l].pop().split("(")[0].split(" ")[-1]

        token = f"{os.path.relpath(os.path.dirname(f), paths['02450public'] + '/src')}/{l}_handin_k_of_n.token"
        x[k]['token'] = token
        f = os.path.relpath(f, paths['02450public'] + "/src")
        if f.endswith("_complete.py"):
            f = f.split("_complete.py")[0]
            f = "_".join(f.split("_")[:-1])
            f = f + "_grade.py"
        else:
            f = f.split(".py")[0] + "_grade.py"
        x[k]['grade_file'] = f
        x[k]['grade_module'] = f[:-3].replace("/", ".")

    """ TH: What happens here is that we cache the report information so we can later load it (above) when rst source is build. 
    The reason we split the code like this is because we don't have access to the report classes during the Sphinx build process, 
    and that means some of the variables are not easily set. This is a bit of a dirty fix, but it works. """
    with open(extra_info := source + "/_extra_info.pkl", 'wb') as f:
        print("Writing extra info to", extra_info)
        pickle.dump(x, f)

    for f in glob.glob(f"{paths['02450public']}/src/docs/templates/*.rst"):
        if f.endswith("blurb.rst") or f.endswith("base.rst"):
            continue # We dealt with these; nb. very hacky stuff.

    # PROJECTS = [int(os.path.basename(f)[len("project"):]) for f in glob.glob(f"{paths['02450public']}/src/cp/project*")]
    # WEEKS = [int(os.path.basename(f)[len("ex"):]) for f in glob.glob(f"{paths['02450public']}/src/cp/ex*") if not os.path.basename(f) == 'exam']

    from coursebox.core.info_paths import core_conf

    PROJECTS = list(core_conf['projects_all'].keys())
    WEEKS = list(core_conf['weeks_all'].keys())


    pdfs = []
    for g in glob.glob(paths['pdf_out'] +"/handout/*.pdf"):
        dst = paths['02450public'] + "/src/docs/assets/"+os.path.basename(g)[:-4] + "-handout.pdf"
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy(g,  dst)
        pdfs.append(dst)

    for g in glob.glob(paths['pdf_out'] + "/*.pdf"):
        if "_devel" in g:
            continue
        dst = paths['02450public'] + "/src/docs/assets/" + os.path.basename(g)
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy(g, dst)
        pdfs.append(dst)

    for g in [paths['pdf_out'] + "/" + paths['course_number'] + "_Notes.pdf"]:
        dst = paths['02450public'] + "/src/docs/assets/" + os.path.basename(g)
        shutil.copy(g, dst)
        pdfs.append(dst)

    # Copy shared templates.
    if not os.path.isdir(paths['02450public'] + "/src/docs/source/templates_generated"):
        os.mkdir(paths['02450public'] + "/src/docs/source/templates_generated")
    for g in glob.glob(paths['shared'] + "/templates/*.rst"):
        if '_partial.rst' in g:
            continue
        shutil.copy(g, f"{paths['02450public']}/src/docs/source/templates_generated/{os.path.basename(g)}")
    ## Update the translation files.

    if update_translations:
        print("build_documentation> updating ze translations.")
        pr1 = run(f"cd {paths['docs']} && make gettext", print_output=False, log_output=True, check=True)
        pr2 = run(f"cd {paths['docs']} && sphinx-intl update -p build/gettext", print_output=False, log_output=True, check=True)
        assert pr1.returncode == 0 and pr2.returncode ==0, "you done goofed in the translation building."
        print("build_documentation> I am done updating ze translation!")

    # from cp_box.checks.checks import deploy_student_repos
    BAD_MODULES_DIR = False
    deploy_students_complete() # I guess this will build public and private.
    students_complete = paths['02450students'] + "_complete"
    fns = []

    # Blow public modules. This is because renamed files will otherwise stay around and when you later build the version
    # without solutions, and verify the without/with solutions version has the same files, the old files will cause problems.
    if os.path.isdir(d_ := f"{PUBLIC_BUILD_DEST}/_modules"):
        shutil.rmtree(d_)

    for l in languages:
        if l=='en':
            lang = ""
            TAG_EXTRA = ''
        else:
            lang = " -D language='da' "
            TAG_EXTRA = '-t da'
        if not sphinx_cache:
            TAG_EXTRA += ' -a'

        # " sphinx-build -b html source build -D language='da' -t da "
        _FINAL_BUILD_DEST = f"{PUBLIC_BUILD_DEST}{'/da' if l=='da' else ''}"

        SET_PATH = f"""PYTHONPATH="{paths['02450students'] + '_complete'}" """
        if os.name == 'nt':
            SET_PATH = "set "+SET_PATH +" && "

        cmd_ = f"""cd "{students_complete}/docs" && {SET_PATH} sphinx-build  -b html source "{os.path.relpath(_FINAL_BUILD_DEST, students_complete+'/docs')}" {TAG_EXTRA} {SPHINX_TAG} {lang}"""
        cmd =  f"""cd "{students_complete}/docs" && sphinx-build  -b html source "{os.path.relpath(_FINAL_BUILD_DEST, students_complete + '/docs')}" {TAG_EXTRA} {SPHINX_TAG} {lang}"""

        # if os.name == "nt":
        #     cmd = cmd.replace("&&", ";")
        # cd "C:\Users\tuhe\Documents\02002students_complete/docs" ; $env:PYTHONPATH="C:\Users\tuhe\Documents\02002students_complete" ; sphinx-build  -b html source ..\..\02002public\public  -a

        # p = subprocess.run(cmd, shell=True, capture_output=True, encoding="utf-8")
        # print(">>>>>>>>>> inside build_documentation.py. The python binary is", sys.executable)
        cmd = cmd.replace("\\", "/")
        print(">>> Sphinx main build command is\n", cmd_)
        print(" ")

        # subprocess.run(cmd, shell=True)
        # subprocess.run('cd "C:/Users/tuhe/Documents/02002students_complete/docs" && set PYTHONPATH="C:/Users/tuhe/Documents/02002students_complete" && sphinx-build  -b html source "../../02002public/public"  -a  ', shell=True)

        problems = []
        if os.name == "nt":

            # do win specific stuff here.
            # >> > result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
            # >> > result.stdout
            pass

        my_env = os.environ.copy()
        my_env['PYTHONPATH'] = (paths['02450students'] + '_complete').replace("\\", "/")
        process = run(cmd, print_output=True, log_output=True, check=False, env=my_env)

        """r 
         cd /home/tuhe/Documents/02465students_complete/ && sphinx-build -b html docs/source ./public 
        cd "/home/tuhe/Documents/02465students_complete/docs" && sphinx-build  -b html source "../../02465public/public"  -a 
    
        """
        if os.name == 'nt':
            # time.sleep(10)
            process = run(cmd, print_output=True, log_output=True, check=False, env=my_env)
            print("TH 2023 Juli: Running sphinx compilation job twice bc of path error on windows. This should be easy to fix but I don't know enough about windows to do so.")
            print(process.stderr.getvalue())

        errors = process.stderr.getvalue()

        file = f"{os.path.normpath(PUBLIC_BUILD_DEST)}/log_{l}.txt"
        fns.append(file)

        if not os.path.isdir(d_ := os.path.dirname(file)):
            os.makedirs(d_)
        with open(file,'w') as f:
            f.write("\n".join(["stdout","="*100,"", process.stdout.getvalue(), "stderr","="*100,"", errors, " ","build at", datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") ]))

        problems = [l for l in  errors.splitlines() if ("WARNING:" in l ) or "ERROR" in l]

        if len(problems) > 0 and not tolerate_problems:
            print("=" * 50)
            print("""Sphinx compilation encountered errors and/or warnings. Although the documentation can build, we are running build_documentation(..., tolerate_problems=False), which is the 
default on gitlab, as we don't want a pileup of small(ish) build errors. So carefully read through the output above to identify errors and fix them. 
Remember you can also use the tolerate_problems argument locally to fix problems in that way.

Below is a summary of the problems we found: """)
            for p in problems:
                print(">", p)
            raise Exception("There were compilation problems when compiling documentation using sphinx. Please read output above carefully for details. ")

        # Slightly silly code that copies the language thumbnails. I guess I could find a way to include them and do it automatically but oh well.
        if not os.path.isdir(fbd := f"{_FINAL_BUILD_DEST}/_images"):
            os.makedirs(fbd)

        for im in ["gb.png", "dk.png"]:
            shutil.copy(f"{paths['shared']}/figures/{im}", f"{_FINAL_BUILD_DEST}/_images/{im}")


    if build_and_copy_censored:
        verbose = False
        setup_student_files(run_files=False, cut_files=False, censor_files=True, setup_lectures=cut_files,
                            week=WEEKS, projects=PROJECTS,
                            fix_shared_files=True, verbose=verbose, include_docs=True)

        cmd_with_pythonpath = f"cd {paths['02450students']}/docs && PYTHONPATH={paths['02450students']} sphinx-build -b html source ../public {SPHINX_TAG} -a"
        cmd = f"cd {paths['02450students']}/docs && sphinx-build -b html source ../public {SPHINX_TAG} -a"

        # try:
        my_env = os.environ.copy()
        my_env['PYTHONPATH'] = paths['02450students'].replace("\\","/")
        print("> Building documentation based on .py-files that do not contain solutions based on command:\n", cmd_with_pythonpath)
        out = subprocess.run(cmd, shell=True, check=True, env=my_env, capture_output=False)

        known_modules = set([os.path.relpath(f, PUBLIC_BUILD_DEST) for f in glob.glob(f"{PUBLIC_BUILD_DEST}/_modules/**/*.html", recursive=True) ] )
        build_modules = set([os.path.relpath(f, f"{paths['02450students']}/public") for f in glob.glob(f"{paths['02450students']}/public/_modules/**/*.html", recursive=True) ] )

        # known_modules == build_modules
        # set.difference()
        for f in known_modules.difference(build_modules):
            print(f)
        for f in known_modules.difference(build_modules):
            print("> Documentation error. View source function did not build correctly since the (censored) files did not contain the html file: ", f)
            print("> The likely cause of this problem is that you got a top-level #!b tag in the corresponding python file, meaning the documentation cannot be build for this file. ")
            print("> To fix the problem, use the #!b;noerror command to suppress Exceptions.")
            raise Exception(f"View source file not found for {f}. Please see terminal output above.")

        shutil.rmtree(paths['02450students'] + "/docs")
        if os.path.isdir(f"{PUBLIC_BUILD_DEST}/_modules"):
            shutil.rmtree(f"{PUBLIC_BUILD_DEST}/_modules")

        if os.path.isdir(f"{paths['02450students']}/public/_modules"):
            shutil.copytree(f"{paths['02450students']}/public/_modules", f"{PUBLIC_BUILD_DEST}/_modules")
        else:
            BAD_MODULES_DIR = True

        if os.path.isdir(f"{paths['02450students']}/docs"):
            shutil.rmtree(f"{paths['02450students']}/docs")

        if os.path.isdir(f"{paths['02450students']}/public"):
            shutil.rmtree(f"{paths['02450students']}/public")

    # copy images into the _image folder.


    if BAD_MODULES_DIR:
        print("WARNING!: Student _modules dir not generated. Probably script crash. This is a bad situation. Documentation view source links not up to date. ")

    if open_browser:
        import webbrowser
        try:
            if os.name == "nt":
                chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                webbrowser.get("chrome").open(f"{PUBLIC_BUILD_DEST}/index.html")
            else:
                webbrowser.get("chromium").open(f"{PUBLIC_BUILD_DEST}/index.html")
        except Exception as e:
            print("URL to local host website:",f"{PUBLIC_BUILD_DEST}/index.html")
            webbrowser.get("firefox").open(f"{PUBLIC_BUILD_DEST}/index.html")
            pass
    for f in fns:
        print("> See log file", f, "at", f"https://cp.pages.compute.dtu.dk/02002public/{os.path.relpath(f, PUBLIC_BUILD_DEST)}")


def _makeShadow(image, iterations, border=8, offset=(3,3), backgroundColour="#ffffff", shadowColour="#444444"):
    # backgroundColour = ()
    from PIL import Image, ImageFilter
    # from PIL import

    # image: base image to give a drop shadow
    # iterations: number of times to apply the blur filter to the shadow
    # border: border to give the image to leave space for the shadow
    # offset: offset of the shadow as [x,y]
    # backgroundCOlour: colour of the background
    # shadowColour: colour of the drop shadow

    # Calculate the size of the shadow's image
    fullWidth = image.size[0] + abs(offset[0]) + 2 * border
    fullHeight = image.size[1] + abs(offset[1]) + 2 * border

    # Create the shadow's image. Match the parent image's mode.
    shadow = Image.new(image.mode, (fullWidth, fullHeight), backgroundColour)

    # Place the shadow, with the required offset
    shadowLeft = border + max(offset[0], 0)  # if <0, push the rest of the image right
    shadowTop = border + max(offset[1], 0)  # if <0, push the rest of the image down
    # Paste in the constant colour
    shadow.paste(shadowColour,
                 [shadowLeft, shadowTop,
                  shadowLeft + image.size[0],
                  shadowTop + image.size[1]])

    # Apply the BLUR filter repeatedly
    for i in range(iterations):
        shadow = shadow.filter(ImageFilter.BLUR)

    # Paste the original image on top of the shadow
    imgLeft = border - min(offset[0], 0)  # if the shadow offset was <0, push right
    imgTop = border - min(offset[1], 0)  # if the shadow offset was <0, push down
    shadow.paste(image, (imgLeft, imgTop))

    return shadow


def _get_source(paths):
    return paths['02450public'] + "/src/docs/source"
    # return source



def deploy_students_complete(verbose=False):
    from coursebox.core.info_paths import get_paths
    paths = get_paths()
    from coursebox.core.info_paths import core_conf
    PROJECTS = list(core_conf['projects_all'].keys())
    WEEKS = list(core_conf['weeks_all'].keys())

    # from cp_box.material.student_files import setup_student_files
    from coursebox.student_files.student_files import setup_student_files
    studens_complete = paths['02450students'] + '_complete'
    if os.path.isdir(studens_complete):
        shutil.rmtree(paths['02450students'] + '_complete')
    # PROJECTS = [int(os.path.basename(f)[len("project"):]) for f in
    #             glob.glob(f"{paths['02450public']}/src/cp/project*")]
    # WEEKS = [int(os.path.basename(f)[len("ex"):]) for f in glob.glob(f"{paths['02450public']}/src/cp/ex*") if
    #          not os.path.basename(f) == 'exam']
    # shutil.rmtree(paths['02450students'] + '_complete')
    cut_files=False
    # verbose=False
    # cut_files = False # This deploy to students_complete.
    setup_student_files(run_files=False, cut_files=cut_files, censor_files=False, setup_lectures=cut_files,
                        week=WEEKS, projects=PROJECTS,
                        fix_shared_files=cut_files, verbose=verbose, include_docs=True)


def fix_all_shared_files(paths=None, dosvg=False,compile_templates=True, verbose=False):
    # Tue: Do these imports here to avoid circular imports.
    from coursebox.core.info_paths import get_paths
    # from irlc_box.irlc_main import setup_notes
    # Make the chamor snapshot list.
    setup_notes(dosvg=dosvg)
    paths = get_paths()
    # from coursebox.do

    for w in range(14):
        out = paths['exercises'] + f"/ExercisesPython/Exercise{w}/latex"
        if os.path.isdir(out):
            fix_shared(paths, out, pdf2png=False,dosvg=dosvg, compile_templates=compile_templates, verbose=verbose)  # , dosvg=dosvg  <--- please update coursebox (script broken as is)

        out = paths['lectures'] + f"/Lecture_{w}/Latex"
        if os.path.isdir(out):
            fix_shared(paths, out, pdf2png=False, compile_templates=compile_templates, verbose=verbose)

    out = paths['exercises'] + f"/LatexCompilationDir/Latex"
    if os.path.isdir(out):
        fix_shared(paths, out, pdf2png=False, dosvg=dosvg, compile_templates=compile_templates, verbose=verbose)  # , dosvg=dosvg  <--- please update coursebox (script broken as is)

    # New 2023: Sync with documentation path.
    out = paths['02450public'] + f"/src/docs/shared"
    if os.path.isdir(out):
        # I feel we need to convert the SVG images?
        fix_shared(paths, out, pdf2png=dosvg, dosvg=dosvg, compile_templates=compile_templates, verbose=verbose)  # , dosvg=dosvg  <--- please update coursebox (script broken as is)
    else:
        print("Coursebox> No documentation shared directory. This is very, very odd indeed. I am stopping now. ")


