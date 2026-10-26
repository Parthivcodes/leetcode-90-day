// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool isValidSudoku(vector<vector<char>>& b){bool r[9][9]{},c[9][9]{},box[9][9]{};for(int i=0;i<9;++i)for(int j=0;j<9;++j)if(b[i][j]!='.'){int n=b[i][j]-'1',k=i/3*3+j/3;if(r[i][n]||c[j][n]||box[k][n])return false;r[i][n]=c[j][n]=box[k][n]=true;}return true;}
};
