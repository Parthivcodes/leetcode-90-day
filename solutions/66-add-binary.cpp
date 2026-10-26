// Original prepared solution. LeetCode supplies node definitions.
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
string addBinary(string a,string b){string out;int i=(int)a.size()-1,j=(int)b.size()-1,c=0;while(i>=0||j>=0||c){if(i>=0)c+=a[i--]-'0';if(j>=0)c+=b[j--]-'0';out+=char('0'+c%2);c/=2;}reverse(out.begin(),out.end());return out;}
};
