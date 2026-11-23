class Solution {
public:
    bool isAnagram(string s, string t) {
        array<int, 26> c{};
        for (char x : s)
            ++c[x - 'a'];
        for (char x : t)
            --c[x - 'a'];
        return all_of(c.begin(), c.end(), [](int n) { return n == 0; });
    }
};
