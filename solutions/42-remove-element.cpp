// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int removeElement(vector<int>& nums,int val){int k=0;for(int x:nums)if(x!=val)nums[k++]=x;return k;}
};
