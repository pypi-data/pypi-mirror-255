# -*- coding: utf-8 -*-
import shutil
import os
import re
import ntpath
import glob


CDIR = os.path.dirname(os.path.realpath(__file__))
CDIR = CDIR.replace('\\','/')
os.chdir(CDIR)
OUTPUT_TEX_BASE = CDIR + "/../Latex/Exams"

nm = []
def rec_input(fname) :
    f = open(fname, "r")
    dirname = os.path.dirname(fname)    
    cc = f.readlines()
    f.close()
    for i in range(len(cc)):
        m = re.search(r'\\input{([^}]*)\}', cc[i])
        if m :
            s = m.group(0)
            fname2 = dirname + '/' + s[s.index('{')+1:s.index('}')]
            xx, file_extension = os.path.splitext(fname2)     
            if file_extension == ".tex" :
                None
            else:
                fname2 = fname2 + ".tex"
                            
            s = rec_input(fname2)
            cc[i] = s
    
    for (i,sc) in enumerate(cc) : 
        if len(sc) >= 2 and sc[-2:] == '%\n' and not (len(sc) >= 3 and sc[-3:] == "\\%\n"): cc[i] = sc[:-2]
    return ''.join(cc)


def getgroups(s2,gstart,IncludeTags = False) : 
    qs = [];
    i2 = 0
    while True :    
        t1 = '\\begin{'+gstart+'}'
        t2 = '\\end{'+gstart+'}'
        i1 = s2.find(t1,i2)
        if i1 < 0 : break
        i2 = s2.find(t2,i1)        
        
        if IncludeTags :
            d1 = 0
            d2 = len(t2)
        else:
            d1 = len(t1)
            d2 = 0
        
        s = s2[i1+d1:i2+d2] 
        refs = tagfind(s,'ref')
        refs = refs + tagfind(s,'cref')
        
        labels = tagfind(s,'label')        
        if not labels : labels = [['','']]
        
        qs.append( [s.strip(),refs,labels] )
    return qs
    
def tagfind(s,tag) :
    tags = []
    cp = re.compile(r'\\'+tag+'{(\S*)}')
    for i in cp.finditer(s) : 
        tags.append( [i.group(1), i.group(0)] ) 
    return tags
   
def process_figures(fs, PREFIX, INPUT_TEX_BASE) :
    fs = re.sub(r'\\begin{figure(}.*)', r'\\begin{figure}[H]',fs)
    fs = re.sub(r'\\begin{table(}.*)', r'\\begin{table}[H]',fs)
    rm = re.finditer(r'\\includegraphics(.*){([^}]*)}', fs)
    fig_files = [] 
    for i in rm : 
        tex_source_name = i.groups(1)[1]
        sourcefile = INPUT_TEX_BASE + tex_source_name.strip()
        tex_dest_name = PREFIX+ntpath.basename(sourcefile)                  
        fnc = glob.glob(sourcefile) + glob.glob(sourcefile+".pdf")+glob.glob(sourcefile+".png")
        
        sourcefile = fnc[0]        
        xx, file_extension = os.path.splitext(sourcefile)                
        
        destfile = OUTPUT_TEX_BASE + "/"+tex_dest_name
        if destfile.find(file_extension) < 0 : destfile = destfile+file_extension     
        
        fs = re.sub(r'\\includegraphics(.*){'+tex_source_name+'}', r'\\includegraphics\1{Exams/'+tex_dest_name+'}',fs)
        fig_files.append([sourcefile,destfile])
        
        shutil.copy(sourcefile,destfile)
    return fs
    
