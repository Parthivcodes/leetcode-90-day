// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int maxSubArray(vector<int>& nums){int best=nums[0],run=nums[0];for(int i=1;i<(int)nums.size();++i){run=max(nums[i],run+nums[i]);best=max(best,run);}return best;}
};
