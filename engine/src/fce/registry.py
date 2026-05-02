"""BuiltinPackRegistry module for FCE."""
import os
import yaml


class BuiltinPackRegistry:
    """Registry for built-in packs."""

    AVAILABLE_PACKS = ["finance_v1", "health_v1", "career_v1"]

    def __init__(self, packs_dir: str | None = None):
        if packs_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.packs_dir = os.path.normpath(os.path.join(current_dir, '..', '..', 'packs'))
        else:
            self.packs_dir = packs_dir

    def lookup(self, pack_id: str) -> dict:
        """
        Recherche pack_id dans le registre.
        Raise ValueError avec valeur du domaine + liste disponibles si inconnu.
        """
        pack_file = os.path.join(self.packs_dir, f"{pack_id}.yaml")

        if not os.path.exists(pack_file):
            available = ", ".join(self.AVAILABLE_PACKS)
            raise ValueError(
                f"Unsupported domain: '{pack_id}'. Available: {available}"
            )

        with open(pack_file, "r") as f:
            return yaml.safe_load(f)

    def get(self, pack_id: str) -> dict:
        """Délègue à lookup()."""
        return self.lookup(pack_id)

    def load(self, pack_id: str) -> dict:
        """Alias de lookup() pour compatibilité AC-005."""
        return self.lookup(pack_id)
