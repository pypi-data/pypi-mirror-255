from tinydb import TinyDB, Query
import os
import zipfile
from tinydb import TinyDB, Query, where
import glob
import pycode_similar
import numpy as np
import matplotlib.pyplot as plt

# Update for later: Add code to copy current .zip file content to special (archived) files. Then load these files into DB later.
# Structure should be extended to include semester structure.

def plagiarism_checker(paths,info):
    db = insert_projects(paths,info)
    for repn in range(1, 4):
        d = [v for v in db if v['code'] and v['report-number'] == repn]
        if len(d) == 0:
            continue

        M = np.zeros( shape = (len(d), len(d)) )
        for i,d1 in enumerate(d):
            for j, d2 in enumerate(d):
                if i < j:
                    x = compare(d1['code'],d2['code'])
                    M[i,j] = x
            print(i)

        plt.imshow(M)
        plt.colorbar()
        plt.title("Report number %i"%repn)
        plt.show()

        aa = np.flip( np.argsort( M.ravel()),axis=0)[:10]
        ii,jj = np.unravel_index(aa, M.shape)
        for dx in range(len(aa)):
            i = ii[dx]
            j = jj[dx]
            s1 = d[i]['code'].split("\n")
            s2 = d[j]['code'].split("\n")

            bp = os.path.dirname(paths['collected_project_evaluations.xlsx']) + "/plagiarism"
            if not os.path.exists(bp):
                os.mkdir(bp)
            bp = bp + "/report_%i"%repn
            if not os.path.exists(bp):
                os.mkdir(bp)
            dout = bp + "/%.2f_%i_%i"%(M[i,j], i,j)
            if not os.path.exists(dout):
                os.mkdir(dout)

            with open(dout + "/s1.txt", 'w') as f:
                mark(f, s1, s2)

            with open(dout + "/s2.txt", 'w') as f:
                mark(f, s2, s1)

            with open(dout + "/sim.txt", 'w') as f:
                ss = [s for s in s2 if s in s1]
                f.write("\n".join(ss))

def get_toolbox_lines(paths):
    names = [("Matlab", "m"), ("Python", "py"), ("R", "R")]
    all_code = []
    dirs = ["/Tools/", "/Tools/02450Tools/",'/Scripts/']
    for (n,ex) in names:
        for d in dirs:
            tb = paths['instructor'] +"/02450Toolbox_" + n +d
            if not os.path.exists(tb):
                continue
            ls = glob.glob(tb +"/*." + ex)
            for l in ls:
                with open(l, 'r') as f:
                    s = f.read()
                    code = code2lines(s)
                    all_code += code
    return all_code


def code2lines(s):
    ls = s.split("\n")
    ls = [l.strip() for l in ls]
    ls = [l for l in ls if len(l) > 3
          and not l.startswith("# In[")
          and not l.startswith("hold")]
    return ls


def compare(s1, s2):
    s1 = set(s1.split("\n"))
    s2 = set( s2.split("\n") )
    eps = 1e-6
    x = 2*len(s1 & s2) / (len(s1) + len(s2) + eps)
    return x



def mark(f, s1, s2):
    ss = [("[!] " + s if s in s2 else s) for s in s1]
    f.write("\n".join(ss))


def get_db_DEFUNCT(paths):
    bp = os.path.dirname(paths['collected_project_evaluations.xlsx'])
    bp = os.path.dirname(bp)
    db = TinyDB(bp + '/plagiarism.json')
    return db


def insert_projects(paths,info):
    toolbox_code =  get_toolbox_lines(paths)
    db = []
    for i in range(3):
        zip_file = paths['instructor_project_evaluations'] + "/zip%i.zip"%(i+1)
        if not os.path.exists(zip_file):
            continue
        proj = {}

        zf = zipfile.ZipFile(zip_file)
        ls = zf.namelist()
        for l in ls:
            j = l.find('/')
            if j <= 0: continue
            key = l[:j]
            val = proj.get(key, [])
            val.append(l)
            proj[key] = val

        for k in proj:
            s = ""
            for f in proj[k]:
                if f.lower().endswith(".py") or f.lower().endswith(".m") or f.lower().endswith(".r"):
                    file = zf.read(f).decode('utf-8', errors='ignore')
                    s = s + "\n" + file
            group_code_ = code2lines(s)
            group_code = [l for l in group_code_ if l not in toolbox_code]
            print([len(s.split("\n")), len(group_code_), len(group_code)])
            s = "\n".join(group_code)
            v = {'semester': info['semester_id'], 'report-number': i+1, 'student_id': k, 'code': s}
            db.append(v)
    return db