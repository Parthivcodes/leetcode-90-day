// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<vector<string>> groupAnagrams(vector<string>& strs){unordered_map<string,vector<string>> groups;for(auto s:strs){auto key=s;sort(key.begin(),key.end());groups[key].push_back(s);}vector<vector<string>> out;for(auto& p:groups)out.push_back(move(p.second));return out;}
};
