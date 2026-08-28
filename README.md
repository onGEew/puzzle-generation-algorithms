# Puzzle Generation Algorithms

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains the core procedural generation algorithms for two logic puzzle types developed as part of my HKUST Final Year Project (Neon Pulse: Grid Logic).

## 📦 Contents

| File | Description |
|------|-------------|
| `blockfill_generator.py` | Hamiltonian path generator on grid graphs using DFS + boundary growth with real-time uniqueness verification |
| `lasergrid_generator.py` | Reflection puzzle generator using controlled-turn construction with bitmask BFS verification |

## 🧩 Algorithm Overview

### Block Fill (Hamiltonian Path)
- **Problem**: Generate a path that visits every target cell on a grid exactly once
- **Approach**: Boundary-guided growth with real-time uniqueness checking via DFS + bitmask state representation
- **Complexity**: Practical for grids with < 30 cells (~6ms generation time)
- **Reference**: Hamiltonian path problem (NP-complete, solved practically for small instances)

### Laser Grid (Reflection Puzzles)
- **Problem**: Place mirrors to guide a laser beam through all checkpoints
- **Approach**: Controlled-turn construction + bitmask BFS uniqueness verification
- **Complexity**: BFS state space bounded to ≤ 65,536 states, real-time verification
- **Game Inspiration**: The Witness (Jonathan Blow)

## 🚀 Usage

Both scripts can be run standalone for testing:

```bash
# Test Block Fill generator
python blockfill_generator.py

# Test Laser Grid generator
python lasergrid_generator.py

### Example (Block Fill)

```python
from blockfill_generator import generate_block_fill

result = generate_block_fill(rows=8, cols=8, target_count=16, difficulty=1)
if result:
    print(f"Path length: {len(result['path'])}")
    print(f"Turns ratio: {result['turns_ratio']:.3f}")
```

### Example (Laser Grid)

```python
from lasergrid_generator import generate_laser_grid

result = generate_laser_grid(size=6, d=15, m=3, difficulty=2)
if result:
    print(f"Mirrors: {result['mirrors']}")
    print(f"Checkpoints: {result['checkpoints']}")
```

## 📊 Performance Metrics

| Puzzle Type | Grid Size | Avg Gen Time | Solvability | Uniqueness |
|-------------|-----------|--------------|-------------|------------|
| Block Fill | 6×6 | ~20ms | 90% | 98% |
| Block Fill | 8×8 | ~25ms | 85% | 85% |
| Laser Grid | 6×6 | ~40ms | 100% | 80% |

*Measured on Apple M1 Pro, 16GB RAM*

## 🎮 Interactive Demonstration

These algorithms are integrated into a playable Phaser 3 game suite:
- **Neon Pulse: Grid Logic** — A two-game puzzle collection with Hong Kong-inspired neon aesthetics
- Block Fill: Draw a path through all highlighted cells
- Laser Grid: Place mirrors to guide lasers to checkpoints

> *The frontend implementation is separate. This repository focuses solely on the generation algorithms.*

## 📚 Academic Context

This work was completed as my Final Year Project at HKUST, supervised by Shing-Yu Leung. It combines:
- **Mathematics**: Graph theory, computational complexity, constraint satisfaction
- **Computer Science**: DFS, BFS, bitmasking, backtracking, NP-complete subproblems
- **Digital Media**: Interactive game design and visual aesthetics

## 📄 License

MIT License — feel free to use this code for your own projects, academic or commercial.

## 🔗 Related

- [[FYP Report Link]](https://hkustconnect-my.sharepoint.com/:w:/g/personal/lwwongai_connect_ust_hk/IQDFQVgRpqhBSbjn1VyANWW1ARxyWL6XaEbOH5KzTGJ9EGY?e=Vs1Ot2)

---

*Created by Wong Lee Wai (William) — BSc Mathematics (CS Track) / Digital Media & Creative Arts Extended Major, HKUST 2026*
```
