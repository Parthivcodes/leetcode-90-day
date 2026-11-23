class Solution {
public:
    int firstUniqChar(string s) {
        array<int, 26> c{};
        for (char x : s)
            ++c[x - 'a'];
        for (int i = 0; i < (int)s.size(); ++i)
            if (c[s[i] - 'a'] == 1)
                return i;
        return -1;
    }
};
