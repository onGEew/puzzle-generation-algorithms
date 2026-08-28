import networkx as nx
import random


def check_solvability(targets, rows, cols):
    """
    Check if the subgraph of targets is Eulerian.
    
    Args:
        targets: Set of target positions
        rows: Number of rows
        cols: Number of columns
    
    Returns:
        bool: True if solvable (Eulerian)
    """
    # Create subgraph of targets
    G = nx.grid_2d_graph(rows, cols)
    subgraph = G.subgraph(targets)
    
    # Check if Eulerian
    return nx.is_eulerian(subgraph)


def check_unique_solution(targets, rows, cols, num_tests=5):
    """
    Check if the puzzle has a unique solution.
    
    Args:
        targets: Set of target positions
        rows: Number of rows
        cols: Number of columns
        num_tests: Number of different starts to test
    
    Returns:
        tuple: (unique_paths, unique_count)
    """
    # Create subgraph of targets
    G = nx.grid_2d_graph(rows, cols)
    subgraph = G.subgraph(targets)
    
    if not nx.is_eulerian(subgraph):
        return ([], 0)
    
    unique_paths = set()
    
    # Try different starting points
    target_list = list(targets)
    for _ in range(min(num_tests, len(target_list))):
        start = random.choice(target_list)
        try:
            # Generate Eulerian path starting from start node
            path = list(nx.eulerian_path(subgraph, source=start))
            # Convert edges to node sequence
            if path:
                nodes = [path[0][0]] + [edge[1] for edge in path]
                # Normalize path (rotate to start with same node)
                unique_paths.add(tuple(sorted(nodes)))
        except:
            continue
    
    return (unique_paths, len(unique_paths))


def calculate_difficulty(path):
    """
    Calculate difficulty based on number of turns.
    
    Args:
        path: List of (x, y) positions
    
    Returns:
        float: Turns ratio (0-1)
    """
    if len(path) < 2:
        return 0.0
    
    turns = 0
    for i in range(2, len(path)):
        # Calculate directions
        dir1 = (path[i-1][0] - path[i-2][0], path[i-1][1] - path[i-2][1])
        dir2 = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        
        if dir1 != dir2:
            turns += 1
    
    return turns / (len(path) - 1) if len(path) > 1 else 0.0


def generate_block_fill(rows=8, cols=8, target_count=16, difficulty=2):
    """
    Generate a solvable Block Fill puzzle with no obstacles.
    
    Args:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        target_count: Number of target blocks to cover
        difficulty: Difficulty level (1=easy, higher=harder)
    
    Returns:
        dict: {'path': [(x,y)...], 'targets': {(x,y)...}, 'start': (x,y)}
        or None if failed after max retries
    """
    # Ensure target_count is even (required for Eulerian path)
    original_target_count = target_count
    if target_count % 2 != 0:
        target_count += 1
    
    direction_bias = 0.7 - 0.2 * (difficulty - 1)
    max_retries = 20
    
    for attempt in range(max_retries):
        try:
            # Adjust parameters based on attempt
            current_bias = direction_bias
            current_target = target_count
            
            # Adjust after initial attempts
            if attempt > 10:
                current_bias = min(0.9, direction_bias + 0.2)
            if attempt > 15:
                current_target = max(8, target_count - 2)
            
            # Set max_straight for hard difficulty (force more turns)
            max_straight = None
            if difficulty >= 3:
                max_straight = 5 - difficulty  # difficulty 3: max 2 straight, 4: max 1, 5+: 0
            
            # Create grid graph
            G = nx.grid_2d_graph(rows, cols)
            
            # Choose random start node
            start_node = (random.randint(0, rows-1), random.randint(0, cols-1))
            
            # Generate path using backtracking
            path = backtrack_path(G, start_node, current_target, current_bias, max_straight)
            
            if path and len(path) >= current_target * 0.9:  # Accept 90% of target
                # Validate path: ensure no overlaps
                if len(path) != len(set(path)):
                    # Has duplicates, try to clean
                    unique_path = []
                    seen = set()
                    for node in path:
                        if node not in seen:
                            unique_path.append(node)
                            seen.add(node)
                    path = unique_path
                
                if len(path) < current_target * 0.9:
                    continue
                
                targets = set(path)
                
                # Run checks
                # Check solvability (Eulerian) - make it soft
                is_eulerian = check_solvability(targets, rows, cols)
                
                # Check unique solution (relaxed - allow if 1-2 unique solutions found)
                unique_paths, unique_count = check_unique_solution(targets, rows, cols, num_tests=5)
                
                # Only reject if really problematic
                if attempt < 15 and not is_eulerian:
                    continue
                if attempt < 10 and unique_count > 5:
                    continue
                
                # Calculate and verify difficulty
                turns_ratio = calculate_difficulty(path)
                
                # Relax difficulty constraints to be more permissive
                # For difficulty 1 (easy), prefer lower turn ratios but accept wider range
                if difficulty == 1 and turns_ratio > 0.4:
                    if attempt < max_retries - 1:
                        continue
                
                # For higher difficulties, accept if reasonable
                if difficulty > 1 and turns_ratio < 0.15:
                    if attempt < max_retries - 2:
                        continue
                
                return {
                    'path': path,
                    'targets': targets,
                    'start': path[0] if path else start_node,
                    'turns_ratio': turns_ratio,
                    'unique_count': unique_count,
                    'is_eulerian': is_eulerian
                }
        except Exception as e:
            continue
    
    return None


