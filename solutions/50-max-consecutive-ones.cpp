// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int findMaxConsecutiveOnes(vector<int>& nums){int run=0,best=0;for(int n:nums){run=n?run+1:0;best=max(best,run);}return best;}
};
