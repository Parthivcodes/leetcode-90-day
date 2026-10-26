// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
void setZeroes(vector<vector<int>>& a){int m=a.size(),n=a[0].size();bool row=false,col=false;for(int j=0;j<n;++j)row|=a[0][j]==0;for(int i=0;i<m;++i)col|=a[i][0]==0;for(int i=1;i<m;++i)for(int j=1;j<n;++j)if(!a[i][j])a[i][0]=a[0][j]=0;for(int i=1;i<m;++i)for(int j=1;j<n;++j)if(!a[i][0]||!a[0][j])a[i][j]=0;if(row)fill(a[0].begin(),a[0].end(),0);if(col)for(auto& r:a)r[0]=0;}
};
