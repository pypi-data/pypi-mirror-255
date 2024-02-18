import os
import shutil
import glob

from jinjafy import jinjafy_template
from slider import latexmk
from coursebox.thtools_base import execute_command
from slider.slide import slide_no_by_text, recursive_tex_apply
from slider.legacy_importer import slide_to_image


def lecture_question_compiler(paths, info, lecture_texfile):

    lecture_latex_path = os.path.dirname(lecture_texfile)
    lecture_pdffile = lecture_texfile[:-3] + "pdf"
    # nosvg = lecture_pdffile[:-4] + "_NO_SVGS.pdf"
    qpath = lecture_latex_path +"/questions"
    if not os.path.exists(qpath):
        os.mkdir(qpath)
    all_questions_csv = []
    png_out = None
    for fn in glob.glob(qpath + "/*_base_*.tex"):
        print(fn)
        with open(fn, 'r') as f:
            s = f.read()

        qstart = s.find('\\begin{question}') + len("\\begin{question}")
        qend = s.find('\\begin{solution}') #+ len('\\begin{solution}')
        sstart = qend + len('\\begin{solution}')
        send = s.find('\\end{solution}')

        qes = s[qstart:qend]
        sol = s[sstart:send]

        a,b,c = os.path.basename(fn).split("_")
        question_no = c.split(".")[0]
        fout_q = qpath +"/"+a + "_" + c
        fout_sol = qpath +"/"+ a + "_" + question_no+ "_sol.tex"

        data = {'text': qes}
        jinjafy_template(data=data, file_in=lecture_latex_path +"/questions/question_partial.tex", file_out=fout_q)
        fout_q_pdf = qpath + "/" + latexmk(fout_q, cleanup=True)
        execute_command(["pdfcrop", fout_q_pdf, fout_q_pdf])

        # get "nice" .png file (or fallback)
        tex = recursive_tex_apply(lecture_texfile)
        tex = "\n".join([tex[k] for k in tex])
        qtex = os.path.basename(fout_q)
        dex = tex.find(qtex[:-4])


        if dex >= 0:
            j = tex[:dex].rfind("\\begin{frame}")
            ol = tex[j:dex]
            j1 = ol.find("\\osvg{")
            j2 = ol.find("}",j1)

            ol = ol[j1 + 6:j2]
            # n = slide_no_by_text(nosvg, ol)
            print(lecture_pdffile, ol)
            n = slide_no_by_text(lecture_pdffile, ol)
            if n < 0:
                print("Question compiler: Question missing osvg label?")
                dex = -1
            else:
                png_out = fout_q_pdf[:-4] + ".png"
                print("png_out", png_out)
                slide_to_image(lecture_pdffile, png_out, page_to_take=n)
        if dex < 0:
            execute_command(["pdftocairo", fout_q_pdf, fout_q_pdf[:-4], "-png"])
            ls = glob.glob( fout_q_pdf[:-4] +"-*.png")
            if len(ls) > 1:
                print("Hacky, two files exist (bad/old png conversaion code", ls)
                l2 = glob.glob(fout_q_pdf[:-4] + "-000*.png")[0]
                os.remove(l2)
                ls = glob.glob(fout_q_pdf[:-4] + "-*.png")


            # print(ls)
            if len(ls) != 1:
                raise Exception("Multiple question png files found", ls)
            png_out = ls[0] if ls else None
            print("png_out b", png_out)

        qdir = paths['pdf_out'] +"/quiz"
        if not os.path.exists(qdir):
            os.mkdir(qdir)
        print("png_out c", png_out)
        if png_out:
            # a + "_" + c[:-4] + ".png"
            # png_out2 = os.path.basename(lecture_texfile)[:-4] + "_"+os.path.basename(png_out)
            png_out2 = os.path.basename(lecture_texfile)[:-4] + "_" + a + "_" + c[:-4] + ".png"
            print("Copying quiz png> " + png_out2)
            print("png_out d", png_out)
            shutil.copyfile(png_out, qdir+"/" + png_out2)

        data = {'text': sol}
        jinjafy_template(data=data, file_in=lecture_latex_path +"/questions/question_partial.tex", file_out=fout_sol)
        fout_sol_pdf = qpath + "/" + latexmk(fout_sol)
        execute_command(["pdfcrop", fout_sol_pdf, fout_sol_pdf])

        # Now make the cvx fileÆ
        try:
            ans = [l for l in qes.splitlines() if not l.strip().startswith("%") and r"\begin{answer}" in l].pop()
        except IndexError as e:
            print("Bad list pop", fn)
            print(qes)
            print(e)
        correct = int( ans[ans.rfind("[")+1:ans.rfind("]")] )
        answers = []

        for j in range(5):
            lbl = ([v + " is correct" for v in "ABCD"] + ["E: Don't know"] )[j]
            points = "100" if j+1 == correct else "0"
            answers.append( f"Option,{points},{lbl},," )

        if png_out is not None:
            l, n = os.path.basename(lecture_texfile[:-4]).split("_")
            n = "0"+n if len(n) < 2 else n
            csv_out = qdir + "/" + png_out2[:-3] + "csv"
            lines = [ "NewQuestion,MC,"
                      f"ID,{png_out2[:-4]}",
                      f"Title,{l} {n}: Quiz {question_no}",
                        f"QuestionText,Select correct option or Don't know,",
                        f"Points,1,",
                        f"Difficulty,1,",
                        f"Image,images/quiz/{png_out2}"] +\
                        answers
                        # f"Hint,This is the hint text,,,",
                        # f"Feedback,This is the feedback text,,,",
                # ]
            s = "\n".join(lines)
            all_questions_csv.append(s)
        print("Compiled question: %s"%(fout_q_pdf,))

    if png_out:
        s = "\n\n".join(all_questions_csv)
        csv_base = qdir + "/dtulearn_csv"
        if not os.path.isdir(csv_base):
            os.mkdir(csv_base)
        with open(csv_base + "/" + os.path.basename(lecture_pdffile)[:-3] + "csv", 'w') as f:
            f.write(s)

        """ 
        //MULTIPLE CHOICE QUESTION TYPE,,
        //Options must include text in column3,,
        NewQuestion,MC,
        ID,LECTURE05_question1
        Title,Lecture 01: Quiz 1
        QuestionText,This is thdfsklad fjasdklj fasdkl j text for MC1,
        Points,1,
        Difficulty,1,
        Image,images/quizzes/Lecture_5_question_1.png
        Option,100,This is the asdfsd correct answer,,This is feed sda fsdf asdf back for option 1
        Option,0,This is asdfsadfsdfsadf answer 1,,This is feedback for option 2
        Option,0,This is incorrect answer 2,,This is feedback for option 3
        Option,0,This is partially correct,,This is feedback for option 4
        Hint,This is the hint text,,,
        Feedback,This is the feedback text,,,
        """
        # =======
        print("Compiled question: %s"%(fout_q_pdf,))


        """
        //MULTIPLE CHOICE QUESTION TYPE,,
        //Options must include text in column3,,
        NewQuestion,MC,
        ID,LECTURE05_question1
        Title,Lecture 01: Quiz 1
        QuestionText,This is thdfsklad fjasdklj fasdkl j text for MC1,
        Points,1,
        Difficulty,1,
        Image,images/quizzes/Lecture_5_question_1.png
        Option,100,This is the asdfsd correct answer,,This is feed sda fsdf asdf back for option 1
        Option,0,This is asdfsadfsdfsadf answer 1,,This is feedback for option 2
        Option,0,This is incorrect answer 2,,This is feedback for option 3
        Option,0,This is partially correct,,This is feedback for option 4
        Hint,This is the hint text,,,
        Feedback,This is the feedback text,,,
        """