def process_question(PREFIX,INPUT_TEX_BASE,s2,question_number,figures_included) :
    s2 = s2 + " "
    Qs = getgroups(s2,'question')
    Ts = getgroups(s2,'table',True)
    Fs = getgroups(s2,'figure',True)
    Eqs = getgroups(s2,'equation',True)
    Als = getgroups(s2,'align',True)    
    ELEMENTS = Ts + Fs + Eqs + Als
    
    pfix = []
    eleminc = []
    q = Qs[question_number-1]
    referenced_labels = [r[0] for r in q[1]] # labels which we reference.         
    referenced_labels = list(set(referenced_labels))
    for rname in referenced_labels : 
        pfix.append(rname)       
        included_labels = [PREFIX + ll[0] for ll in q[2]]  + figures_included 
        #print included_labels
        if (PREFIX+rname) not in included_labels :                                 
            l = [e[0] for e in ELEMENTS if e[2][0][0] == rname]   
            eleminc.append(l[0])        
            
    solution = getgroups(q[0],'solution')[0][0]
    sanswer = getgroups(q[0],'answer')[0][0]
    answer = int(sanswer[1:2])
    sanswer = sanswer[3:]
    sanswer = "\\begin{enumerate}[label=\\Alph*]" + sanswer + "\\end{enumerate}"
    
    question_text = q[0][0:q[0].find('\\begin{answer}')]
    question_text = question_text.strip() + "\n" + '\n'.join(eleminc) + '\n'+sanswer.strip()
        
    question_text = process_figures(question_text,PREFIX,INPUT_TEX_BASE)
    question_text = question_text.replace("\\thecorrect\\", "ABCD"[answer-1]+" ")
    for pf in pfix:
        question_text = question_text.replace('{'+pf+'}', '{'+PREFIX+pf+'}')
        solution = solution.replace('{'+pf+'}', '{'+PREFIX+pf+'}')
        
    solution = solution.replace("\\thecorrect\\", "ABCD"[answer-1]+" ")    
    figures_included = figures_included + [PREFIX + rl for rl in referenced_labels]
    
    FOUT = OUTPUT_TEX_BASE + "/"+PREFIX[0:6]+str(question_number)+".tex"
    f = open(FOUT,'w')
    f.write(question_text.strip())
    f.close()
    
    FOUT = OUTPUT_TEX_BASE + "/"+PREFIX[0:6]+str(question_number)+"sol.tex"
    f = open(FOUT,'w')
    f.write(solution.strip())
    f.close()
    return [question_text,solution,answer,figures_included]


EXAM_INCLUDES = [[] for i in range(20)]
if True :
    # viz, hist, box, distance, sims 
    EXAM_INCLUDES[2] = ['f2011q1', 'f2013q1','f2014q1',]    
    EXAM_INCLUDES[3] = ['s2012q4','f2011q2', 'f2013q3','f2014q3','f2014q4','s2014q3',]      # PCA
    
    EXAM_INCLUDES[4] = ['f2014q10', 's2013Q18', 'f2013q18']  # Data, norms, variance, correlation, percentile.
    EXAM_INCLUDES[5] = ['f2014q8','s2013q17', 'f2013q15'] # Bayes
    EXAM_INCLUDES[6] = ['f2012q2', 'f2014Q2', 's2014q1'] # Visualization
    
    EXAM_INCLUDES[7] = ['s2013Q12', 's2014Q5', 'f2013q6', 'f2013q17','f2014q22']  # log. regression     
    EXAM_INCLUDES[8] = ['f2013q14','f2013q13','f2014q9','f2014q21'] # TREES     
    
    EXAM_INCLUDES[9] = ['f2014q27', 's2013q13', 's2013q14', 'f2013q7','f2013q16','f2014q6','f2013q25','f2014q18',]  # overfitting, fw selection
    
    EXAM_INCLUDES[10] = ['f2013q9','f2014q23','f2014q12'] # KNN methods
    EXAM_INCLUDES[11] = ['f2015q16', 'f2015q17', 'f2013q19', 'f2014q15'] # bayesian methods (classifier) + NB.    

    EXAM_INCLUDES[12] = ['s2013q26']  # bias-variance, regularization. # PROBLEMS!
    EXAM_INCLUDES[13] = ['f2013q23','f2014q5', 'f2013q12','f2014q19', ] # neural networks
    
    EXAM_INCLUDES[14] = ['f2014q24','f2014q25',]  # AUC, statistics (CIs)
    EXAM_INCLUDES[15] = ['f2014q26', 'f2013q24',] # ensemble methods boosting
    
    ## PART 3
    # Lecture 10   
    EXAM_INCLUDES[16] = ['f2013q8','f2014q20','f2014q11','f2012q12'] # kmeans, hierarchical agglom
    
    #Lecture 11
    EXAM_INCLUDES[17] = ['f2013q22','f2013q26', 'f2014q7',]     # EM/GMM
    EXAM_INCLUDES[18] = ['f2013q11', 's2013q9','f2011q27', 'f2013q20','f2013q10','f2014q13','f2014q14'] # Density estimation

    # Lecture 12    
    EXAM_INCLUDES[19] = ['s2014q11', 's2014q12'] # Association rule learning

AE = [b for e in EXAM_INCLUDES for b in e]
for e in AE : 
    if len([j for j in AE if j == e]) > 1 : 
        print(e)
    
HOMEWORK_PROBLEMS = [[] for i in range(len(EXAM_INCLUDES))]
# BKOCK 1
HOMEWORK_PROBLEMS[2]= [(3,1), (2,1), (3,2)] # basic data and PCA
HOMEWORK_PROBLEMS[3]= [(4,1), (4,2), (4,3)] # Measures of similarity and summary statistics.
HOMEWORK_PROBLEMS[4]= [(5,1), (5,2), (6,1)] # Visualization, probabilities

