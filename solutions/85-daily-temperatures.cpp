class Solution {
public:
    vector<int> dailyTemperatures(vector<int> &t) {
        vector<int> out(t.size()), s;
        for (int i = 0; i < (int)t.size(); ++i) {
            while (!s.empty() && t[s.back()] < t[i]) {
                out[s.back()] = i - s.back();
                s.pop_back();
            }
            s.push_back(i);
        }
        return out;
    }
};
