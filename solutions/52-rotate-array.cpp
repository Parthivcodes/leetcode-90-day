// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
void rotate(vector<int>& nums,int k){if(nums.empty())return;k%=nums.size();reverse(nums.begin(),nums.end());reverse(nums.begin(),nums.begin()+k);reverse(nums.begin()+k,nums.end());}
};
