from math import gcd
from collections import defaultdict

def max_points_on_line(customer_locations):
    """
    Returns the largest number of customer homes that lie on a single straight line.

    Strategy:
    - Fix each point as an anchor.
    - Calculate slopes to every other point.
    - Use GCD-reduced fractions to represent slopes to avoid floating-point errors.

    Time Complexity: O(n^2)
    Space Complexity: O(n)
    """
    n = len(customer_locations)
    if n <= 2:
        return n  

    global_max = 1

    for i in range(n):
        slope_map = defaultdict(int)
        duplicates = 1  
        local_max = 0

        for j in range(i + 1, n):
            dx = customer_locations[j][0] - customer_locations[i][0]
            dy = customer_locations[j][1] - customer_locations[i][1]

           
            if dx == 0 and dy == 0:
                duplicates += 1
                continue

           
            g = gcd(abs(dx), abs(dy))
            if dx < 0:  
                dx, dy = -dx, -dy
            key = (dy // g, dx // g)

            slope_map[key] += 1
            local_max = max(local_max, slope_map[key])

        global_max = max(global_max, local_max + duplicates)

    return global_max


#  Test cases
if __name__ == "__main__":
    tests = [
        ([[1,1],[2,2],[3,3]], 3),  
        ([[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]], 4),  
        ([[0,0],[0,0],[0,0]], 3), 
        ([[1,1]], 1),  
    ]

    for pts, expected in tests:
        result = max_points_on_line(pts)
        print(f"{'PASS' if result == expected else 'FAIL'} | got={result} | expected={expected} | input={pts}")





        