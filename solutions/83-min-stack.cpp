// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class MinStack {vector<pair<int,int>> s;public:MinStack(){}void push(int val){s.push_back({val,s.empty()?val:min(val,s.back().second)});}void pop(){s.pop_back();}int top(){return s.back().first;}int getMin(){return s.back().second;}};
