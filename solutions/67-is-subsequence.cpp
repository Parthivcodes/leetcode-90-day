// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool isSubsequence(string s,string t){int i=0;for(char c:t)if(i<(int)s.size() && s[i]==c)++i;return i==(int)s.size();}
};
