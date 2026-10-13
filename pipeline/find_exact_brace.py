# -*- coding: utf-8 -*-
with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

depth = 0
for line_no, line in enumerate(lines, 1):
    for col, ch in enumerate(line, 1):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and line_no > 80:
                print(f"Depth reached 0 at line {line_no}:{col} -> {line.strip()[:80]}")
