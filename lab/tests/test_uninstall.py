from pathlib import Path
import subprocess
import sys

def test_uninstall_requires_confirmation(tmp_path):
    db = tmp_path / "lab.sqlite3"
    db.write_text("test")
    subprocess.run([sys.executable, "-m", "lab.uninstall", "--db", str(db)], check=True)
    assert db.exists()
    subprocess.run([sys.executable, "-m", "lab.uninstall", "--db", str(db), "--confirm"], check=True)
    assert not db.exists()
