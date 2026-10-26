// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool validateStackSequences(vector<int>& pushed,vector<int>& popped){vector<int>s;int j=0;for(int x:pushed){s.push_back(x);while(!s.empty() && j<(int)popped.size() && s.back()==popped[j]){s.pop_back();++j;}}return s.empty();}
};
