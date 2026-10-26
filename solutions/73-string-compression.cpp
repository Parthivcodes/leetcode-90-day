// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int compress(vector<char>& chars){int out=0;for(int i=0;i<(int)chars.size();){int j=i;while(j<(int)chars.size() && chars[j]==chars[i])++j;chars[out++]=chars[i];if(j-i>1)for(char c:to_string(j-i))chars[out++]=c;i=j;}return out;}
};
