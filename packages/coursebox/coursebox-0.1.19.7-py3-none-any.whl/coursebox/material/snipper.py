# from snipper.load_citations import find_tex_cite
# import os
# import functools
# from jinjafy import execute_command
# import textwrap
# import re
#
# COMMENT = '"""'
# def indent(l):
#     v = len(l) - len(l.lstrip())
#     return l[:v]
#
# def fix_r(lines):
#     for i,l in enumerate(lines):
#         if "#!r" in l:
#             lines[i] = indent(l) + l[l.find("#!r") + 3:].lstrip()
#     return lines
#
# def gcoms(s):
#     coms = []
#     while True:
#         i = s.find(COMMENT)
#         if i >= 0:
#             j = s.find(COMMENT, i+len(COMMENT))+3
#         else:
#             break
#         if j < 0:
#             raise Exception("comment tag not closed")
#         coms.append(s[i:j])
#         s = s[:i] + s[j:]
#         if len(coms) > 10:
#             print("long comments in file", i)
#     return coms, s
#
# def strip_tag(lines, tag):
#     lines2 = []
#     for l in lines:
#         dx = l.find(tag)
#         if dx > 0:
#             l = l[:dx]
#             if len(l.strip()) == 0:
#                 l = None
#         if l is not None:
#             lines2.append(l)
#     return lines2
#
# def block_process(lines, tag, block_fun):
#     i = 0
#     didfind = False
#     lines2 = []
#     block_out = []
#     cutout = []
#     while i < len(lines):
#         l = lines[i]
#         dx = l.find(tag)
#         if dx >= 0:
#             if l.find(tag, dx+1) > 0:
#                 j = i
#             else:
#                 for j in range(i + 1, 10000):
#                     if j >= len(lines):
#                         print("\n".join(lines))
#                         print("very bad end-line j while fixing tag", tag)
#                         raise Exception("Bad line while fixing", tag)
#                     if lines[j].find(tag) >= 0:
#                         break
#
#             pbody = lines[i:j+1]
#             if i == j:
#                 start_extra = lines[j][dx:lines[j].rfind(tag)].strip()
#                 end_extra = lines[j][lines[j].rfind(tag) + len(tag):].strip()
#             else:
#                 start_extra = lines[i][dx:].strip()
#                 end_extra = lines[j][lines[j].rfind(tag) + len(tag):].strip()
#
#             cutout.append(pbody)
#             tmp_ = start_extra.split("=")
#             arg = None if len(tmp_) <= 1 else tmp_[1].split(" ")[0]
#             start_extra = ' '.join(start_extra.split(" ")[1:] )
#
#             pbody[0] = pbody[0][:dx]
#             if j > i:
#                 pbody[-1] = pbody[-1][:pbody[-1].find(tag)]
#
#             nlines, extra = block_fun(lines=pbody, start_extra=start_extra, end_extra=end_extra, art=arg, head=lines[:i], tail=lines[j+1:])
#             lines2 += nlines
#             block_out.append(extra)
#             i = j+1
#             didfind = True
#             if "!b" in end_extra:
#                 assert(False)
#         else:
#             lines2.append(l)
#             i += 1
#
#     return lines2, didfind, block_out, cutout
#
#
# def rem_nonprintable_ctrl_chars(txt):
#     """Remove non_printable ascii control characters """
#     #Removes the ascii escape chars
#     try:
#         txt = re.sub(r'[^\x20-\x7E|\x09-\x0A]','', txt)
#         # remove non-ascii characters
#         txt = repr(txt).decode('unicode_escape').encode('ascii','ignore')[1:-1]
#     except Exception as exception:
#         print(exception)
#     return txt
#
#
# def run_i(lines, file, output):
#     extra = dict(python=None, output=output, evaluated_lines=0)
#     def block_fun(lines, start_extra, end_extra, art, head="", tail="", output=None, extra=None):
#         outf = output + ("_" + art if art is not None and len(art) > 0 else "") + ".shell"
#         lines = full_strip(lines)
#         s = "\n".join(lines)
#         s.replace("...", "..") # passive-aggressively truncate ... because of #issues.
#         lines = textwrap.dedent(s).strip().splitlines()
#
#         if extra['python'] is None:
#             # import thtools
#
#             if os.name == 'nt':
#                 import wexpect as we
#             else:
#                 import pexpect as we
#             an = we.spawn("python", encoding="utf-8", timeout=20)
#             an.expect([">>>"])
#             extra['python'] = an
#
#         analyzer = extra['python']
#         def rsession(analyzer, lines):
#             l2 = []
#             for i, l in enumerate(lines):
#                 l2.append(l)
#                 if l.startswith(" ") and i < len(lines)-1 and not lines[i+1].startswith(" "):
#                     if not lines[i+1].strip().startswith("else:") and not lines[i+1].strip().startswith("elif") :
#                         l2.append("\n")
#
#             lines = l2
#             alines = []
#
#             # indented = False
#             in_dot_mode = False
#             if len(lines[-1]) > 0 and (lines[-1].startswith(" ") or lines[-1].startswith("\t")):
#                 lines += [""]
#
#             for i, word in enumerate(lines):
#                 analyzer.sendline(word)
#                 before = ""
#                 while True:
#                     analyzer.expect_exact([">>>", "..."])
#                     before += analyzer.before
#                     if analyzer.before.endswith("\n"):
#                         break
#                     else:
#                         before += analyzer.after
#
#                 dotmode = analyzer.after == "..."
#                 if 'dir(s)' in word:
#                     pass
#                 if 'help(s.find)' in word:
#                     pass
#                 if dotmode:
#                     # alines.append("..." + word)
#                     alines.append(">>>" + analyzer.before.rstrip() if not in_dot_mode else "..." + analyzer.before.rstrip())
#                     in_dot_mode = True
#                     # if i < len(lines) - 1 and not lines[i + 1].startswith(" "):
#                     #     analyzer.sendline("\n")  # going out of indentation mode .
#                     #     analyzer.expect_exact([">>>", "..."])
#                     #     alines.append("..." + analyzer.after.rstrip())
#                     #     pass
#                 else:
#                     alines.append( ("..." if in_dot_mode else ">>>") + analyzer.before.rstrip())
#                     in_dot_mode = False
#             return alines
#
#         for l in (head[extra['evaluated_lines']:] + ["\n"]):
#             analyzer.sendline(l)
#             analyzer.expect_exact([">>>", "..."])
#
#
#         alines = rsession(analyzer, lines)
#         extra['evaluated_lines'] += len(head) + len(lines)
#         lines = alines
#         return lines, [outf, lines]
#     try:
#         a,b,c,_ = block_process(lines, tag="#!i", block_fun=functools.partial(block_fun, output=output, extra=extra))
#         if extra['python'] is not None:
#             extra['python'].close()
#
#         if len(c)>0:
#             kvs= { v[0] for v in c}
#             for outf in kvs:
#                 out = "\n".join( ["\n".join(v[1]) for v in c if v[0] == outf] )
#                 out = out.replace("\r", "")
#
#                 with open(outf, 'w') as f:
#                     f.write(out)
#
#     except Exception as e:
#         print("lines are")
#         print("\n".join(lines))
#         print("Bad thing in #!i command in file", file)
#         raise e
#     return lines
#
# def save_s(lines, file, output, include_path_base=None): # save file snips to disk
#     def block_fun(lines, start_extra, end_extra, art, output, **kwargs):
#         outf = output + ("_" + art if art is not None and len(art) > 0 else "") + ".py"
#         lines = full_strip(lines)
#         return lines, [outf, lines]
#     try:
#         a,b,c,_ = block_process(lines, tag="#!s", block_fun=functools.partial(block_fun, output=output))
#
#         if len(c)>0:
#             kvs= { v[0] for v in c}
#             for outf in kvs:
#
#                 out = "\n".join([f"# {include_path_base}"]  + ["\n".join(v[1]) for v in c if v[0] == outf] )
#
#                 with open(outf, 'w') as f:
#                     f.write(out)
#
#     except Exception as e:
#         print("lines are")
#         print("\n".join(lines))
#         print("Bad thing in #!s command in file", file)
#         raise e
#     return lines
#
# def run_o(lines, file, output):
#     def block_fun(lines, start_extra, end_extra, art, output, **kwargs):
#         id = indent(lines[0])
#         outf = output + ("_" + art if art is not None else "") + ".txt"
#         l2 = []
#         l2 += [id + "import sys", id + f"sys.stdout = open('{outf}', 'w')"]
#         l2 += lines
#         # l2 += [indent(lines[-1]) + "sys.stdout.close()"]
#         l2 += [indent(lines[-1]) + "sys.stdout = sys.__stdout__"]
#         return l2, None
#     try:
#         lines2, didfind, extra, _ = block_process(lines, tag="#!o", block_fun=functools.partial(block_fun, output=output) )
#     except Exception as e:
#         print("Bad file: ", file)
#         print("I was cutting the #!o tag")
#         print("\n".join( lines) )
#         raise(e)
#
#     if didfind:
#         fp, ex = os.path.splitext(file)
#         file_run = fp + "_RUN_OUTPUT_CAPTURE" +ex
#         if os.path.exists(file_run):
#             print("file found mumble...")
#         else:
#             with open(file_run, 'w', encoding="utf-8") as f:
#                 f.write("\n".join(lines2) )
#             cmd = "python " + file_run
#
#             s,ok = execute_command(cmd.split(), shell=True)
#             print(s)
#             os.remove(file_run)
#
# def fix_f(lines, debug):
#     lines2 = []
#     i = 0
#     while i < len(lines):
#         l = lines[i]
#         dx = l.find("#!f")
#         if dx >= 0:
#             l_head = l[dx+3:].strip()
#             l = l[:dx]
#             lines2.append(l)
#             id = indent(lines[i+1])
#             for j in range(i+1, 10000):
#                 jid = len( indent(lines[j]) )
#                 if  j+1 == len(lines) or ( jid < len(id) and len(lines[j].strip() ) > 0):
#                     break
#
#             if len(lines[j-1].strip()) == 0:
#                 j = j - 1
#             funbody = "\n".join( lines[i+1:j] )
#             if i == j:
#                 raise Exception("Empty function body")
#             i = j
#             comments, funrem = gcoms(funbody)
#             comments = [id + c for c in comments]
#             if len(comments) > 0:
#                 lines2 += comments[0].split("\n")
#             lines2 += [id+"#!b"]
#             lines2 += (id+funrem.strip()).split("\n")
#             errm = l_head if len(l_head) > 0 else "Implement function body"
#             lines2 += [f'{id}#!b {errm}']
#
#         else:
#             lines2.append(l)
#             i += 1
#     return lines2
#
# def fix_b2(lines):
#     stats = {'n': 0}
#     def block_fun(lines, start_extra, end_extra, art, stats=None, **kwargs):
#         id = indent(lines[0])
#         lines = lines[1:] if len(lines[0].strip()) == 0 else lines
#         lines = lines[:-1] if len(lines[-1].strip()) == 0 else lines
#         cc = len(lines)
#         ee = end_extra.strip()
#         if len(ee) >= 2 and ee[0] == '"':
#             ee = ee[1:-1]
#         start_extra = start_extra.strip()
#         l2 = ([id+start_extra] if len(start_extra) > 0 else []) + [id + f"# TODO: {cc} lines missing.",
#                                          id+f'raise NotImplementedError("{ee}")']
#         # if "\n".join(l2).find("l=l")>0:
#         #     a = 2342342
#         stats['n'] += cc
#         return l2, cc
#     lines2, _, _, cutout = block_process(lines, tag="#!b", block_fun=functools.partial(block_fun, stats=stats))
#     return lines2, stats['n'], cutout
#
#
# def fix_references(lines, info, strict=True):
#     for cmd in info['new_references']:
#         lines = fix_single_reference(lines, cmd, info['new_references'][cmd], strict=strict)
#     return lines
#
# def fix_single_reference(lines, cmd, aux, strict=True):
#     references = aux
#     s = "\n".join(lines)
#     i = 0
#     while True:
#         (i, j), reference, txt = find_tex_cite(s, start=i, key=cmd)
#         if i < 0:
#             break
#         if reference not in references:
#             er = "cref label not found for label: " + reference
#             if strict:
#                 raise IndexError(er)
#             else:
#                 print(er)
#                 continue
#         r = references[reference]
#         rtxt = r['pyref']
#         s = s[:i] + rtxt + s[j + 1:]
#         i = i + len(rtxt)
#         print(cmd, rtxt)
#
#     lines = s.splitlines(keepends=False)
#     return lines
#
#
# def fix_cite(lines, info, strict=True):
#     lines = fix_references(lines, info, strict=strict)
#
#     s = "\n".join(lines)
#     i = 0
#     all_refs = []
#     while True:
#         (i, j), reference, txt = find_tex_cite(s, start=i, key="\\cite")
#         if i < 0:
#             break
#         if reference not in info['references']:
#             raise IndexError("no such reference: " + reference)
#         ref = info['references'][reference]
#         label = ref['label']
#         rtxt = f"({label}" + (", "+txt if txt is not None else "") + ")"
#         r = ref['plain']
#         if r not in all_refs:
#             all_refs.append(r)
#         s = s[:i] + rtxt + s[j+1:]
#         i = i + len(rtxt)
#
#     cpr = "{{copyright}}"
#     if not s.startswith(COMMENT):
#         s = f"{COMMENT}\n{cpr}\n{COMMENT}\n" + s
#     if len(all_refs) > 0:
#         i = s.find(COMMENT, s.find(COMMENT)+1)
#         all_refs = ["  " + r for r in all_refs]
#         s = s[:i] + "\nReferences:\n" + "\n".join(all_refs) + "\n" + s[i:]
#
#     s = s.replace(cpr, info['code_copyright'])
#     return s
#
# def full_strip(lines, tags=None):
#     if tags is None:
#         tags = ["#!s", "#!o", "#!f", "#!b"]
#     for t in tags:
#         lines = strip_tag(lines, t)
#     return lines
#
# def censor_file(file, info, paths, run_files=True, run_out_dirs=None, cut_files=True, solution_list=None,
#                 censor_files=True,
#                 include_path_base=None,
#                 strict=True):
#     dbug = False
#     with open(file, 'r', encoding='utf8') as f:
#         s = f.read()
#         s = s.lstrip()
#         lines = s.split("\n")
#         for k, l in enumerate(lines):
#             if l.find(" # !") > 0:
#                 print(f"{file}:{k}> bad snipper tag, fixing")
#             lines[k] = l.replace("# !", "#!")
#
#         try:
#             s = fix_cite(lines, info, strict=strict)
#             lines = s.split("\n")
#         except IndexError as e:
#             print(e)
#             print("Fuckup in file, cite/reference tag not found!>", file)
#             raise e
#
#         if run_files or cut_files:
#             ofiles = []
#             for rod in run_out_dirs:
#                 if not os.path.isdir(rod):
#                     os.mkdir(rod)
#                 ofiles.append(os.path.join(rod, os.path.basename(file).split(".")[0]) )
#             ofiles[0] = ofiles[0].replace("\\", "/")
#
#             if run_files:
#                 run_o(lines, file=file, output=ofiles[0])
#                 run_i(lines, file=file, output=ofiles[0])
#             if cut_files:
#                 save_s(lines, file=file, output=ofiles[0], include_path_base=include_path_base)  # save file snips to disk
#         lines = full_strip(lines, ["#!s", "#!o", '#!i'])
#
#         # lines = fix_c(lines)
#         if censor_files:
#             lines = fix_f(lines, dbug)
#             lines, nB, cut = fix_b2(lines)
#         else:
#             nB = 0
#         lines = fix_r(lines)
#
#         if censor_files and len(cut) > 0 and solution_list is not None:
#             fname = file.__str__()
#             i = fname.find("irlc")
#             wk = fname[i+5:fname.find("\\", i+6)]
#             sp = paths['02450students'] +"/solutions/"
#             if not os.path.exists(sp):
#                 os.mkdir(sp)
#             sp = sp + wk
#             if not os.path.exists(sp):
#                 os.mkdir(sp)
#
#             stext = ["\n".join(lines) for lines in cut]
#             for i,sol in enumerate(stext):
#                 sout = sp + f"/{os.path.basename(fname)[:-3]}_TODO_{i+1}.py"
#                 wsol = any([True for s in solution_list if os.path.basename(sout).startswith(s)])
#                 print(sout, "(published)" if wsol else "")
#                 if wsol:
#                     with open(sout, "w") as f:
#                         f.write(sol)
#
#         if len(lines[-1])>0:
#             lines.append("")
#         s2 = "\n".join(lines)
#
#     with open(file, 'w', encoding='utf-8') as f:
#         f.write(s2)
#     return nB
# # lines: 294, 399, 420, 270