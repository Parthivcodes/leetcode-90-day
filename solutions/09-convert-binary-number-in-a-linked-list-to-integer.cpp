// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
int getDecimalValue(ListNode* head){int n=0;for(;head;head=head->next)n=n*2+head->val;return n;}
};
