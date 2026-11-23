class Solution {
public:
    void moveZeroes(vector<int> &nums) {
        int k = 0;
        for (int n : nums)
            if (n)
                nums[k++] = n;
        while (k < (int)nums.size())
            nums[k++] = 0;
    }
};
