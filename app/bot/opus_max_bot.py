from collections import deque

from app.hero import Hero

NAME = "Opus_4_7_Max"

# Grid — game hard-codes 20 rows x 80 cols. Hero x is always even (moves by +-2),
# y steps by +-1. Border rows/cols are spikes.
YMAP = 20
XMAP = 80
MOVES = (('w', 0, -1), ('s', 0, 1), ('a', -2, 0), ('d', 2, 0))
DELTA = {'w': (0, -1), 's': (0, 1), 'a': (-2, 0), 'd': (2, 0)}

# Score weights: post-eat reach dominates, dead-end cells proxy for brittleness
# (every dead end is a future trap when the next dollar respawns near it), and
# walk distance is a mild tiebreak against unnecessary wandering.
W_REACH = 10.0
W_DEAD = 2.0
W_DIST = 0.5


def _safe_moves(grid, x, y):
    out = []
    ny = y - 1
    if 0 <= ny < YMAP and grid[ny][x] != '*':
        out.append(('w', x, ny))
    ny = y + 1
    if 0 <= ny < YMAP and grid[ny][x] != '*':
        out.append(('s', x, ny))
    nx = x - 2
    if 0 <= nx < XMAP and grid[y][nx] != '*':
        out.append(('a', nx, y))
    nx = x + 2
    if 0 <= nx < XMAP and grid[y][nx] != '*':
        out.append(('d', nx, y))
    return out


def _bfs_first_move(grid, start, target, forbidden=None):
    """Shortest-path BFS returning the first move. `forbidden` excludes cells
    from the path (used to keep the hero from stepping onto the dollar while
    rerouting to a different approach side)."""
    if start == target:
        return None
    forbid = forbidden if forbidden else ()
    parent = {start: (None, None)}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for mv, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < XMAP and 0 <= ny < YMAP):
                continue
            if grid[ny][nx] == '*':
                continue
            nxt = (nx, ny)
            if nxt in parent:
                continue
            if nxt in forbid and nxt != target:
                continue
            parent[nxt] = ((x, y), mv)
            if nxt == target:
                cur = nxt
                first_move = None
                while parent[cur][0] is not None:
                    first_move = parent[cur][1]
                    cur = parent[cur][0]
                return first_move
            q.append(nxt)
    return None


def _bfs_distance(grid, start, target, forbidden=None):
    if start == target:
        return 0
    forbid = forbidden if forbidden else ()
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (x, y), d = q.popleft()
        for _, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < XMAP and 0 <= ny < YMAP):
                continue
            if grid[ny][nx] == '*':
                continue
            nxt = (nx, ny)
            if nxt in seen:
                continue
            if nxt in forbid and nxt != target:
                continue
            if nxt == target:
                return d + 1
            seen.add(nxt)
            q.append((nxt, d + 1))
    return None


def _flood_with_forbidden(grid, start, forbidden):
    """Single-pass flood-fill from `start`, treating `forbidden` cells as if
    they were spikes. Returns (reach, dead_ends) where dead_ends counts cells
    in the component that have exactly one open (non-forbidden, non-spike)
    neighbor — a proxy for brittleness."""
    sx, sy = start
    if not (0 <= sx < XMAP and 0 <= sy < YMAP) or grid[sy][sx] == '*':
        return 0, 0
    seen = {start}
    q = [start]
    qi = 0
    dead_ends = 0
    while qi < len(q):
        x, y = q[qi]
        qi += 1
        deg = 0
        ny = y - 1
        if 0 <= ny < YMAP and grid[ny][x] != '*':
            nxt = (x, ny)
            if nxt not in forbidden:
                deg += 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        ny = y + 1
        if 0 <= ny < YMAP and grid[ny][x] != '*':
            nxt = (x, ny)
            if nxt not in forbidden:
                deg += 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        nx = x - 2
        if 0 <= nx < XMAP and grid[y][nx] != '*':
            nxt = (nx, y)
            if nxt not in forbidden:
                deg += 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        nx = x + 2
        if 0 <= nx < XMAP and grid[y][nx] != '*':
            nxt = (nx, y)
            if nxt not in forbidden:
                deg += 1
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        if deg == 1:
            dead_ends += 1
    return len(seen), dead_ends


