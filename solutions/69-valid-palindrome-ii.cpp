// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool validPalindrome(string s){auto pal=[&](int l,int r){while(l<r)if(s[l++]!=s[r--])return false;return true;};int l=0,r=(int)s.size()-1;while(l<r){if(s[l]!=s[r])return pal(l+1,r)||pal(l,r-1);++l;--r;}return true;}
};
