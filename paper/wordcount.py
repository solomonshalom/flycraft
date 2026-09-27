#!/usr/bin/env python3
"""Word counts of the paper's parts (main text = abstract to conclusion, without figures, tables and LaTeX commands)."""
import re, sys
t = open(sys.argv[1] if len(sys.argv) > 1 else "flycraft.tex").read()
def words(s):
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{(figure|table)\}", "", s, flags=re.S)
    s = re.sub(r"\\(cite[pt]?|citealt|Cref|cref|label|ref|note|url|href)\{[^}]*\}(\{[^}]*\})?", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s); s = re.sub(r"[{}$\\~]", " ", s)
    return len([w for w in s.split() if re.search(r"[A-Za-z0-9]", w)])
abstract = t.split("\\begin{abstract}")[1].split("\\end{abstract}")[0]
main = t.split("\\section{Introduction}")[1].split("is an independent researcher")[0]
notes = t.split("\\section*{Notes}")[1].split("\\input{tables_arena.tex}")[0] if "\\section*{Notes}" in t else ""
guide = t.split("\\section{A Fly Brain for Readers Without Biology}")[1].split("\\section{The Experiment}")[0]
print(f"abstract {words(abstract)}  main text {words(main)} (of which the lay guide {words(guide)})  notes {words(notes)}")
