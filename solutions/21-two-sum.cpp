// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> twoSum(vector<int>& nums,int target){unordered_map<int,int> m;for(int i=0;i<(int)nums.size();++i){auto p=m.find(target-nums[i]);if(p!=m.end())return {p->second,i};m[nums[i]]=i;}return {};}
};