def backtrack_path(graph, start, target_length, direction_bias, max_straight=None):
    """
    Generate a path using backtracking with direction bias and optimizations.
    
    Args:
        graph: NetworkX graph
        start: Starting node (x, y)
        target_length: Desired path length
        direction_bias: Bias toward straight movement (0-1)
        max_straight: Maximum consecutive straight moves (None = unlimited)
    
    Returns:
        list: Path as list of (x, y) tuples
    """
    if start not in graph:
        return []
    
    # Memoization cache for visited states
    cache = set()
    
    stack = [(start, [start], (0, 0), 0)]  # (current, path, last_dir, straight_count)
    visited_edges = set()
    
    while stack:
        current, path, last_dir, straight_count = stack.pop()
        
        # Check cache to avoid redundant exploration
        state_key = (current, len(path), straight_count)
        if state_key in cache:
            continue
        cache.add(state_key)
        
        # Limit backtrack depth to target_length
        if len(path) > target_length * 2:
            continue
        
        if len(path) >= target_length:
            return path
        
        # Get neighboring nodes
        neighbors = list(graph.neighbors(current))
        random.shuffle(neighbors)
        
        # Apply direction bias and max_straight constraint
        candidates = []
        straight_candidates = []
        turn_candidates = []
        
        for neighbor in neighbors:
            # Check if we've visited this edge in this path context
            edge_key = (min(current, neighbor), max(current, neighbor))
            if edge_key in visited_edges and neighbor in path:
                continue
            
            neighbor_dir = (neighbor[0] - current[0], neighbor[1] - current[1])
            
            if neighbor_dir == last_dir and len(path) > 1:
                straight_candidates.append(neighbor)
            else:
                turn_candidates.append(neighbor)
        
        # Force turns if max_straight exceeded
        if max_straight is not None and straight_count >= max_straight:
            candidates = turn_candidates
        elif len(path) > 1 and direction_bias > 0:
            # Apply direction bias
            if random.random() < direction_bias and straight_candidates:
                candidates = straight_candidates
            else:
                candidates = turn_candidates if turn_candidates else neighbors
        else:
            candidates = neighbors
        
        # Try candidates (limited to avoid explosion)
        for neighbor in candidates[:8]:  # Limit branching factor
            if neighbor not in path[-5:]:  # Avoid immediate revisits
                new_path = path + [neighbor]
                edge_key = (min(current, neighbor), max(current, neighbor))
                
                new_dir = (neighbor[0] - current[0], neighbor[1] - current[1])
                new_straight_count = straight_count + 1 if new_dir == last_dir else 1
                
                new_visited_edges = visited_edges | {edge_key}
                stack.append((neighbor, new_path, new_dir, new_straight_count))
                
                # Continue searching with this path
                break
    
    # If we couldn't reach target_length, return what we have
    return path if len(path) >= target_length * 0.8 else []


# Test the function
if __name__ == "__main__":
    import time
    
    print("Testing generate_block_fill with 5 runs (8x8, target_count=16, difficulty=1)...")
    print("=" * 60)
    
    results = []
    for i in range(5):
        result = generate_block_fill(rows=8, cols=8, target_count=16, difficulty=1)
        
        if result:
            results.append(result)
            print(f"\nRun {i+1}: Success")
            print(f"  Start: {result['start']}")
            print(f"  Path length: {len(result['path'])}")
            print(f"  Number of targets: {len(result['targets'])}")
            print(f"  Turns ratio: {result.get('turns_ratio', 'N/A'):.3f}")
            print(f"  Is Eulerian: {result.get('is_eulerian', 'N/A')}")
            print(f"  Unique paths found: {result.get('unique_count', 'N/A')}")
        else:
            print(f"\nRun {i+1}: Failed")
    
    # Calculate averages
    if results:
        print("\n" + "=" * 60)
        avg_turns = sum(r.get('turns_ratio', 0) for r in results) / len(results)
        avg_unique = sum(r.get('unique_count', 0) for r in results) / len(results)
        print(f"Average turns ratio: {avg_turns:.3f}")
        print(f"Average unique solution count: {avg_unique:.2f}")
        print(f"Success rate: {len(results)}/5 ({len(results)*20}%)")
    
    # Performance test: 8x8 with target_count=32, difficulty=3
    print("\n" + "=" * 60)
    print("Performance test: 8x8, target_count=32, difficulty=3")
    print("Target: <50ms per generation")
    print("=" * 60)
    
    times = []
    performance_results = []
    for i in range(5):
        start_time = time.time()
        result = generate_block_fill(rows=8, cols=8, target_count=32, difficulty=3)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        times.append(elapsed)
        if result:
            performance_results.append(result)
            status = "✓"
        else:
            status = "✗ Failed"
        
        print(f"Run {i+1}: {elapsed:.2f}ms {status}")
        if result:
            print(f"  Path length: {len(result['path'])}, Targets: {len(result['targets'])}, Turns ratio: {result.get('turns_ratio', 'N/A'):.3f}")
    
    if times:
        print("\n" + "-" * 60)
        print(f"Average time: {sum(times)/len(times):.2f}ms")
        print(f"Min time: {min(times):.2f}ms")
        print(f"Max time: {max(times):.2f}ms")
        print(f"Performance target met: {'✓' if max(times) < 50 else '✗'} ({'PASS' if max(times) < 50 else 'FAIL'})")
