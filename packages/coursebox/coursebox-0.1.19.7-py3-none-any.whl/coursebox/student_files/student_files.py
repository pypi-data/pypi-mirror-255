import os, shutil
from coursebox.core.info_paths import get_paths
from coursebox.core.info import class_information
from snipper.snip_dir import snip_dir
from coursebox.material.homepage_lectures_exercises import fix_shared
from snipper.snipper_main import censor_file
from pathlib import Path
import fnmatch
import glob
from coursebox.material.documentation import fix_all_shared_files

def setup_student_files(run_files=True,
                        cut_files=True,
                        censor_files=True,
                        week=None, extra_dirs=None,
                        include_solutions=None,
                        projects=None,
                        setup_lectures=False, strict=True,
                        fix_shared_files=True,
                        include_exam_examples=False, # Include the directory with exam-related examples.
                        verbose=True,
                        students_irlc_tools=None, # Destination dir for the irlc folder (the one we really want to deploy).
                        midterms=None, # Can be a list: [0, 1]
                        include_docs=False, # Include the documentation directory, i.e. 02465public/src/docs.
                        convert_svg=True, # Whether to convert SVG file when deploying. Leave to true, unless we are doing CI/CD in which case inkscape may not be installed.
                        package="cp",
                        # fix_shared_files_func=None,
                        ):

    if midterms is None:
        midterms = []
    from coursebox.core import info_paths
    # from coursebox.core.info import class_information
    # info = class_information()
    from coursebox.core.info import core_conf
    PACKAGE = list(core_conf['projects_all'].values()).pop()['module_public'].split(".")[0]


    if censor_files:
        assert not run_files, "You cannot run files while you are censoring them -- your scripts will crash. Call with run_files=False."

    week = [week] if isinstance(week, int) else week
    if verbose:
        print("toolbox running. Fixing student files by copying to student dir")
    paths = get_paths()
    if include_solutions is None:
        include_solutions = []

    if projects is None:
        projects = []

    public_irlc_tools = f"{paths['02450public']}/src/{PACKAGE}"


    if students_irlc_tools is None:
        if censor_files:
            students_irlc_tools = f"{paths['02450students']}/{PACKAGE}"
        else:
            students_irlc_tools = f"{paths['02450students']}_complete/{PACKAGE}"

    if not os.path.isdir(students_irlc_tools):
        os.makedirs(students_irlc_tools)

    init_dest = students_irlc_tools+"/__init__.py"
    shutil.copy(public_irlc_tools + "/__init__.py", init_dest)
    for fpy in glob.glob(public_irlc_tools + "/*.py"):
        shutil.copy(fpy, students_irlc_tools + "/" + os.path.basename(fpy))

    if os.path.isfile(public_irlc_tools + "/../.coveragerc"):
        shutil.copy(public_irlc_tools + "/../.coveragerc", students_irlc_tools+ "/../.coveragerc")
    # assert False
    censor_file(init_dest)

    # Check for exclusion mask.
    exclude = list( info_paths.core_conf.get('student_files', {}).get('exclude', []) )

    if extra_dirs is None:
        extra_dirs = list(info_paths.core_conf.get('student_files', {}).get('extra_dirs', []))

    print("Extra dirs are", extra_dirs)
    exclude += [f'tests_week{w if w >= 10 else f"0{w}"}.py' for w in range(0,14) if w not in week]
    exclude = exclude + ["**/" + ex for ex in exclude]
    if not include_exam_examples:
        exclude += ['exam_tabular_examples']
    inclusion = [] # 'ex09old/cache']
    hws = []
    for m in midterms:
        # Copy the midterm from the exam directory into the public repository. This will ensure the midterm is later propagated to the student directory.
        # The midterm should always be distributed as a .zip file: This is the only legal distribution mechanism.
        # The midterm in the student directory does not need to be super-duper up to date. This is not the file which is distributed 'officially'.
        if verbose:
            print(m)

    if extra_dirs is None:
        # extra_dirs = []

        extra_dirs = ['utils', 'tests', 'exam/exam2023spring', 'pacman', 'gridworld', 'car'] # 'assignments',
        for m in midterms:
            if m == 0:
                extra_dirs += ['exam/midterm2023a']
            if m == 1:
                extra_dirs += ['exam/midterm2023b']

        # if include_exam_examples:
        #     extra_dirs += ['exam_tabular_examples']
    if setup_lectures:
        extra_dirs += [
            # 'lectures/chapter0pythonC',
            # 'lectures/chapter0pythonA',
            # 'lectures/chapter0pythonB',
            # 'lectures/chapter1',
            'lectures',
            # 'workshop'
        ]

    import coursebox.core.info

    for id in projects:
        # if setup_projects:
        if 'projects_all' in info_paths.core_conf:
            p = info_paths.core_conf['projects_all'][id]['class']
            extra_dirs += [os.path.basename(os.path.dirname(p.mfile()))]
        else:

            if id <= 3:
                extra_dirs += [f'project{id}'] # , 'project1', 'project2', 'project3']
            else:
                extra_dirs.append(f'project3i')

    if week is not None:
        for w in week:
            ex = str(w)
            ex = "ex" + ("0" + ex if len(ex) < 2 else ex)
            base = public_irlc_tools +"/"+ex
            if not os.path.isdir(base):
                continue
            d = {'base': base,
                 'out': students_irlc_tools +"/"+ex,
                 'exclusion': exclude,
                 'inclusion': inclusion,
                 'include_solutions': w in include_solutions,
                 'week': w}
            hws.append(d)

        weekn = 101
        for weekn, d in enumerate(extra_dirs):
            dutil = {'base': public_irlc_tools + "/" + d,
                 'out': students_irlc_tools + "/" + d,
                 'exclusion': exclude,
                 'inclusion': inclusion,
                'include_solutions': False,
                 'week': f'{weekn+100}'}
            hws.append(dutil)
        weekn += 1

    else:
        raise Exception("Specify a week")

    if len(hws) >  0:
        info = class_information(verbose=verbose)
        # print("references") # Bad idea because of the very long output.
        # print(info['references']['commands'])
    else:
        info = None
    for hw in hws:
        # if "ex08" in hw['out']:
        #     print("ex08")
        print("Fixing hw", hw['out'])
        n = fix_hw(paths=paths, info=info, hw=hw, out= hw['out'], output_dir=paths['shared'] +"/output", run_files=run_files, cut_files=cut_files,
                   package_base_dir=os.path.dirname(students_irlc_tools), censor_files=censor_files, strict=strict,
                   include_solutions=hw.get('include_solutions', False),
                   verbose=verbose)

        if censor_files:
            with open(paths['shared'] + f"/output/lines_{hw['week']}.txt", 'w') as f:
                f.write(str(n))


    if fix_shared_files:
        if verbose:
            print("> Homework fixed, copying shared files...")
        fix_all_shared_files(paths=paths, compile_templates=False, verbose=verbose, dosvg=convert_svg)

    if verbose:
        print("> Removing excluded files from students gitlab directory...")
    # for f in exclude + ["lectures"]:
    for l in list(Path(students_irlc_tools).glob('**/*')):
        if not os.path.exists(l):  # May have been removed as part of a subtree
            continue
        m = [ ex for ex in exclude if fnmatch.fnmatch(l, ex)]
        if len(m) > 0:
            if os.path.isdir(l):
                shutil.rmtree(l)
            else:
                os.remove(l)

    for f in glob.glob(public_irlc_tools +"/../requirements*.txt"):
        if "full" in os.path.basename(f):
            continue
        os.path.basename(f) # Copy requirements and all simiarly named files.
        shutil.copy(f, students_irlc_tools +"/../"+os.path.basename(f))
    # shutil.copy(public_irlc_tools +"/../requirements_conda.txt", students_irlc_tools +"/../requirements_conda.txt")
    # Don't think we need this anymore. Why copy docs if they cannot be compiled anyway? Perhaps for the complete docs?
    if include_docs:
        if os.path.isdir(students_irlc_tools + "/../docs"):
            shutil.rmtree(students_irlc_tools + "/../docs")
        # if not censor_files:
        shutil.copytree(public_irlc_tools + "/../docs", students_irlc_tools + "/../docs")
        # Fix reference to output.
        snip_dir(public_irlc_tools + "/../docs/source", students_irlc_tools + "/../docs/source", run_files=False, cut_files=False, censor_files=False, references=info['references'], verbose=verbose)
    if verbose:
        print("> All student file stuff completed.")



