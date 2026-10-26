// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> nextGreaterElement(vector<int>& a,vector<int>& b){unordered_map<int,int> next;vector<int> st;for(int x:b){while(!st.empty() && st.back()<x){next[st.back()]=x;st.pop_back();}st.push_back(x);}vector<int> out;for(int x:a)out.push_back(next.count(x)?next[x]:-1);return out;}
};
