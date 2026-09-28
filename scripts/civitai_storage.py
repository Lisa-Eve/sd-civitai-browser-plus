"""Small, safe helpers for model sidecar files and disk checks."""

import json
import os
import shutil
import tempfile

MODEL_EXTENSIONS = frozenset({'.pt', '.ckpt', '.pth', '.safetensors', '.th', '.zip', '.vae'})


def is_model_sidecar(folder, name, entries=None):
    """Only inspect metadata belonging to an actual model in this folder."""
    if not name.lower().endswith('.json') or name.lower().endswith('.cm-info.json'):
        return False
    stem = name[:-5]
    try:
        return any(os.path.splitext(entry)[0].casefold() == stem.casefold()
                   and os.path.splitext(entry)[1].lower() in MODEL_EXTENSIONS
                   for entry in (entries if entries is not None else os.listdir(folder)))
    except OSError:
        return False


def read_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else default
    except (OSError, ValueError):
        return default


def write_json(path, value):
    """Replace a complete JSON file; a failed write leaves the old file intact."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.civitai-', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, indent=4, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def enough_space(path, required, reserve=512 * 1024 * 1024):
    """Check the destination volume, accounting for a small working reserve."""
    existing = os.path.abspath(path)
    while not os.path.exists(existing):
        parent = os.path.dirname(existing)
        if parent == existing:
            return False, 0
        existing = parent
    free = shutil.disk_usage(existing).free
    return free >= required + reserve, free
