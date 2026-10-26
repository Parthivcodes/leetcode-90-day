// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int calPoints(vector<string>& ops){vector<int> st;for(auto& s:ops){if(s=="C")st.pop_back();else if(s=="D")st.push_back(st.back()*2);else if(s=="+")st.push_back(st.back()+st[st.size()-2]);else st.push_back(stoi(s));}return accumulate(st.begin(),st.end(),0);}
};
