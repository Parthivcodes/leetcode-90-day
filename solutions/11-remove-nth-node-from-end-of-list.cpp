// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* removeNthFromEnd(ListNode* head,int n){ListNode d(0,head);auto fast=&d,slow=&d;for(int i=0;i<n;++i)fast=fast->next;while(fast->next){fast=fast->next;slow=slow->next;}slow->next=slow->next->next;return d.next;}
};
