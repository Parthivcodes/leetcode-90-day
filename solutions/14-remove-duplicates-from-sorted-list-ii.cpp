// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* deleteDuplicates(ListNode* head){ListNode d(0,head);auto p=&d;while(head){if(head->next && head->val==head->next->val){int v=head->val;while(head && head->val==v)head=head->next;p->next=head;}else{p=head;head=head->next;}}return d.next;}
};
