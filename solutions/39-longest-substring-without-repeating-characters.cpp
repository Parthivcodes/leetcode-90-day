// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int lengthOfLongestSubstring(string s){array<int,256> last;last.fill(-1);int left=0,best=0;for(int i=0;i<(int)s.size();++i){unsigned char c=s[i];left=max(left,last[c]+1);last[c]=i;best=max(best,i-left+1);}return best;}
};
