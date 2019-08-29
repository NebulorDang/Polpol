#include <iostream>
#include <vector>
#include <math.h>
#include <iomanip>
#include <unordered_map>
#include <map>
#include <algorithm>
#include <unordered_set>
#include <set>
#include <queue>
using namespace std;

class Solution {
private:
    int min_pay = INT32_MAX;
public:
    int shoppingOffers(vector<int>& price, vector<vector<int>>& special, vector<int>& needs) {
        sort(special.begin(), special.end(), [](vector<int> &a, vector<int>&b){ return a.back() > b.back();});
        dfs(price, special, needs, 0);
        return min_pay;
    }

    void dfs(vector<int> &price, vector<vector<int>>& special, vector<int> still_needs, int cur_pay){
        int can_exit = 1;
        for(auto &i : still_needs){
            if(i != 0){
                can_exit = 0;
                break;
            }
        }
        if(can_exit){
            min_pay = min(min_pay, cur_pay);
            return;
        }
        for(auto &gift : special){
            vector<int> still_needs_tmp;
            int buy_gift = 1;
            for(int i = 0; i < still_needs.size(); i++){
                if(still_needs[i] - gift[i] < 0){
                    buy_gift = 0;
                    break;
                } else{
                    still_needs_tmp.emplace_back(still_needs[i] - gift[i]);
                }
            }
            if(min_pay < cur_pay + gift.back()){
                buy_gift = 0;
            }
            if(buy_gift){
                dfs(price, special, still_needs_tmp, cur_pay + gift.back());
            } else{
                int total = cur_pay;
                for(int i = 0; i < still_needs.size(); ++i){
                    total += still_needs[i] * price[i];
                }
                min_pay = min(min_pay, total);
            }
        }
    }
};

int main(){
    vector<vector<char>> matrix = {{'1','1','1','1','0'},{'1','1','0','1','0'},{'1','1','0','0','0'},{'0','0','0','0','0'}};
    string words1 = "plasma";
    string words2 = "altruism";
    Solution *solution = new Solution();
    string s = "cbbd";
    vector<int> a = {3, 4, 2};
    cout << solution->shoppingOffers(a);
    vector<vector<int>> mat = {{1,3,1},{1,5,1},{4,2,1}};
}