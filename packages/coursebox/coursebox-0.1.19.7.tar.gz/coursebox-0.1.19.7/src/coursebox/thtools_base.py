import os
import platform
import subprocess
import inspect


def is_win():
    # if sys.platform()
    return platform.uname()[0].startswith("Windows")


def is_compute():
    return platform.uname()[1] == "linuxterm1"


def is_gbar():
    return False

def is_cogsys_cluster():
    return platform.uname()[0] == "Linux" and os.path.exists("/dtu-compute") and not is_compute()

def is_cluster():
    return is_compute() or is_gbar() or is_cogsys_cluster()

def get_system_name():
    if is_win():
        return "Win"
    if is_compute():
        return "thinlinc.compute.dtu.dk"
    if is_cogsys_cluster():
        return "cogys cluster"

def execute_command(command, shell=True):
    if not isinstance(command, list):
        command = [command]
    if not is_compute():
        result = subprocess.run(command, stdout=subprocess.PIPE, shell=shell)
        out = result.stdout
    else:
        out = subprocess.check_output(command, shell=shell)
    s = out.decode("utf-8")
    OK = True
    return s, OK

# def git_pull(repo_dir=None):
#     import pbs # should switch to sh when it gets windows support.
#     gitty = pbs.Command('git')
#     # args = {}
#     # if repo_dir is not None:
#     #     kwargs = {'_cwd': repo_dir}
#     # if repo_dir is not None:
#     r = gitty("pull", _cwd=repo_dir)
#     # else:
#     #     r = gitty("pull")
#     err = r.stderr
#     if err is not None and err is not "":
#         print("thtools_base.git_pull(), encountered error", err)


# def git_commit_push(repo_dir=None, commit="default commit message from thtools farm"):
#     import pbs
#     gitty = pbs.Command('git')
#     # probably it is a good idea to check the status
#
#     # repo_dir
#
#     r1 = gitty("add", ".", _cwd=repo_dir)
#     try:
#         r2 = gitty("commit", "-m'%s'"%commit, _cwd=repo_dir)
#     except pbs.ErrorReturnCode_1:
#         print("Error in git push!")
#         # print(r2.stderr)
#
#     r3 = gitty("push",  _cwd=repo_dir)


# Returns the base root of thtools
# def thtools_root_dir():
#     frame = inspect.stack()[0]
#     module = inspect.getmodule(frame[0])
#     file_in = os.path.dirname(module.__file__)
#     return file_in


def get_callstack(nback=2):
    x = inspect.currentframe()
    for j in range(nback):
        x = x.f_back
    ff = os.path.abspath(inspect.getfile(x))
    return ff, x.f_lineno, x


def caller_script_path():
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    file_in = module.__file__
    return file_in


def pprint(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pprint(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def list_dict2dict_list(lst, along_new_axis=True):
    import numpy as np
    if not lst:
        return dict()
    dc = dict()
    for key in lst[0].keys():
        dc[key] = np.stack([l[key] for l in lst if key in l], axis=0)
    if not along_new_axis:
        raise Exception("Should probably implement new axis = false")
    return dc


def partition_list(I,K,randomize=False):
    import numpy as np
    J = np.arange(len(I))
    if randomize:
        J = np.random.permutation(J)

    spl = np.array_split(J, K)
    di = []
    for chunk in spl:
        x = []
        for j in chunk:
            x.append(I[j])
        di.append(x)
    return di


def watermark_string(nback=2):

    from datetime import datetime

    tm =  datetime.now().strftime('%b-%d-%I:%M%p')
    # for line in traceback.format_stack():
    #     #     print(line.strip())
    v = inspect.stack()
    ss = []
    j = 0
    for i in range(len(v)):
        if "plot_helpers.py" in v[i].filename: continue
        ss.append( os.path.basename( v[i].filename) )
        j = j + 1
        if j > nback: break
    # from thtools import execute_command
    v, _ = execute_command("git rev-parse --short HEAD".split())

    ss.append(tm)
    return ('/'.join(ss) + f" @{v}").strip()
