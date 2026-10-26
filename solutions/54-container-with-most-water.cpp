// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int maxArea(vector<int>& h){int l=0,r=(int)h.size()-1,ans=0;while(l<r){ans=max(ans,(r-l)*min(h[l],h[r]));if(h[l]<h[r])++l;else --r;}return ans;}
};
