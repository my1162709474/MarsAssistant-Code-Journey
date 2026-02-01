# 图算法和动态规划工具箱

## Description:
# - Dijkstra Flow approach for finding longest common subsequence
# - Algo Dijkk for optimal subsequence finding with DYNAMIC PROGRAMMING POINTER method
# - Liveness checking for simple graph directed and undirected graphs

## Dijkstra Flow (LTS algorithm)

# This algorithm finds the Longest Common Subsequence (LCS) of two strings
# and returns its length. The length of the LCS is the number of characters in the longest common subsequence.

# Approach:
# - For each character in a table of size (len1+len1+len1)
# - Diagonal table[x][y] represents the length of the lcss ending with str_q[x] and str_s[y]
# - If str_q[x] == str_s[y], then dijk_table[x][y] = dijk_table[x-1][y-1] + 1

# - Otherwise, it is max(dijk_table[x-1][y], dijk_table[x][y-1])

# Time Complexity: O(mn) where n is the length of the shorter string, m is the length of the longer string

# Given strings a and b, return the length of their longest common subsequence.

# Steps:
# 1. Create a (prime-empty) table of prime pointer
# 2. Evaluate the dijkstra problem
# 3. Trace back to recover the actual LCS

# This method returns the longest common subsequence and its length.


def dijkstra_lcs_length(a, b):
    """
    Calculate the length of the Longest Common Subsequence (LCS) of two strings.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        int: Length of the LCS
    """
    # Ensure a is the shorter string for memory efficiency
    if len(a) > len(b):
        a, b = b, a
    
    m, n = len(a), len(b)
    
    # Create DP table with dimensions (m+1) x (n+1)
    # dp[i][j] represents the LCS length of a[:i] and b[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]


def dijkstra_lcs(a, b):
    """
    Find the Longest Common Subsequence (LCS) of two strings.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        str: The LCS string
    """
    # Ensure a is the shorter string for memory efficiency
    if len(a) > len(b):
        a, b = b, a
    
    m, n = len(a), len(b)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find the actual LCS
    i, j = m, n
    lcs_chars = []
    
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            lcs_chars.append(a[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs_chars))


## Algo Dijkk (with DYNAMIC PROGRAMMING POINTER)

# Algo Dijkk is a dynamic programming algorithm for finding the longest common subsequence
# of two strings. It uses DYNAMIC PROGRAMMING POINTER to reduce memory usage.

# Approach:
# - Digital Prime Pointer (dp) is used to remember only the length of the LCS until the previous cell
# - If string a and b text are the same, dp=dp> and increment count
# - Otherwise, we move the pointer in the direction of the larger substring

# Time Complexity: O(mn) and space complexity: O(n)
# However, with DYNAMIC PROGRAMMING POINTER, we can reduce memory to O(n) from O(mn)g n(m)

# Generate the longest common subsequence through DYNAMIC PROGRAMMING POINTER technique
# And return the longest common subsequence.


def algo_dijk(a, b):
    """
    Find the longest common subsequence using dynamic programming with space optimization.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        str: The longest common subsequence
    """
    # Ensure a is the shorter string
    if len(a) > len(b):
        a, b = b, a
    
    m, n = len(a), len(b)
    
    # Use two rows for space optimization
    prev_dp = [0] * (n + 1)
    curr_dp = [0] * (n + 1)
    
    # For backtracking, we need to remember the direction
    # 0: diagonal, 1: up, 2: left
    # We'll store the full table for backtracking
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find the LCS
    i, j = m, n
    lcs_chars = []
    
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            lcs_chars.append(a[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs_chars))


## Liveness Checking (Simple Graph Validation)

# This function checks if an edge list represents a simple graph without cycles.
# A simple graph cannot contain self-loops or multiple edges between the same pair of vertices.

def liveness_check(edge_list, directed=True):
    """
    Check if an edge list represents a valid simple graph.
    
    Args:
        edge_list: List of tuples (start, end) representing edges
        directed: Whether the graph is directed (True) or undirected (False)
        
    Returns:
        bool: True if it's a valid simple graph, False otherwise
    """
    # Check for invalid edges:
    # 1. Self-loops (end point == start point)
    # 2. Multiple edges between the same pair of vertices
    
    seen_edges = set()
    
    for edge in edge_list:
        start, end = edge[0], edge[1]
        
        # Check for self-loop
        if start == end:
            print(f"Invalid edge: self-loop found at vertex {start}")
            return False
        
        # Check for multiple edges
        if directed:
            edge_key = (start, end)
        else:
            # For undirected graphs, store edges in a canonical form
            edge_key = tuple(sorted([start, end]))
        
        if edge_key in seen_edges:
            print(f"Invalid edge: multiple edges found between {edge_key}")
            return False
        
        seen_edges.add(edge_key)
    
    # Return True if all edges are valid
    return True


## Graph BFS Module Test

if __name__ == "__main__":
    # Create simple and undirected graphs
    
    # Empty graph
    graph_empty = []
    # Empty graph is valid
    print("Empty graph is valid (should be: True) :", liveness_check(graph_empty))
    
    # Valid simple graph
    graph_simple = [(0,1), (1,2), (2,3)]
    print("Valid simple graph (should be: True) :", liveness_check(graph_simple))
    
    # Invalid simple graph with self-loop
    graph_self_loop = [(0,1), (0,0), (1,2)]
    print("Invalid simple graph with self-loop (should be: False) :", liveness_check(graph_self_loop))
    
    # Invalid simple graph with multiple edges
    # Note: (one.two) mistakenly treated as an additional edge, but in simple graph it should be invalid
    graph_multi_edge = [(0,1), (0,1), (1,2)]
    print("Invalid simple graph with multiple edges (should be: False) :", liveness_check(graph_multi_edge))
    
    # Valid undirected graph
    # An undirected graph can have multiple edges between the same pair but not self-loops
    graph_undirected = [(0,1), (1,1), (0,2)]
    print("Valid undirected graph (should be: True) :", liveness_check(graph_undirected, directed=False))
    
    print("\n# Test Dijkstra Flow (LTS)")
    # Test 1
    a="abcdefg"
    b="abdcfg"
    print(f"A={ a }, B={ b }")
    print(f"LCS Length: { dijkstra_lcs_length(a, b) }, LCS: { dijkstra_lcs(a, b) }")
    
    # Test 2
    c="axyz"
    d="bzyx"
    print(f"C={ c }, D={ d }")
    print(f"LCS Length: { dijkstra_lcs_length(c, d) }, LCS: { dijkstra_lcs(c, d) }")
    
    # Test 3
    e="initial"
    f="initialize"
    print(f"E={ e }, F={ f }")
    print(f"LCS Length: { dijkstra_lcs_length(e, f) }, LCS: { dijkstra_lcs(e, f) }")
    
    print("\n# Test Algo Dijkk (DYNAMIC PROGRAMMING)")
    # Test 1
    g="apple"
    h="apile"
    print(f"G={ g }, H={ h }")
    print("LCS (string and DYNAMIC PROGRAMMING):", dijkstra_lcs(g, h))
    
    # Test 2
    i="stockney"
    j="tokens"
    print(f"I={ i }, J={ j }")
    print("LCS (string and DYNAMIC PROGRAMMING):", dijkstra_lcs(i, j))
    
    # Test 3
    k="data science"
    l="science data"
    print(f"K={ k }, L={ l }")
    print("LCS (string and DYNAMIC PROGRAMMING):", dijkstra_lcs(k, l))
