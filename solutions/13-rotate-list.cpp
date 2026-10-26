// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* rotateRight(ListNode* head,int k){if(!head||!head->next)return head;int n=1;auto tail=head;while(tail->next){++n;tail=tail->next;}k%=n;if(!k)return head;tail->next=head;auto p=head;for(int i=1;i<n-k;++i)p=p->next;head=p->next;p->next=nullptr;return head;}
};
