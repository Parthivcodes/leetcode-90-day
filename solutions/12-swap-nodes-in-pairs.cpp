// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* swapPairs(ListNode* head){ListNode d(0,head);auto p=&d;while(p->next && p->next->next){auto a=p->next,b=a->next;a->next=b->next;b->next=a;p->next=b;p=a;}return d.next;}
};
