from collections import deque

from app.hero import Hero

NAME = "Opus_4_7_Master"

# Grid constants — the game hard-codes a 20×80 map with cells traversed by
# ±2 in x and ±1 in y. Border rows/cols are all spikes.
YMAP = 20
XMAP = 80
MOVES = (('w', 0, -1), ('s', 0, 1), ('a', -2, 0), ('d', 2, 0))


def _in_bounds(x, y):
    return 0 <= y < YMAP and 0 <= x < XMAP


def _bfs_first_move(grid, start, target):
    """Shortest safe path from start to target (cells reachable without stepping
    on a '*'). Returns the first move's direction char, or None if unreachable.
    """
    if start == target:
        return None
    sx, sy = start
    parent = {start: (None, None)}           # pos -> (prev_pos, move_that_got_here)
    q = deque([start])
    while q:
        x, y = q.popleft()
        for mv, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if not _in_bounds(nx, ny):
                continue
            if (nx, ny) in parent:
                continue
            if grid[ny][nx] == '*':
                continue
            parent[(nx, ny)] = ((x, y), mv)
            if (nx, ny) == target:
                # Walk back target -> start; the last move appended is the
                # one taken from start itself, which is what we return.
                cur = (nx, ny)
                first_move = None
                while parent[cur][0] is not None:
                    first_move = parent[cur][1]
                    cur = parent[cur][0]
                return first_move
            q.append((nx, ny))
    return None


def _reachable_count(grid, start, limit):
    """Flood-fill size from `start` through non-spike cells, capped at `limit`.
    Used to grade how 'open' a candidate next cell is — traps have tiny counts.
    """
    if not _in_bounds(*start) or grid[start[1]][start[0]] == '*':
        return 0
    seen = {start}
    q = deque([start])
    while q and len(seen) < limit:
        x, y = q.popleft()
        for _, dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if (nx, ny) in seen:
                continue
            if not _in_bounds(nx, ny):
                continue
            if grid[ny][nx] == '*':
                continue
            seen.add((nx, ny))
            q.append((nx, ny))
    return len(seen)


def _safe_moves(grid, x, y):
    """All moves whose destination isn't a spike and stays in bounds."""
    out = []
    for mv, dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if _in_bounds(nx, ny) and grid[ny][nx] != '*':
            out.append((mv, nx, ny))
    return out


def checkBot(hero: Hero):
    """Return one of 'w'/'a'/'s'/'d'.

    Strategy:
      1. BFS the current map for the shortest spike-free path to the dollar.
         Take the first step of that path — but only if the destination cell
         still has enough breathing room (flood-fill reach >= threshold) so we
         don't walk into a trap on the way.
      2. If no path exists or the first step is unsafe, pick the safe move that
         maximizes open space ahead, with a mild pull toward the dollar so we
         don't wander.
      3. Last resort: any safe move; else 'w' (the game ends anyway).
    """
    try:
        grid = hero.getMap()
        x, y = hero.getLocation()
        dy, dx = hero.findLocationDollar()   # map.findLocationDollar returns (row, col)
        target = (dx, dy)

        safe = _safe_moves(grid, x, y)
        if not safe:
            return 'w'

        mv = _bfs_first_move(grid, (x, y), target)
        if mv is not None:
            # Eating move is always taken — the point of the game.
            for m, nx, ny in safe:
                if m == mv and (nx, ny) == target:
                    return m
            # Non-eating move: verify the destination isn't a near-trap.
            for m, nx, ny in safe:
                if m == mv:
                    room = _reachable_count(grid, (nx, ny), limit=16)
                    if room >= 6:
                        return m
                    break  # fall through to survival pick

        # Survival: max reachable area, tiebreak toward the dollar.
        best = None
        best_key = (-1, 10**9)
        for m, nx, ny in safe:
            room = _reachable_count(grid, (nx, ny), limit=40)
            dist_to_dollar = abs(nx - dx) // 2 + abs(ny - dy)
            key = (room, -dist_to_dollar)   # bigger room wins; closer dollar breaks ties
            if key > best_key:
                best_key = key
                best = m
        return best or safe[0][0]

    except Exception:
        # Never crash the game loop — fall back to any non-spike direction.
        try:
            for m in ('w', 'a', 's', 'd'):
                if not hero.spikeCheck(m):
                    return m
        except Exception:
            pass
        return 'w'
