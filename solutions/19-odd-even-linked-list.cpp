// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* oddEvenList(ListNode* head){if(!head)return head;auto odd=head,even=head->next,firstEven=even;while(even && even->next){odd->next=even->next;odd=odd->next;even->next=odd->next;even=even->next;}odd->next=firstEven;return head;}
};