def fix_hw(paths, info, hw, out, output_dir, run_files=False, cut_files=False, censor_files=True,
           include_solutions=False,
           package_base_dir=None,  # When runing files using #!o, this specify the base directory of the  package the files resides in. Can be None.
           verbose=True,
           **kwargs):

    n, cutouts = snip_dir(source_dir=hw['base'], dest_dir=out, output_dir=output_dir, exclude=hw['exclusion'], references=info['references'],
                 run_files=run_files, cut_files=cut_files, license_head=info.get('code_copyright', None),
                 censor_files=censor_files,verbose=verbose,package_base_dir=package_base_dir)

    if "tests" in hw['base']:
        print(hw)
        print("Doing the base.")

    if include_solutions:
        wk = hw['base'].split("/")[-1]
        sp = paths['02450students'] + "/solutions/"
        if not os.path.exists(sp):
            os.mkdir(sp)
        sp = sp + wk
        if os.path.isdir(sp):
            shutil.rmtree(sp)
        # if not os.path.exists(sp):
        os.mkdir(sp)

        for f, cut in cutouts.items():
            if len(cut) > 0:
                fname = os.path.basename(f)
                sols = []
                stext = ["\n".join(lines) for lines in cut]
                for i, sol in enumerate(stext):
                    sols.append((sol,))
                    sout = sp + f"/{os.path.basename(fname)[:-3]}_TODO_{i + 1}.py"
                    wsol = True
                    print(sout, "(published)" if wsol else "")
                    if wsol:
                        with open(sout, "w") as f:
                            f.write(sol)

    return n
