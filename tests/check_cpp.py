"""Compile every solution and run a sample/edge check for each (not LeetCode judging)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
plan = json.loads((ROOT/'roadmap.json').read_text())
cases = {}
for line in (ROOT/'tests/cases.txt').read_text().splitlines():
    key, code = line.split('|',1)
    cases[int(key)] = code
assert set(cases) == set(range(1,91)), 'Every problem requires a test.'
compiler = shutil.which(os.environ.get('CXX','g++'))
if not compiler:
    raise SystemExit('C++ compiler unavailable. Run this check on the Ubuntu GitHub Actions runner.')
header = '''#include <bits/stdc++.h>
using namespace std;
struct ListNode {int val;ListNode* next;ListNode(int v=0,ListNode* n=nullptr):val(v),next(n){}};
ListNode* make(initializer_list<int> a){ListNode d;auto p=&d;for(int n:a){p->next=new ListNode(n);p=p->next;}return d.next;}
vector<int> vals(ListNode* h){vector<int>a;while(h){assert(a.size()<1000);a.push_back(h->val);h=h->next;}return a;}
'''
units = [header]
for p in plan:
    body = (ROOT/p['solution']).read_text()
    body = '\n'.join(line for line in body.splitlines() if not line.startswith('#include'))
    instance = '' if p['day'] in (77,78,82,83) else 'Solution s;'
    units.append(f"namespace day{p['day']} {{\n{body}\nvoid test(){{{instance}{cases[p['day']]}}}\n}}")
units.append('int main(){' + ''.join(f"day{p['day']}::test();" for p in plan) + 'cout << "90 C++ solution checks passed\\n";}')
with tempfile.TemporaryDirectory() as folder:
    source = Path(folder)/'all.cpp'
    binary = Path(folder)/('checks.exe' if os.name=='nt' else 'checks')
    source.write_text('\n'.join(units))
    subprocess.run([compiler,'-std=c++17','-O1','-Wall','-Wextra',str(source),'-o',str(binary)],check=True,timeout=180)
    subprocess.run([str(binary)],check=True,timeout=30)
