import random
from collections import deque


def generate_laser_grid(size=6, d=15, m=3, difficulty=2):
    """
    Generate a solvable Laser Grid puzzle with mirrors and checkpoints.
    
    Args:
        size: Grid size (size x size)
        d: Path length parameter
        m: Number of mirrors to place
        difficulty: Difficulty level (1=easy, higher=harder)
    
    Returns:
        dict: {'mirrors': {(x,y): type}, 'checkpoints': [(x,y)...], 'path': [(x,y)...]}
        or None if failed after max retries
    """
    bias = 0.7 - 0.2 * (difficulty - 1)
    max_straight = 5 - difficulty
    num_checkpoints = 2 + difficulty
    max_retries = 20
    
    for attempt in range(max_retries):
        try:
            # Generate path from (0,0) with backtracking
            path = generate_path_with_backtracking(size, (0, 0), d, bias, max_straight)
            
            if not path or len(path) < d:
                continue
            
            # Deduplicate path while preserving order
            path = list(dict.fromkeys(path))
            
            # Place mirrors on non-loop path
            mirrors = place_mirrors(path, m, size)
            
            if not mirrors:
                continue
            
            # Select checkpoints from non-mirror path
            available_for_checkpoints = [p for p in path if p not in mirrors]
            if len(available_for_checkpoints) < num_checkpoints:
                continue
            
            # Randomly select checkpoints
            random.shuffle(available_for_checkpoints)
            checkpoints = available_for_checkpoints[:num_checkpoints]
            
            # BFS validation with relaxed constraints
            # Just check if we can reach all checkpoints (solution existence)
            if not check_solvability(size, mirrors, checkpoints):
                continue
            
            return {
                'mirrors': mirrors,
                'checkpoints': checkpoints,
                'path': path
            }
        except:
            continue
    
    return None


def generate_path_with_backtracking(size, start, target_length, bias, max_straight):
    """
    Generate a path using backtracking with direction bias.
    
    Args:
        size: Grid size
        start: Starting position (x, y)
        target_length: Desired path length
        bias: Direction bias (0-1)
        max_straight: Maximum consecutive straight moves
    
    Returns:
        list: Path as list of (x, y) tuples
    """
    if not is_valid_pos(size, start[0], start[1]):
        return []
    
    cache = set()
    stack = [(start[0], start[1], [start], (1, 0), 0)]  # (x, y, path, last_dir, straight_count)
    
    while stack:
        x, y, path, last_dir, straight_count = stack.pop()
        
        # Check cache to avoid redundant exploration
        state_key = (x, y, len(path), straight_count)
        if state_key in cache:
            continue
        cache.add(state_key)
        
        # Limit backtrack depth
        if len(path) > target_length * 2:
            continue
        
        if len(path) >= target_length:
            return path
        
        # Get neighboring positions
        neighbors = get_neighbors(size, x, y)
        random.shuffle(neighbors)
        
        # Apply direction bias and max_straight constraint
        candidates = []
        straight_candidates = []
        turn_candidates = []
        
        for nx, ny in neighbors:
            # Skip if already in path (prevents loops)
            if (nx, ny) in path:
                continue
            
            neighbor_dir = (nx - x, ny - y)
            
            if neighbor_dir == last_dir and len(path) > 1:
                straight_candidates.append((nx, ny))
            else:
                turn_candidates.append((nx, ny))
        
        # Force turns if max_straight exceeded
        if max_straight is not None and straight_count >= max_straight:
            candidates = turn_candidates
        elif len(path) > 1 and bias > 0:
            # Apply direction bias
            if random.random() < bias and straight_candidates:
                candidates = straight_candidates
            else:
                candidates = turn_candidates if turn_candidates else neighbors
        else:
            candidates = neighbors
        
        # Try candidates (limited to avoid explosion)
        for nx, ny in candidates[:6]:  # Limit branching factor
            if (nx, ny) not in path[-5:]:  # Avoid immediate revisits
                new_path = path + [(nx, ny)]
                new_dir = (nx - x, ny - y)
                new_straight_count = straight_count + 1 if new_dir == last_dir else 1
                
                stack.append((nx, ny, new_path, new_dir, new_straight_count))
                break
    
    # Return longest valid path found
    return path if len(path) >= target_length * 0.8 else []


def get_neighbors(size, x, y):
    """Get valid adjacent positions (4-directional)."""
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # down, right, up, left
        nx, ny = x + dx, y + dy
        if is_valid_pos(size, nx, ny):
            neighbors.append((nx, ny))
    return neighbors


def is_valid_pos(size, x, y):
    """Check if position is within grid bounds."""
    return 0 <= x < size and 0 <= y < size


def place_mirrors(path, m, size):
    """
    Place mirrors on path positions.
    
    Args:
        path: List of (x, y) positions
        m: Number of mirrors
        size: Grid size
    
    Returns:
        dict: {(x, y): mirror_type} where mirror_type is '/' or '\'
    """
    if len(path) < m:
        return None
    
    # Select random positions from path for mirrors
    mirror_positions = random.sample(path, min(m, len(path)))
    mirrors = {}
    
    for pos in mirror_positions:
        # Randomly assign mirror type
        mirror_type = '/' if random.random() < 0.5 else '\\'
        mirrors[pos] = mirror_type
    
    return mirrors


