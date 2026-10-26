// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> intersection(vector<int>& a,vector<int>& b){unordered_set<int> s(a.begin(),a.end());vector<int> out;for(int x:b)if(s.erase(x))out.push_back(x);return out;}
};
