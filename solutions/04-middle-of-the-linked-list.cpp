// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* middleNode(ListNode* head){auto slow=head,fast=head;while(fast && fast->next){slow=slow->next;fast=fast->next->next;}return slow;}
};
