// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
void reorderList(ListNode* head){if(!head||!head->next)return;auto slow=head,fast=head;while(fast->next && fast->next->next){slow=slow->next;fast=fast->next->next;}auto p=slow->next;slow->next=nullptr;ListNode* prev=nullptr;while(p){auto n=p->next;p->next=prev;prev=p;p=n;}p=head;while(prev){auto a=p->next,b=prev->next;p->next=prev;prev->next=a;p=a;prev=b;}}
};
