class Solution {
public:
    bool canConstruct(string a, string b) {
        array<int, 26> c{};
        for (char x : b)
            ++c[x - 'a'];
        for (char x : a)
            if (--c[x - 'a'] < 0)
                return false;
        return true;
    }
};
