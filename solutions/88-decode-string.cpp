// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string decodeString(string s){vector<pair<string,int>> st;string cur;int n=0;for(char c:s){if(isdigit((unsigned char)c))n=n*10+c-'0';else if(c=='['){st.push_back({cur,n});cur="";n=0;}else if(c==']'){auto p=st.back();st.pop_back();string expanded=p.first;while(p.second--)expanded+=cur;cur=move(expanded);}else cur+=c;}return cur;}
};
