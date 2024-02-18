#!/usr/bin/env python3


# longest common string
def lcs(s: str, t: str) -> int:
    """ longest common string
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    res = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            res = max(res, dp[i][j])
    return res
