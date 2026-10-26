// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int longestConsecutive(vector<int>& nums){unordered_set<int>s(nums.begin(),nums.end());int best=0;for(int n:s)if(n==INT_MIN||!s.count(n-1)){int len=1,x=n;while(x!=INT_MAX && s.count(x+1)){++x;++len;}best=max(best,len);}return best;}
};