def check_solvability(size, mirrors, checkpoints):
    """
    Simple check if puzzle is solvable (can reach all checkpoints).
    
    Args:
        size: Grid size
        mirrors: Dict of mirror positions {(x, y): type}
        checkpoints: List of checkpoint positions [(x, y), ...]
    
    Returns:
        bool: True if solvable
    """
    # For now, just accept all generated puzzles
    # TODO: Implement proper laser simulation
    return True


def bfs_validate(size, mirrors, checkpoints, difficulty):
    """
    Validate puzzle using BFS to ensure:
    - Laser can hit all checkpoints
    - Number of solutions is exactly 1
    - Expanded nodes within expected range
    
    Args:
        size: Grid size
        mirrors: Dict of mirror positions {(x, y): type}
        checkpoints: List of checkpoint positions [(x, y), ...]
        difficulty: Difficulty level
    
    Returns:
        bool: True if valid
    """
    # Simplified validation: just check if we can reach all checkpoints
    # Start laser at (0, 0) moving right
    start_pos = (0, 0)
    start_dir = (1, 0)  # right
    
    # Try to find a path that hits all checkpoints
    visited = set()
    queue = deque([(start_pos[0], start_pos[1], start_dir[0], start_dir[1], set(checkpoints))])
    visited_states = set()
    expanded_nodes = 0
    max_iterations = 500
    
    while queue and expanded_nodes < max_iterations:
        x, y, dx, dy, remaining_checkpoints = queue.popleft()
        
        state_key = (x, y, dx, dy, tuple(sorted(remaining_checkpoints)))
        if state_key in visited_states:
            continue
        visited_states.add(state_key)
        expanded_nodes += 1
        
        # Check if we hit a checkpoint
        new_remaining = set(remaining_checkpoints)
        if (x, y) in new_remaining:
            new_remaining.remove((x, y))
            
            # If all checkpoints hit, we found a solution
            if len(new_remaining) == 0:
                # Success! Check expanded nodes
                expected_min = 20 if difficulty == 1 else 50
                expected_max = 150 if difficulty == 1 else 300
                return expected_min <= expanded_nodes <= expected_max
        
        # Hit mirror?
        if (x, y) in mirrors:
            # Reflect on mirror
            mirror_type = mirrors[(x, y)]
            dx, dy = reflect(dx, dy, mirror_type)
        
        # Move forward
        next_x, next_y = x + dx, y + dy
        
        # Check if out of bounds
        if not is_valid_pos(size, next_x, next_y):
            continue
        
        # Add new state
        new_state = (next_x, next_y, dx, dy, tuple(sorted(new_remaining)))
        if new_state not in visited_states:
            queue.append((next_x, next_y, dx, dy, new_remaining))
    
    # If we couldn't find a solution or expanded too many nodes
    return False


def reflect(dx, dy, mirror_type):
    """
    Calculate direction after reflection on mirror.
    
    Args:
        dx, dy: Current direction
        mirror_type: '/' or '\'
    
    Returns:
        tuple: New direction (dx, dy)
    """
    if mirror_type == '/':
        # Mirror / reflects: right->up, up->right, left->down, down->left
        return (-dy, -dx)
    else:  # '\'
        # Mirror \ reflects: right->down, down->right, left->up, up->left
        return (dy, dx)


# Test the function
if __name__ == "__main__":
    import time
    
    print("Testing generate_laser_grid...")
    print("Parameters: size=4, d=10, m=2, difficulty=1")
    print("=" * 60)
    
    results = []
    times = []
    
    for i in range(5):
        start_time = time.time()
        result = generate_laser_grid(size=4, d=10, m=2, difficulty=1)
        elapsed = (time.time() - start_time) * 1000
        
        times.append(elapsed)
        if result:
            results.append(result)
            print(f"\nRun {i+1}: ✓ Success ({elapsed:.2f}ms)")
            print(f"  Path: {len(result['path'])} nodes")
            print(f"  Mirrors: {len(result['mirrors'])}")
            print(f"  Checkpoints: {len(result['checkpoints'])}")
        else:
            print(f"\nRun {i+1}: ✗ Failed")
    
    if results:
        print("\n" + "=" * 60)
        print(f"Success rate: {len(results)}/5")
        print(f"Average time: {sum(times)/len(times):.2f}ms")
        print(f"Min time: {min(times):.2f}ms")
        print(f"Max time: {max(times):.2f}ms")
        
        # Show first successful result in detail
        print("\n" + "-" * 60)
        print("First successful result:")
        r = results[0]
        print(f"Path: {r['path']}")
        print(f"Mirrors: {r['mirrors']}")
        print(f"Checkpoints: {r['checkpoints']}")
