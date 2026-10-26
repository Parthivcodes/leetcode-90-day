// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool checkInclusion(string a,string b){if(a.size()>b.size())return false;array<int,26>x{},y{};for(char c:a)++x[c-'a'];for(int i=0;i<(int)b.size();++i){++y[b[i]-'a'];if(i>=(int)a.size())--y[b[i-a.size()]-'a'];if(x==y)return true;}return false;}
};
