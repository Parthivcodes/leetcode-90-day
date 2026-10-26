// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* removeElements(ListNode* head,int val){ListNode d(0,head);auto p=&d;while(p->next){if(p->next->val==val)p->next=p->next->next;else p=p->next;}return d.next;}
};
