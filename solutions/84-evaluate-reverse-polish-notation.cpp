// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int evalRPN(vector<string>& tokens){vector<long long> s;for(auto& t:tokens){if(t=="+"||t=="-"||t=="*"||t=="/"){auto b=s.back();s.pop_back();auto a=s.back();s.pop_back();s.push_back(t=="+"?a+b:t=="-"?a-b:t=="*"?a*b:a/b);}else s.push_back(stoll(t));}return s.back();}
};
