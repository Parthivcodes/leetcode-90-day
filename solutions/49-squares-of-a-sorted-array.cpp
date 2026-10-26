// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> sortedSquares(vector<int>& nums){int l=0,r=(int)nums.size()-1;vector<int> out(nums.size());for(int k=r;k>=0;--k){if(abs(nums[l])>abs(nums[r])){out[k]=nums[l]*nums[l];++l;}else{out[k]=nums[r]*nums[r];--r;}}return out;}
};
