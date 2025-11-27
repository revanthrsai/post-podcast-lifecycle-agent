from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import time
import os

@dataclass
class SessionStore:
    session_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)

    def set(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.data.get(key, default)

    def log_step(self, agent_name: str, output: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "timestamp": ts,
            "agent": agent_name,
            "preview": output[:120] + ("..." if len(output) > 120 else "")
        })

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "data": self.data,
            "history": self.history
        }

    def save_snapshot(self, path: str = "outputs/session_snapshot.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.snapshot(), f, ensure_ascii=False, indent=2)

    def clear(self):
        self.data.clear()
        self.history.clear()
