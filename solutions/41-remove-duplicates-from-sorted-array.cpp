// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int removeDuplicates(vector<int>& nums){int k=0;for(int x:nums)if(k==0||x!=nums[k-1])nums[k++]=x;return k;}
};
