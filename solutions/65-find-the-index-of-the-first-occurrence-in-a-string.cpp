class Solution {
public:
    int strStr(string haystack, string needle) {
        auto p = haystack.find(needle);
        return p == string::npos ? -1 : (int)p;
    }
};
