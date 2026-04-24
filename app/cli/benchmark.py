"""Batch-run every registered bot for N games each and print a leaderboard.

Shares scoring with the web session (app/web/session.py): +20 per dollar +
current rage + current sp, plus sp bonuses every 9 eats / every 4 new spikes.
Runs silently (no map prints) so a full sweep finishes in minutes."""
import random
import sys
import time

from app import baseMap, statePoint
from app.bot import getBot
from app.database import db
from app.hero import Hero


def play_game(bot_fn, seed, max_moves=100000):
    """Play one silent game with web-mode scoring. Returns a dict matching the
    fields `db.save_score` expects, plus an `end` reason."""
    random.seed(seed)
    rage, point, eated, sp = statePoint()
    map_data = baseMap()
    hero = Hero(map_data)
    moves = 0
    end = 'max_moves'
    for _ in range(max_moves):
        try:
            mv = bot_fn(hero)
        except Exception as exc:
            end = 'exception:{}'.format(exc.__class__.__name__)
            break
        if mv in ('w', 'a', 's', 'd'):
            hero.setMove(mv)
        safety, is_eat = hero.moveWithAutoDirection()
        if hero.hasMove():
            moves += 1
            if rage:
                rage -= 1
            if sp:
                sp -= 1
        if not safety:
            end = 'spike'
            break
        if sp <= 0:
            end = 'timeout'
            break
        if is_eat:
            point += 20 + rage + sp
            rage = 50
            if eated % 9 == 0:
                sp += 200
            if (sum(map_data, []).count('*') - 116) % 4 == 0:
                sp += 50
            eated += 1
            hero.dropRandomDollar()
    spikes = sum(row.count('*') for row in map_data) - 116
    return {
        'score': point,
        'moves': moves,
        'eaten': eated,
        'rage': rage,
        'sp': sp,
        'spikes': spikes,
        'end': end,
    }


def _load_bots(bot_filter=None):
    raw = getBot()
    bots = [(k, v) for k, v in raw.items() if 'name' in v and 'func' in v]
    if bot_filter:
        wanted = set(bot_filter)
        bots = [(k, v) for k, v in bots if k in wanted or v['name'] in wanted]
    bots.sort(key=lambda kv: kv[1]['name'].lower())
    return bots


def run_benchmark(runs_per_bot=10, max_moves=100000, bot_filter=None, save_to_db=False):
    bots = _load_bots(bot_filter)
    if not bots:
        print('No bots found.')
        return {}

    total = len(bots)
    print('=' * 78)
    print('Bulk bot benchmark')
    print('  bots       : {}'.format(total))
    print('  runs/bot   : {}'.format(runs_per_bot))
    print('  max moves  : {}'.format(max_moves))
    print('  save to db : {}'.format('yes (type=bot, per-bot best)' if save_to_db else 'no'))
    print('=' * 78)

    results = {}
    overall_t0 = time.time()
    for idx, (key, entry) in enumerate(bots, 1):
        name = entry['name']
        fn = entry['func']
        header = '[{:>2}/{:<2}] {:<24}'.format(idx, total, name[:24])
        print(header + ' ', end='', flush=True)

        runs = []
        t0 = time.time()
        for seed in range(runs_per_bot):
            r = play_game(fn, seed, max_moves)
            runs.append(r)
            print('{:>7}'.format(r['score']), end=' ', flush=True)
        elapsed = time.time() - t0

        scores = [r['score'] for r in runs]
        best = max(scores)
        best_run = runs[scores.index(best)]
        ends = {}
        for r in runs:
            ends[r['end']] = ends.get(r['end'], 0) + 1

        results[name] = {
            'key': key,
            'runs': runs,
            'best': best,
            'best_run': best_run,
            'best_moves': best_run['moves'],
            'best_eaten': best_run['eaten'],
            'avg': sum(scores) / len(scores),
            'min': min(scores),
            'ends': ends,
            'elapsed': elapsed,
        }
        summary = '  best={:>7}  avg={:>7}  ({:.1f}s)'.format(
            best, int(results[name]['avg']), elapsed)

        if save_to_db:
            # Reuse db.save_score: unique(name,type='bot') + internal "update
            # only if higher" guarantees no duplicate row per bot.
            saved = db.save_score(
                points=best,
                rages=best_run['rage'],
                spikes=best_run['spikes'],
                eaten=best_run['eaten'],
                moves=best_run['moves'],
                time=best_run['sp'],
                name=name,
                score_type='bot',
            )
            if saved:
                summary += '  [db: saved]'
            else:
                summary += '  [db: existing score higher]'
        print(summary)

    total_elapsed = time.time() - overall_t0

    print()
    print('=' * 78)
    print('Leaderboard (sorted by best score)')
    print('=' * 78)
    print('{:<5} {:<26} {:>10} {:>10} {:>10} {:>10} {:>5}'.format(
        'Rank', 'Bot', 'Best', 'Avg', 'Min', 'Moves*', 'Eat*'))
    print('-' * 78)
    ranked = sorted(results.items(), key=lambda kv: kv[1]['best'], reverse=True)
    for rank, (name, stats) in enumerate(ranked, 1):
        print('{:<5} {:<26} {:>10,} {:>10,} {:>10,} {:>10,} {:>5}'.format(
            rank, name[:26], stats['best'], int(stats['avg']),
            stats['min'], stats['best_moves'], stats['best_eaten']))
    print('-' * 78)
    print('* = from the best-scoring run of that bot')
    print('Total wall time: {:.1f}s'.format(total_elapsed))
    print('=' * 78)

    return results


def _parse_args(argv):
    runs = 10
    max_moves = 100000
    filters = None
    save = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ('-n', '--runs'):
            i += 1
            runs = int(argv[i])
        elif a in ('-m', '--max-moves'):
            i += 1
            max_moves = int(argv[i])
        elif a in ('-b', '--bots'):
            i += 1
            filters = [x.strip() for x in argv[i].split(',') if x.strip()]
        elif a in ('-s', '--save'):
            save = True
        elif a in ('-h', '--help'):
            print('Usage: python benchmark.py [--runs N] [--max-moves M] [--bots a,b,c] [--save]')
            print('  --runs N        Runs per bot (default 10)')
            print('  --max-moves M   Cap per game (default 100000)')
            print('  --bots a,b,c    Filter by module key or NAME')
            print('  --save          Persist each bot\'s best run to the scores DB as type=bot.')
            print('                  Uses db.save_score: the UNIQUE(name,type) constraint + its')
            print('                  internal "only update if higher" logic prevent duplicates.')
            sys.exit(0)
        elif a.isdigit() and i == 0:
            runs = int(a)
        else:
            print('Unknown arg: {!r}'.format(a))
            sys.exit(2)
        i += 1
    return runs, max_moves, filters, save


def main(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    if not argv:
        try:
            entered = input('Runs per bot [10]: ').strip()
            if entered:
                argv = [entered]
        except (EOFError, KeyboardInterrupt):
            print()
            return
    runs, max_moves, filters, save = _parse_args(argv)
    run_benchmark(runs_per_bot=runs, max_moves=max_moves, bot_filter=filters,
                  save_to_db=save)


__all__ = ['main', 'run_benchmark', 'play_game']
