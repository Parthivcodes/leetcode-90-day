// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool checkSubarraySum(vector<int>& nums,int k){unordered_map<int,int> first{{0,-1}};int rem=0;for(int i=0;i<(int)nums.size();++i){rem=(rem+(long long)nums[i])%k;if(first.count(rem)){if(i-first[rem]>=2)return true;}else first[rem]=i;}return false;}
};
