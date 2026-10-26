// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int fourSumCount(vector<int>& a,vector<int>& b,vector<int>& c,vector<int>& d){unordered_map<int,int> m;for(int x:a)for(int y:b)++m[x+y];int ans=0;for(int x:c)for(int y:d)ans+=m[-x-y];return ans;}
};
