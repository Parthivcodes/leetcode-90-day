// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* deleteMiddle(ListNode* head){if(!head||!head->next)return nullptr;auto slow=head,fast=head;ListNode* prev=nullptr;while(fast && fast->next){prev=slow;slow=slow->next;fast=fast->next->next;}prev->next=slow->next;return head;}
};
