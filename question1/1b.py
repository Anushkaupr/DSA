def keyword_segmentation(user_query, marketing_keywords_dictionary):
    """
    Returns all valid ways to insert spaces in `user_query` so that each word
    exists in `marketing_keywords_dictionary`.

    Strategy: Top-down recursion with memoization (Word Break II approach).
    
    Time Complexity: O(n^2)
    Space Complexity: O(n^2)
    """
    memo = {}
    keyword_set = set(marketing_keywords_dictionary)  

    def solve(remaining):
       
        if remaining in memo:
            return memo[remaining]
        
       
        if not remaining:
            return [""]

        results = []
        
        for end in range(1, len(remaining) + 1):
            prefix = remaining[:end]
            if prefix in keyword_set:
               
                for tail in solve(remaining[end:]):
                    sentence = prefix + (" " + tail if tail else "")
                    results.append(sentence)

       
        memo[remaining] = results
        return results

    return solve(user_query)


# Test Cases
if __name__ == "__main__":
    # Example 1
    r1 = keyword_segmentation(
        "nepaltrekkingguide",
        ["nepal", "trekking", "guide", "nepaltrekking"]
    )
    print("Example 1:", r1)
    
     # Example 2
    r2 = keyword_segmentation(
        "visitkathmandunepal",
        ["visit", "kathmandu", "nepal", "visitkathmandu", "kathmandunepal"]
    )
    print("Example 2:", r2)
   

    # Example 3 
    r3 = keyword_segmentation(
        "everesthikingtrail",
        ["everest", "hiking", "trek"]
    )
    print("Example 3:", r3)
   