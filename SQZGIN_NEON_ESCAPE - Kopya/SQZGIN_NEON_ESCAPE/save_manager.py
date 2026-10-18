"""Güvenli yerel JSON kayıtları."""
import json, os, tempfile, shutil
from pathlib import Path

def save_path():
    base = os.getenv("APPDATA") or os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    folder = Path(base) / "SQZGIN_NEON_ESCAPE"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "profile.json"

DEFAULT = {
    "high_score": 0, "last_score": 0, "games": 0, "total_seconds": 0.0,
    "total_crystals": 0, "coins": 0, "unlocked": ["cyan"], "skin": "cyan",
    "settings": {"master": 0.7, "music": 0.5, "sfx": 0.8, "shake": True,
                 "particles": True, "fullscreen": False, "touch": False, "theme": "cyan"},
    "achievements": [], "best_combo": 0
}

def load_profile():
    path = save_path()
    if not path.exists():
        return json.loads(json.dumps(DEFAULT))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = json.loads(json.dumps(DEFAULT))
        profile.update(data if isinstance(data, dict) else {})
        profile["settings"] = {**DEFAULT["settings"], **profile.get("settings", {})}
        return profile
    except (OSError, ValueError, TypeError):
        try:
            shutil.copy2(path, path.with_suffix(".corrupt.bak"))
        except OSError:
            pass
        return json.loads(json.dumps(DEFAULT))

def save_profile(profile):
    path = save_path()
    try:
        fd, temp = tempfile.mkstemp(prefix="profile_", suffix=".tmp", dir=path.parent)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(profile, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        return True
    except OSError:
        try:
            if 'temp' in locals() and os.path.exists(temp): os.unlink(temp)
        except OSError:
            pass
        return False
