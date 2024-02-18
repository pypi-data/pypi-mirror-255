import subprocess
import time
from collections import defaultdict
import glob
import tabulate
import sys
import warnings

def check_by_grade_script(student_dir, module):
    """
    TH 2023: Must be runable on a minimal system, i.e. no unitgrade_private etc.

    :param student_dir:
    :param module:
    :return:
    """
    import sys
    # from unitgrade.utils import
    # from unitgrade_private.run import run # Don't use tihs as it is not available during test.

    cmd = f"cd {student_dir} && {sys.executable} -m {module}"

    # output = subprocess.check_output(f"cd {student_dir} && {sys.executable} -m {module}", shell=True, check=False)
    from subprocess import run
    print("Running command", cmd)
    p = run(cmd, capture_output=True, check=False, shell=True)
    print('exit status:', p.returncode)
    out = p.stdout.decode()
    stderr = p.stderr.decode()
    # process = run(cmd, print_output=False, check=False)
    # stderr = process.stderr.getvalue().strip()
    if p.returncode != 0 and not (stderr == "Killed" or stderr == ""):
        # print(.stdout.getvalue())
        print(out)
        print("-"*50)
        print(stderr)
        print("-"*50)
        raise Exception("Run command gave error: " + cmd)
    # out = process.stdout.getvalue()
    # s = out[out.rfind("handin"):out.rfind(".token")]
    # try:
    #     p = int(s.split("_")[1])
    #     total = int(s.split("_")[-1])
    # except Exception as e:
    #     print("Encountered problem in", module)
    #     print(out)
    #     print(stderr)
    #     print(s)
    #     print(cmd)
    #     raise e
    # out = out.decode("utf-8")
    # print(out)
    s = out[out.rfind("handin"):out.rfind(".token")]
    # try:
    # p = int(s.split("_")[1])
    # total = int(s.split("_")[-1])

    a, _, b = s.split("_")[-3:]

    points = int(a), int(b)

    # total = [l for l in out.splitlines() if l.strip().startswith("Total")].pop()
    # total.split(" ")[1].split("/")
    # points = total.split(" ")[-1]
    # a, b = points.split("/")
    # points = int(a), int(b)
    # points =
    return points, out



def check_py_script(student_dir, module):
    cmd = f"cd {student_dir} && {sys.executable} -m {module} --unmute" # Don't hardcode 'python' bc. of 'python3' on mac/Linux.
    try:
        output = subprocess.check_output(cmd, shell=True)
    except Exception as e:
        print("command that failed was")
        print(cmd)
        # print("The std. out from the command was")
        # print(output.decode("utf-8"))
        raise e

    out = output.decode("utf-8")
    total = [l for l in out.splitlines() if l.strip().startswith("Total")].pop()
    total.split(" ")[1].split("/")
    points = total.split(" ")[-1]
    a, b = points.split("/")
    points = int(a), int(b)
    return points, out

# def check_by_grade_script(student_dir, module):
#     output = subprocess.check_output(f"cd {student_dir} && {sys.executable}  -m {module}", shell=True)
#     out = output.decode("utf-8")
#     s = out[out.rfind("handin"):out.rfind(".token")]
#     try:
#         p = int(s.split("_")[1])
#         total = int(s.split("_")[-1])
#     except Exception as e:
#         print("Encountered problem in", module)
#         print(out)
#         print(s)
#         raise e
#     return p, total, out

def check_pyhon_documentation_in_student_repo(student_dir_complete=None, package="cp"):
    from interrogate import coverage
    if student_dir_complete is None:
        # It is important to not import cp_box here during CI/CD. The coursebox packages is not/should not be installed.
        from cp_box import cp_main
        from coursebox.core.info_paths import get_paths
        paths = get_paths()
        student_dir_complete = paths['02450students'] + "_complete"
        # At this point, also set up the studnets_complete repo.
        from cp_box.material.build_documentation import deploy_students_complete
        deploy_students_complete()

    from pydocstyle.checker import check
    n = 0
    files_ = glob.glob(f"{student_dir_complete}/{package}/ex*/*.py", recursive=True) + glob.glob(f"{student_dir_complete}/{package}/project*/*.py", recursive=True)
    files_ = [f for f in files_ if not f.endswith("_grade.py")]
    files = []
    for f in files_:
        with open(f, "r") as ff:
            s = ff.read().splitlines()
        if len([l for l in s if l.startswith("class ") and "(Report):" in l]) > 0:
            print("Skipping report", f)
            continue
        files.append(f)

    def _darglint_check(filename):
        import darglint
        from darglint import analysis
        from darglint.config import get_config
        from darglint.config import DocstringStyle

        config = get_config()
        # config = get_config()
        from darglint.driver import parser, get_error_report
        args = parser.parse_args()
        config.style = DocstringStyle.SPHINX
        # pass

        raise_errors_for_syntax = args.raise_syntax or False
        # for filename in files:
        # filename = student_dir_base + "/cp/project0/fruit_homework.py"
        error_report = get_error_report(
            filename,
            args.verbosity,
            raise_errors_for_syntax,
            message_template=args.message_template,
        )
        # print(error_report)

        return error_report.splitlines()




    def _pydocstyle_check(filename):
        all_errs = []
        n = 0

        o = check([filename])
        errs = [k for k in o]
        for err in errs:
            # print(f"{f}> ", err)
            all_errs.append(str(err))
        n += len(errs)
        # if n > 0:
        #     print("Total problems", n)
        return all_errs

    print("="*80)
    print("Summary of documentation style errors")
    print("=" * 80)

    n = 0
    for file in files:

        errs1 = _darglint_check(file)
        errs2 = _pydocstyle_check(file)

        if len(errs2) + len(errs1) > 0:
            print(f"{file}> errors were:")
            print(" - \n".join(errs1))
            print(" * \n".join(errs2))
        n += len(errs1) + len(errs2)
    print("Total errors", n)
    return n


