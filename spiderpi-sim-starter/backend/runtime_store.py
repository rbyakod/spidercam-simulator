from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Callable, Dict

from machine_state import default_state, refresh_state
from models import RuntimeContext


class RuntimeStore:
    def __init__(self, context: RuntimeContext, data_dir: Path | None = None):
        self.context = context
        self.data_dir = data_dir or Path("data")
        self.state_path = self.data_dir / "runtime_state.json"
        self.state_lock_path = self.data_dir / "runtime_state.lock"
        self.leader_lock_path = self.data_dir / "sim_loop.lock"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def read_state_unlocked(self) -> Dict[str, object]:
        if not self.state_path.exists():
            state = default_state(self.context)
            self.write_state_unlocked(state)
            return state
        raw = json.loads(self.state_path.read_text())
        return refresh_state(raw, self.context)

    def write_state_unlocked(self, state: Dict[str, object]) -> None:
        normalized = refresh_state(state, self.context)
        payload = json.dumps(normalized)
        with tempfile.NamedTemporaryFile("w", delete=False, dir=str(self.data_dir), suffix=".tmp") as tf:
            tf.write(payload)
            temp_name = tf.name
        os.replace(temp_name, self.state_path)

    def with_state_lock(self, mutator: Callable[[Dict[str, object]], None] | None = None) -> Dict[str, object]:
        with open(self.state_lock_path, "a+") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            state = self.read_state_unlocked()
            if mutator is not None:
                mutator(state)
                state = refresh_state(state, self.context)
                self.write_state_unlocked(state)
            return state
