// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
ListNode* addTwoNumbers(ListNode* a,ListNode* b){ListNode d;auto p=&d;int carry=0;while(a||b||carry){int s=carry;if(a){s+=a->val;a=a->next;}if(b){s+=b->val;b=b->next;}p->next=new ListNode(s%10);p=p->next;carry=s/10;}return d.next;}
};
