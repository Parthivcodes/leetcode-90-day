// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int countSubstrings(string s){int count=0;for(int center=0;center<2*(int)s.size()-1;++center){int l=center/2,r=l+center%2;while(l>=0 && r<(int)s.size() && s[l--]==s[r++])++count;}return count;}
};
