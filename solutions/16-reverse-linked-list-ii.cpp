// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* reverseBetween(ListNode* head,int left,int right){ListNode d(0,head);auto p=&d;for(int i=1;i<left;++i)p=p->next;auto cur=p->next;for(int i=left;i<right;++i){auto n=cur->next;cur->next=n->next;n->next=p->next;p->next=n;}return d.next;}
};
