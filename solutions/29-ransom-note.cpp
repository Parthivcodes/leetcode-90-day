// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool canConstruct(string a,string b){array<int,26> c{};for(char x:b)++c[x-'a'];for(char x:a)if(--c[x-'a']<0)return false;return true;}
};
