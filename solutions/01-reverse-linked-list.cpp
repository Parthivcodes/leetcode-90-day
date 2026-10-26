// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* reverseList(ListNode* head) {
    ListNode* prev=nullptr;
    while(head){auto next=head->next; head->next=prev; prev=head; head=next;}
    return prev;
}
};
