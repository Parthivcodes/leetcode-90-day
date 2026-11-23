class Solution {
public:
    bool containsDuplicate(vector<int> &nums) {
        unordered_set<int> s;
        for (int n : nums)
            if (!s.insert(n).second)
                return true;
        return false;
    }
};
