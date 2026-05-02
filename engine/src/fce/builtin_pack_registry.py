"""BuiltinPackRegistry — loads built-in constraint packs."""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class BuiltinPackRegistry:
    """Registry for built-in domain constraint packs."""

    def __init__(self, packs_dir: Optional[Path] = None):
        if packs_dir is None:
            self.packs_dir = Path(__file__).parent / "packs"
        else:
            self.packs_dir = Path(packs_dir)

    def load(self, domain: str) -> Optional[Dict[str, Any]]:
        """Load a pack by domain identifier (e.g. 'finance_v1')."""
        pack_file = self.packs_dir / f"{domain}.yaml"
        if not pack_file.exists():
            return None
        with open(pack_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, pack_id: str) -> Optional[Dict[str, Any]]:
        """Alias for load() — backward compat."""
        return self.load(pack_id)
