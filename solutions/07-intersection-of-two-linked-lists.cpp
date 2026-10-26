// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* getIntersectionNode(ListNode* a,ListNode* b){auto p=a,q=b;while(p!=q){p=p?p->next:b;q=q?q->next:a;}return p;}
};
