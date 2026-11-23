class Solution {
public:
    vector<int> nextGreaterElements(vector<int> &nums) {
        int n = nums.size();
        vector<int> out(n, -1), s;
        for (int i = 0; i < 2 * n; ++i) {
            while (!s.empty() && nums[s.back()] < nums[i % n]) {
                out[s.back()] = nums[i % n];
                s.pop_back();
            }
            if (i < n)
                s.push_back(i);
        }
        return out;
    }
};
