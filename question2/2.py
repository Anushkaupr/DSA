class TreeNode:
    """Represents a hydropower plant site in the cascade tree."""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def max_generation_path(root):
    """
    Finds the maximum total power generation along any path in the binary tree.

    Strategy:
    - Post-order DFS traversal.
    - Negative branch sums are ignored (treated as zero).
    - Track the maximum path sum that passes through each node.

    Time Complexity: O(n)
    Space Complexity: O(h) where h = tree height
    """
    max_sum = [float('-inf')] 

    def dfs(node):
        if not node:
            return 0

       
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)

        
        max_sum[0] = max(max_sum[0], node.val + left_gain + right_gain)

       
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return max_sum[0]


#  Test Cases 
if __name__ == "__main__":
    # Example 1
    r1 = TreeNode(1, TreeNode(2), TreeNode(3))
    print(f"Example 1 (expected 6): {max_generation_path(r1)}")

    # Example 2
    r2 = TreeNode(-10, TreeNode(9),
                  TreeNode(20, TreeNode(15), TreeNode(7)))
    print(f"Example 2 (expected 42): {max_generation_path(r2)}")
    print(f"Single -5 (expected -5): {max_generation_path(TreeNode(-5))}")
    r4 = TreeNode(-1, TreeNode(-2), TreeNode(-3))
    print(f"All negative (expected -1): {max_generation_path(r4)}")



    