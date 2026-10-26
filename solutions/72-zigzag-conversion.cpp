// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string convert(string s,int numRows){if(numRows==1||numRows>=(int)s.size())return s;vector<string>r(numRows);int i=0,step=1;for(char c:s){r[i]+=c;if(i==0)step=1;if(i==numRows-1)step=-1;i+=step;}string out;for(auto& row:r)out+=row;return out;}
};
