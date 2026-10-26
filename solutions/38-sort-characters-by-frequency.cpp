// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string frequencySort(string s){unordered_map<char,int> c;for(char x:s)++c[x];vector<pair<int,char>> a;for(auto p:c)a.push_back({p.second,p.first});sort(a.rbegin(),a.rend());string out;for(auto p:a)out.append(p.first,p.second);return out;}
};
