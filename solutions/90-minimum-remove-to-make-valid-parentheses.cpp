// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string minRemoveToMakeValid(string s){vector<int> st;vector<bool> drop(s.size());for(int i=0;i<(int)s.size();++i){if(s[i]=='(')st.push_back(i);else if(s[i]==')'){if(st.empty())drop[i]=true;else st.pop_back();}}for(int i:st)drop[i]=true;string out;for(int i=0;i<(int)s.size();++i)if(!drop[i])out+=s[i];return out;}
};
