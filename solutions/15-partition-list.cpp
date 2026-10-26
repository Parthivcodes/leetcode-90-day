// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* partition(ListNode* head,int x){ListNode a,b;auto p=&a,q=&b;while(head){auto next=head->next;head->next=nullptr;if(head->val<x){p->next=head;p=head;}else{q->next=head;q=head;}head=next;}p->next=b.next;return a.next;}
};
