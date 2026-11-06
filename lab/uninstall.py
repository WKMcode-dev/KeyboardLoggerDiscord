"""Remove only known, user-selected local lab data. No system modifications."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Clean up local lab data")
    parser.add_argument("--db", default="lab.sqlite3", help="Local SQLite database path")
    parser.add_argument("--confirm", action="store_true", help="Confirm deletion of local lab DB")
    args = parser.parse_args()
    path = Path(args.db).expanduser().resolve()
    if not args.confirm:
        print(f"Would remove local lab database: {path}")
        print("Close the server and re-run with --confirm to delete.")
        return
    for suffix in ("", "-wal", "-shm"):
        target = Path(str(path) + suffix)
        if target.is_file():
            target.unlink()
            print(f"Removed: {target}")
    print("Lab client does not install services, startup tasks, or hidden copies.")
    print("Remove your extracted project folder or test executable manually if desired.")

if __name__ == "__main__":
    main()
