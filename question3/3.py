def max_trading_profit(max_trades, daily_prices):
    """
    Calculates the maximum profit achievable with at most `max_trades`
    buy-and-sell transactions. Each transaction must be completed
    (sell before next buy).  

    Time Complexity: O(K * N)
    Space Complexity: O(K * N)
    K = max_trades, N = number of days
    """
    n = len(daily_prices)
    if n < 2 or max_trades == 0:
        return 0

    if max_trades >= n // 2:
        return sum(max(0, daily_prices[i] - daily_prices[i - 1]) for i in range(1, n))

    dp = [[0] * n for _ in range(max_trades + 1)]

    for i in range(1, max_trades + 1):
        max_diff = -daily_prices[0]  
        for j in range(1, n):
            dp[i][j] = max(dp[i][j - 1], daily_prices[j] + max_diff)
            max_diff = max(max_diff, dp[i - 1][j] - daily_prices[j])

    return dp[max_trades][-1]


#Test Cases
if __name__ == "__main__":
    # Example 1
    print(f"Ex1 (expected 2000): {max_trading_profit(2, [2000, 4000, 1000])}")

    # Example 2
    print(f"Ex2 (expected 10000): {max_trading_profit(2, [1000, 5000, 2000, 8000])}")

    # Example 3
    print(f"Ex3 (expected 0): {max_trading_profit(3, [5000, 3000, 1000])}")

    # Example 4
    print(f"Ex4 (expected 0): {max_trading_profit(0, [1000, 5000])}")