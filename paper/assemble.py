#!/usr/bin/env python3
"""Assemble flycraft.tex = flycraft_preamble.tex + flycraft_main.tex + flycraft_notes.tex + the cited entries of
references_pool.tex (sorted by first author). Every entry in the pool was checked against Europe PMC (RESEARCH_NOTES 20d,
21, 22, 23). Then: ./build.sh"""
import re
pool = open("references_pool.tex").read()
items = dict((k, b.strip()) for b, k in re.findall(r"(\\bibitem\[[^\]]*\]\{([^}]*)\}\n.*?)(?=\n\s*\n\\bibitem|\Z)", pool, re.S))
body = open("flycraft_preamble.tex").read() + open("flycraft_main.tex").read()
notes = open("flycraft_notes.tex").read()
text = body + notes
cited = {k.strip() for grp in re.findall(r"\\cite[pt]?\{([^}]*)\}|\\citealt\{([^}]*)\}", text) for g in grp for k in g.split(",") if k.strip()}
missing = cited - set(items)
if missing:
    raise SystemExit(f"missing references: {sorted(missing)}")
def key(k):
    m = re.search(r"\]\{[^}]*\}\n([^,]+)", items[k]); return re.sub(r"[\\{}\"']", "", m.group(1) if m else k).lower() + k
bib = ("% ══════════════════════════════════════════════════════════════════════════════\n% References\n"
       "% ══════════════════════════════════════════════════════════════════════════════\n\\begin{thebibliography}{99}\n"
       "\\bibliographystyle{apalike}\n\n" + "\n\n".join(items[k] for k in sorted(cited, key=key)) + "\n\n\\end{thebibliography}\n\n\\end{document}\n")
open("flycraft.tex", "w").write(body.replace("%%NOTES", notes + "\n" + bib))
print(f"flycraft.tex: {len(cited)} references")