def _score_approach(grid, H, A, D, m_eat, h_to_A_dist):
    """Score eating the dollar at D after approaching from A. The post-eat
    grid has a spike on A unless `__stuckCase` auto-escape triggers (when D's
    other 3 neighbors are already spikes). We model this without copying the
    grid: if the auto-escape will fire, A is treated as walkable in the flood;
    otherwise A is treated as spike (forbidden)."""
    dx_, dy_ = D

    # Count D's open neighbors besides A in the CURRENT grid. If zero, then
    # after placing a spike on A all 4 would be spike and auto-escape opens A.
    other_open = 0
    for _, ddx, ddy in MOVES:
        nx, ny = dx_ + ddx, dy_ + ddy
        if (nx, ny) == A:
            continue
        if 0 <= nx < XMAP and 0 <= ny < YMAP and grid[ny][nx] != '*':
            other_open += 1

    auto_escape = other_open == 0
    forbidden = frozenset() if auto_escape else frozenset((A,))

    # Post-eat flood from D.
    reach, dead_ends = _flood_with_forbidden(grid, D, forbidden)
    if reach <= 1:
        # Hero at D has no way out.
        return float('-inf')

    if h_to_A_dist is None:
        return float('-inf')

    return W_REACH * reach - W_DEAD * dead_ends - W_DIST * h_to_A_dist


def _enumerate_approaches(D):
    dx_, dy_ = D
    return (
        ((dx_ + 2, dy_), 'a'),   # hero right of D, moves left
        ((dx_ - 2, dy_), 'd'),   # hero left of D, moves right
        ((dx_, dy_ + 1), 'w'),   # hero below D, moves up
        ((dx_, dy_ - 1), 's'),   # hero above D, moves down
    )


def _survival_move(grid, H, D):
    hx, hy = H
    dx_, dy_ = D
    best_move = None
    best_key = None
    for mv, nx, ny in _safe_moves(grid, hx, hy):
        reach, dead_ends = _flood_with_forbidden(grid, (nx, ny), frozenset())
        dist = abs(nx - dx_) // 2 + abs(ny - dy_)
        key = (reach - 2 * dead_ends, -dist)
        if best_key is None or key > best_key:
            best_key = key
            best_move = mv
    return best_move


def _find_dollar_safe(grid):
    """Scan the grid for '$' without triggering the game's input() fallback
    on miss. Returns (dx, dy) or None."""
    for y in range(YMAP):
        row = grid[y]
        for x in range(XMAP):
            if row[x] == '$':
                return (x, y)
    return None


def _decide(grid, H, D):
    """Pure decision function. Returns a move char or None if no decision
    possible. All returned moves are guaranteed to target a non-spike cell
    of the passed-in grid."""
    hx, hy = H
    safe = _safe_moves(grid, hx, hy)
    if not safe:
        return None

    if D is None or D == H:
        return _survival_move(grid, H, D if D else H) or safe[0][0]

    approaches = _enumerate_approaches(D)
    forbid_D = frozenset((D,))
    best_score = None
    best_move = None
    for A, m_eat in approaches:
        ax, ay = A
        if not (0 <= ax < XMAP and 0 <= ay < YMAP):
            continue
        if grid[ay][ax] == '*':
            continue
        if A == H:
            first_move = m_eat
            dist = 0
        else:
            first_move = _bfs_first_move(grid, H, A, forbid_D)
            if first_move is None:
                continue
            dist = _bfs_distance(grid, H, A, forbid_D)
            if dist is None:
                continue
        score = _score_approach(grid, H, A, D, m_eat, dist)
        if score == float('-inf'):
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_move = first_move

    if best_move is not None:
        return best_move

    return _survival_move(grid, H, D) or safe[0][0]


def _validate_safe(grid, H, move):
    """Return `move` if it targets a non-spike cell, otherwise swap in the
    first available safe move. This is the final guard — no matter what the
    decision layer returns, we never step onto a spike if a safe cell exists."""
    hx, hy = H
    if move in DELTA:
        dx, dy = DELTA[move]
        nx, ny = hx + dx, hy + dy
        if 0 <= nx < XMAP and 0 <= ny < YMAP and grid[ny][nx] != '*':
            return move
    safe = _safe_moves(grid, hx, hy)
    if safe:
        return safe[0][0]
    return 'w'


def checkBot(hero: Hero):
    """Return one of 'w'/'a'/'s'/'d'.

    Strategy:
      1. Enumerate up to 4 approach sides of the dollar. For each reachable
         side, compute a post-eat score from D via single-pass flood-fill
         that models the spike trail (and the game's auto-escape) without
         copying the grid.
      2. Commit to the approach with the highest score; move one step along
         its BFS path.
      3. If no approach is reachable/safe, fall back to survival: stay in
         the largest component, prefer moves with fewer dead-ends.
      4. Final safety gate: validate the returned move against the live grid
         and substitute a safe move if somehow a spike-bound move slipped
         through. This is a defense against latent bugs and map-state
         surprises (e.g. dropRandomDollar overwriting an adjacent cell).
    """
    try:
        grid = hero.getMap()
        hx, hy = hero.getLocation()
        H = (hx, hy)
        D = _find_dollar_safe(grid)

        move = _decide(grid, H, D) or 'w'
        return _validate_safe(grid, H, move)

    except Exception:
        try:
            for m in ('w', 'a', 's', 'd'):
                if not hero.spikeCheck(m):
                    return m
        except Exception:
            pass
        return 'w'
