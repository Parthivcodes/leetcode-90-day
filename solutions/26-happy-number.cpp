// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool isHappy(int n){unordered_set<int> seen;while(n!=1 && seen.insert(n).second){int s=0;while(n){int d=n%10;s+=d*d;n/=10;}n=s;}return n==1;}
};
