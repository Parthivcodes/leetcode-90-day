// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
vector<int> asteroidCollision(vector<int>& asteroids){vector<int>s;for(int x:asteroids){bool alive=true;while(alive && x<0 && !s.empty() && s.back()>0){if(s.back()<-x)s.pop_back();else{if(s.back()==-x)s.pop_back();alive=false;}}if(alive)s.push_back(x);}return s;}
};
