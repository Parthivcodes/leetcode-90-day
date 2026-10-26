// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> topKFrequent(vector<int>& nums,int k){unordered_map<int,int>c;for(int n:nums)++c[n];vector<vector<int>> b(nums.size()+1);for(auto p:c)b[p.second].push_back(p.first);vector<int> out;for(int i=(int)b.size()-1;i>=0 && (int)out.size()<k;--i)for(int n:b[i]){out.push_back(n);if((int)out.size()==k)break;}return out;}
};
