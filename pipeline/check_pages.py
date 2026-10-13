# -*- coding: utf-8 -*-
with open('js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Scanning for page routes...")
for i, l in enumerate(lines, 1):
    s = l.strip()
    if s.startswith("'") and "':" in s:
        print(f"Line {i}: {s[:50]}")
    elif s.startswith("};"):
        print(f"Line {i}: END OF OBJECT: {s}")
