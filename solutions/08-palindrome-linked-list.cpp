// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
bool isPalindrome(ListNode* head){vector<int> a;for(auto p=head;p;p=p->next)a.push_back(p->val);for(int i=0,j=(int)a.size()-1;i<j;++i,--j)if(a[i]!=a[j])return false;return true;}
};
