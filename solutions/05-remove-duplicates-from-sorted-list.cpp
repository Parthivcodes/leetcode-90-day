// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* deleteDuplicates(ListNode* head){auto p=head;while(p && p->next){if(p->val==p->next->val)p->next=p->next->next;else p=p->next;}return head;}
};
