// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool wordPattern(string pattern,string s){istringstream in(s);string w;unordered_map<char,string> m;unordered_set<string> used;for(char c:pattern){if(!(in>>w))return false;if(m.count(c)){if(m[c]!=w)return false;}else{if(!used.insert(w).second)return false;m[c]=w;}}return !(in>>w);}
};
