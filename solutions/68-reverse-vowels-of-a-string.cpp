// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string reverseVowels(string s){string vowels="aeiouAEIOU";int l=0,r=(int)s.size()-1;while(l<r){while(l<r && vowels.find(s[l])==string::npos)++l;while(l<r && vowels.find(s[r])==string::npos)--r;if(l<r)swap(s[l++],s[r--]);}return s;}
};
