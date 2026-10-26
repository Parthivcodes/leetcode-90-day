// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string longestPalindrome(string s){int start=0,len=0;auto expand=[&](int l,int r){while(l>=0 && r<(int)s.size() && s[l]==s[r]){--l;++r;}if(r-l-1>len){start=l+1;len=r-l-1;}};for(int i=0;i<(int)s.size();++i){expand(i,i);expand(i,i+1);}return s.substr(start,len);}
};
