// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string removeDuplicates(string s){string st;for(char c:s){if(!st.empty() && st.back()==c)st.pop_back();else st+=c;}return st;}
};
