// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool isIsomorphic(string s,string t){if(s.size()!=t.size())return false;array<int,256>a{},b{};for(int i=0;i<(int)s.size();++i){unsigned char x=s[i],y=t[i];if(a[x]!=b[y])return false;a[x]=b[y]=i+1;}return true;}
};
