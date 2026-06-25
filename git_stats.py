#!/usr/bin/env python3
"""Git repository statistics CLI."""
import subprocess
import argparse
from collections import Counter, defaultdict
from datetime import datetime

def run_git(cmd: str) -> str:
    result = subprocess.run(
        f"git {cmd}", shell=True, capture_output=True, text=True
    )
    return result.stdout.strip()

def get_summary():
    total = run_git("rev-list --count HEAD")
    branches = run_git("branch -a --no-color").count("\n") + 1
    contributors = len(set(run_git("log --format=%ae").split("\n")))
    first = run_git("log --reverse --format=%ci -1")[:10]
    last = run_git("log --format=%ci -1")[:10]
    
    print(f"Repository Statistics")
    print(f"{'='*40}")
    print(f"Total commits:   {total}")
    print(f"Contributors:    {contributors}")
    print(f"Branches:        {branches}")
    print(f"First commit:    {first}")
    print(f"Latest commit:   {last}")

def get_contributors(limit: int = 10):
    log = run_git("shortlog -sne HEAD")
    print(f"Top {limit} Contributors")
    print(f"{'='*40}")
    for i, line in enumerate(log.split("\n")[:limit]):
        line = line.strip()
        if line:
            count, name = line.split("\t", 1)
            print(f"  {i+1:>2}. {name.strip()} ({count.strip()} commits)")

def get_activity():
    dates = run_git("log --format=%cd --date=format:%Y-%m-%d")
    counter = Counter(dates.split("\n"))
    by_weekday = defaultdict(int)
    for date_str, count in counter.items():
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            by_weekday[dt.strftime("%A")] += count
        except ValueError:
            pass
    
    print("Commit Activity by Day")
    print(f"{'='*40}")
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    max_val = max(by_weekday.values()) if by_weekday else 1
    for day in days:
        count = by_weekday.get(day, 0)
        bar = "█" * int(count / max_val * 30)
        print(f"  {day:>9}: {bar} {count}")

def main():
    parser = argparse.ArgumentParser(description="Git Stats CLI")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("summary")
    c = sub.add_parser("contributors")
    c.add_argument("--limit", type=int, default=10)
    sub.add_parser("activity")
    
    args = parser.parse_args()
    cmds = {"summary": lambda: get_summary(),
            "contributors": lambda: get_contributors(getattr(args, "limit", 10)),
            "activity": lambda: get_activity()}
    
    if args.command in cmds:
        cmds[args.command]()
    else:
        get_summary()

if __name__ == "__main__":
    main()
