class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>> &intervals) {
        sort(intervals.begin(), intervals.end());
        vector<vector<int>> out;
        for (auto a : intervals) {
            if (out.empty() || a[0] > out.back()[1])
                out.push_back(a);
            else
                out.back()[1] = max(out.back()[1], a[1]);
        }
        return out;
    }
};