# BLOCK 2
HOMEWORK_PROBLEMS[5]= [(8,1), (7,1), (7,2)] # Lecture 5, reg+trees
HOMEWORK_PROBLEMS[6]= [(9,1), (9,2), (9,3)] # Lecture 6, crossval 
HOMEWORK_PROBLEMS[7]= [(11,1), (11,2), (10,1)] # Lecture 7, KNN+Bayes+Naive-bayes.
HOMEWORK_PROBLEMS[8]= [(13,1), (13,2), (13,3)] # Lecture 8, Bias/Var + Artificial NN.
HOMEWORK_PROBLEMS[9]= [(14,1), (14,2), (15,1)] # Lecture 9, classimb/AUC + Ensemble

# BLOCK 3
HOMEWORK_PROBLEMS[10]= [(16,1), (16,2), (16,3)] # Lecture 9, classimb/AUC + Ensemble

HOMEWORK_PROBLEMS[11]= [(18,1), (17,1), (17,2)] # Lecture 9, classimb/AUC + Ensemble
HOMEWORK_PROBLEMS[12]= [(19,1), (16,2), (16,3)] # Lecture 9, classimb/AUC + Ensemble

EXAM_BASE_DIR = CDIR+ "/../../Exam/"
EXAM_TEX_CONTENT = {} 

rr = '''
\\newpage \\newgeometry{left=\PLLEFT,right=\PLRIGHT,top=\PLTOP,bottom=\PLBOTTOM} \\begin{multicols}{2}
\\section*{Problems} \\addcontentsline{toc}{section}{Problems}
%s \\end{multicols}
\\restoregeometry  \\newpage '''

if __name__ == "__main__":
    for chap,ae in enumerate(EXAM_INCLUDES):
        allq = []
        allsol = []
        adex = 0
        figs_included = []
        nstrings = []
        if not ae : continue
        sas = []
        for qsin in ae : 
            sem = qsin[0]
            year = qsin[1:5]
            q = int(qsin[6:])   
            
            SEML = "Spring" if sem=="s" else "Fall"
            nstrings.append("%s %s question %i"%(SEML,year,q) )
            
            INPUT_TEX_BASE = EXAM_BASE_DIR + ("Exam %s %s/latex/"%(SEML,year))
            if not os.path.isdir(INPUT_TEX_BASE) :
                INPUT_TEX_BASE = EXAM_BASE_DIR + ("Exam %s %s/02450Exam%s%s/latex/"%(SEML,year,SEML,year))
                        
            exam_tex_file = INPUT_TEX_BASE + ("02450ex_%s%s_book.tex"%(SEML,year))
            
            if not os.path.isfile(exam_tex_file) :
                exam_tex_file = INPUT_TEX_BASE + ("02450ex_%s%s.tex"%(SEML,year))
            
            FIG_PREFIX = qsin[0:6] + "c"+str(chap)
            
            if not EXAM_TEX_CONTENT.has_key(FIG_PREFIX) : 
                EXAM_TEX_CONTENT[FIG_PREFIX] = rec_input(exam_tex_file)
            s2 = EXAM_TEX_CONTENT[FIG_PREFIX]
            
            [qtext,qsol,adex,fi] = process_question(FIG_PREFIX,INPUT_TEX_BASE,s2,q,figs_included)
            figs_included = figs_included + fi
            sa = 'ABCD'[adex-1]
            sas.append(sa)
            # write joint solution file and joint answer thingy
        
        cq = ['\\begin{prob}\\label{c%iprob%i}\\textbf{%s:} \n \\input{Exams/%s}\\end{prob}'%(chap,qn+1,nstrings[qn],qs) for (qn,qs) in enumerate(ae)]
        cq = '\n'.join(cq)
        
        cs = ['\\begin{sol}{c%iprob%i}\\textbf{The correct answer is %s:} \\input{Exams/%ssol}\\end{sol}'%(chap,qn+1,sas[qn],qs) for (qn,qs) in enumerate(ae)]
        cs = '\n'.join(cs)
        
        ss = rr%cq       
        FOUT = OUTPUT_TEX_BASE + "/c%iprob.tex"%chap
        f = open(FOUT,'w')
        f.write(ss)
        f.close()

        FOUT = OUTPUT_TEX_BASE + "/c%isol.tex"%chap
        f = open(FOUT,'w')
        f.write(cs)
        f.close()
    print("All Done")    