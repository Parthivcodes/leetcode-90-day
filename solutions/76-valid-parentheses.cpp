class Solution {
public:
    bool isValid(string s) {
        string st;
        for (char c : s) {
            if (c == '(' || c == '[' || c == '{')
                st += c;
            else {
                if (st.empty())
                    return false;
                char x = st.back();
                st.pop_back();
                if ((c == ')' && x != '(') || (c == ']' && x != '[') || (c == '}' && x != '{'))
                    return false;
            }
        }
        return st.empty();
    }
};