def _run_student_tests(student_dir_base=None, weeks=None, projects=None, fail_if_no_projects=True,
                       fail_if_no_weeks=True):
    """
    TODO: Refactor this function to accept full module paths of tests as input, and move the cp.* specific stuff out. Possibly alternative is to automatically search for tests
    using conventions. The function should ultimately be moved to coursebox.
    """

    # still got that common module. Eventually this should be an argument (probably).
    from cp_box.common import projects_all
    from cp_box.common import weeks_all

    if projects is None:
        projects = projects_all
    else:
        projects = {k: v for k, v in projects_all.items() if k in projects}

    if weeks is None:
        weeks = weeks_all
    else:
        weeks = {k: v for k, v in weeks_all.items() if k in weeks}

    # if projects is None:
    #     from coursebox.core.info_paths import core_conf
    #     projects = list(core_conf['projects_all'].keys())

    # if weeks is None:
    #     weeks_all = core_conf['weeks_all']
    #     weeks = weeks_all
    # else:
    #     pass
    # weeks = {k: weeks_all[k] for k in weeks}

    if student_dir_base is None:
        """ Only import this sometimes to avoid messing up the paths """

        from coursebox.core.info_paths import get_paths
        paths = get_paths()
        student_dir_base = paths['02450students']

    bases = {k: projects[k]['module_public'] for k in
             projects}  # f"cp.project{k}.project{k}_tests" for k in projects if True}

    bases_weekly = [weeks[k]['module_public'] for k in weeks]  # f'cp.tests.tests_week{k:02d}' for k in weeks]

    if fail_if_no_weeks and len(bases_weekly) == 0:
        raise Exception("No weeks found. Bad configuration.")

    if fail_if_no_projects and len(bases) == 0:
        raise Exception("No projects found. Bad configuration.")

    # bases_weekly, bases = get_test_imports(weeks, projects)
    rs = {}
    for censor_files in [False, True]:
        # if not censor_files:
        #     continue
        student_dir = student_dir_base if censor_files else student_dir_base + "_complete"
        for project_id, base in bases.items():
            # student_dir = paths['02450students']
            # print(">>> Checking tests...", base, "censor?", censor_files)
            t0 = time.time()
            (p1, t1), output1 = check_py_script(student_dir, base)
            time1 = time.time() - t0
            # print(">>> Checking grade script...")
            t0 = time.time()
            if base.endswith("_tests"):
                base_grade = base[:-len("_tests")] + "_grade"
            else:
                base_grade = base + "_grade"

            (p2, t2), output2 = check_by_grade_script(student_dir, base_grade)
            time2 = time.time() - t0
            if not censor_files:
                tokens = glob.glob(student_dir + "/" + "/".join(base.split(".")[:-1]) + "/*.token")
                assert len(tokens) == 1

            rs[(base, censor_files)] = {'p1': p1, 'p2': p2, 't1': t1, 't2': t2, 'time1': time1, 'time2': time2}
            """
            These values reflect
                p1: Obtained points by project.py-script
                t1: total points by project.py-script

                p2: obtained points by project_grade.py-script
                t2: Total points by project_grade.py-script
            """
            if p1 != p2:
                print(output1)
                print("Obtained (i.e., from current code) points differ:", p1, p2)
                assert False
            if t1 != t2:
                print("Total (obtainable) points differ:", t1, t2)
                assert False

            assert (t1 > 0)
            if censor_files:
                if p1 != 0:
                    print("Ran tests with code missing. The student should get 0  points, but instead got: ", p1, "of",
                          t1)
                    print(rs[(base, censor_files)])

                assert p1 == 0
                assert p2 == 0
            else:
                if p1 != t1:
                    print(base, "Wrong number of obtained points by regular check script. Output from script is:")
                    print(p1, t1)
                    print(output1)
                    assert False
                if p2 != t2:
                    print(base, "Wrong number of obtained points by grade script. Output from grade script is:")
                    print(p2, t2)
                    print(output2)
                    assert False

        for base in bases_weekly:
            # if not weekly_tests:
            #     continue
            # print(">>> Checking tests...", base)
            t0 = time.time()
            (p1, t1), output = check_py_script(student_dir, base)
            time1 = time.time() - t0
            rs[(base, censor_files)] = {'p1': p1, 't1': t1, 'time1': time1}
            assert t1 > 0
            if censor_files:
                if p1 != 0:
                    print(p1, t1, base, "censor_files =", censor_files)
                    print(output)
                assert p1 == 0
            else:
                if p1 != t1:
                    # import warnings
                    print("=" * 50)
                    print("Check of student files when files are NOT censored.")
                    print("p1, t1 are", p1, t1)
                    print("Base is", base)
                    print("Failed check for p1 == p2")
                    print(output)
                    print(p1, t1, base, censor_files)
                    print("=" * 50)

                assert p1 == t1

    print("Main check completed")
    dd = defaultdict(list)
    for (k, mode), val in rs.items():
        # print(k, mode, val)
        dd['Test'].append(k)
        dd['censored'].append(mode)
        dd['Points obtained'].append(val['p1'])
        dd['Points total'].append(val['t1'])
        dd['Time taken'].append(int(val['time1']))

    print(tabulate.tabulate(dd, headers='keys'))

