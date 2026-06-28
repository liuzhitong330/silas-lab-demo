import json, re, html

d = json.load(open("experiment_results.json"))

def md_to_html(text):
    text = html.escape(text)
    text = re.sub(r'&quot;([^&]+?)&quot;', r'“\1”', text)
    lines = text.split("\n")
    out = []
    in_list = False
    for ln in lines:
        ln = ln.rstrip()
        if not ln:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        m = re.match(r'^##\s+(.*)', ln)
        if m:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<h4>{m.group(1)}</h4>")
            continue
        if ln.strip() == "---":
            if in_list:
                out.append("</ul>"); in_list = False
            out.append("<hr>")
            continue
        m = re.match(r'^[-*]\s+(.*)', ln)
        if m:
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            continue
        m = re.match(r'^\d+\.\s+(.*)', ln)
        if m:
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            continue
        if in_list:
            out.append("</ul>"); in_list = False
        out.append(f"<p>{inline_md(ln)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

def inline_md(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

# truncate exp1 to first 4 complete gap points (5th was cut by token limit)
exp1_text = d["experiment1"]["response"]
parts = exp1_text.split("## 5.")
exp1_text = parts[0].strip()

exp1_html = md_to_html(exp1_text)

turns = d["experiment2"]["turns"]
t1 = md_to_html(turns[1]["content"])
t2_raw = turns[3]["content"]
# trim incomplete trailing bullet from turn 2
t2_raw = t2_raw.split("If decay is lost")[0].rstrip()
t2 = md_to_html(t2_raw)
t3 = md_to_html(turns[5]["content"])

with open("exp1.html", "w") as f: f.write(exp1_html)
with open("exp2_t1.html", "w") as f: f.write(t1)
with open("exp2_t2.html", "w") as f: f.write(t2)
with open("exp2_t3.html", "w") as f: f.write(t3)

print("wrote exp1.html, exp2_t1.html, exp2_t2.html, exp2_t3.html")
print(f"exp1 chars: {len(exp1_html)}")
