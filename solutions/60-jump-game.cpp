// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool canJump(vector<int>& nums){int far=0;for(int i=0;i<(int)nums.size();++i){if(i>far)return false;far=max(far,i+nums[i]);}return true;}
};
