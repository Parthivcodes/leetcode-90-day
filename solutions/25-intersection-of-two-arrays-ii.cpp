// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> intersect(vector<int>& a,vector<int>& b){unordered_map<int,int> c;for(int x:a)++c[x];vector<int> out;for(int x:b)if(c[x]>0){--c[x];out.push_back(x);}return out;}
};
