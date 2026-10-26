// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> spiralOrder(vector<vector<int>>& a){vector<int> out;int top=0,bottom=(int)a.size()-1,left=0,right=(int)a[0].size()-1;while(top<=bottom && left<=right){for(int j=left;j<=right;++j)out.push_back(a[top][j]);++top;for(int i=top;i<=bottom;++i)out.push_back(a[i][right]);--right;if(top<=bottom){for(int j=right;j>=left;--j)out.push_back(a[bottom][j]);--bottom;}if(left<=right){for(int i=bottom;i>=top;--i)out.push_back(a[i][left]);++left;}}return out;}
};
