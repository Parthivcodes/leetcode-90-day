class Solution {
public:
    int subarraySum(vector<int> &nums, int k) {
        unordered_map<int, int> c{{0, 1}};
        int sum = 0, ans = 0;
        for (int n : nums) {
            sum += n;
            ans += c[sum - k];
            ++c[sum];
        }
        return ans;
    }
};
