// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string longestCommonPrefix(vector<string>& strs){if(strs.empty())return "";string p=strs[0];for(auto& s:strs){int k=0;while(k<(int)p.size() && k<(int)s.size() && p[k]==s[k])++k;p.resize(k);}return p;}
};
