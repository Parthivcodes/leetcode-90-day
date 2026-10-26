// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class RecentCounter {queue<int> q;public:RecentCounter(){}int ping(int t){q.push(t);while(q.front()<t-3000)q.pop();return q.size();}};
