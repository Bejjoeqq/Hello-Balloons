"""Bulk bot benchmark entry point.

Usage:
    python benchmark.py                   # prompts for runs, defaults to 10
    python benchmark.py 10                # 10 runs per bot
    python benchmark.py --runs 10         # same
    python benchmark.py --runs 5 --bots opus_max_bot,opus_master_bot
"""
from app.cli.benchmark import main


if __name__ == '__main__':
    main()
