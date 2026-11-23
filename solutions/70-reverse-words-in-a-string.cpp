class Solution {
public:
    string reverseWords(string s) {
        istringstream in(s);
        vector<string> w;
        string x;
        while (in >> x)
            w.push_back(x);
        reverse(w.begin(), w.end());
        string out;
        for (auto &a : w) {
            if (!out.empty())
                out += ' ';
            out += a;
        }
        return out;
    }
};
