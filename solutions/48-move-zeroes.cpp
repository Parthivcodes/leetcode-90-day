// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
void moveZeroes(vector<int>& nums){int k=0;for(int n:nums)if(n)nums[k++]=n;while(k<(int)nums.size())nums[k++]=0;}
};
