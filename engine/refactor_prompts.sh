#!/bin/bash
# refactor_prompts.sh — Ajoute les prompts de refactor sur le repo GitHub
# Lance depuis ~/Desktop/spec-fce-001-cards

set -e

cd ~/Desktop/spec-fce-001-cards

echo "Génération des prompts de refactor..."

mkdir -p cards/FC-FCE-AC004/refactor
mkdir -p cards/FC-FCE-AC005/refactor
mkdir -p cards/FC-FCE-AC006/refactor
mkdir -p cards/FC-FCE-AC007/refactor
mkdir -p cards/FC-FCE-AC008/refactor

# ── REFACTOR AC004 ──────────────────────────────────────────
cat > cards/FC-FCE-AC004/refactor/prompt_refactor_1.txt << 'EOF'
REFACTOR — Tentative 1 — FC-FCE-AC004
Oracle verdict : PARTIAL_FULFILLMENT

Le projet FCE existe. Ne recrée pas la structure.
Fichier cible : src/fce/state_classifier.py

[VIOLATION DÉTECTÉE]
compute_confidence() est absente en tant que méthode publique séparée.
Le clamp existe dans score() mais n'est pas exposé comme méthode standalone.

[CORRECTION REQUISE]
Ajoute cette méthode dans StateClassifier :

```python
def compute_confidence(self, raw_score: float) -> float:
    """
    Clamp raw_score dans [0.0, 1.0].
    raw_score < 0.0 → 0.0
    raw_score > 1.0 → 1.0
    Sinon → raw_score tel quel.
    """
    return max(0.0, min(1.0, raw_score))
```

Et modifie score() pour appeler compute_confidence() :
```python
final_score = weighted_sum / total_weight if total_weight > 0 else 0.5
return self.compute_confidence(final_score)
```

[NE PAS MODIFIER]
- La logique de score() existante
- Les autres modules

[QUAND C'EST FAIT]
Place work_result.json ici : results/FC-FCE-AC004/work_result.json
```json
{
  "card_id": "FC-FCE-AC004",
  "status": "PASS",
  "files_changed": ["src/fce/state_classifier.py"],
  "test_results": {"T-004": "pass"},
  "confidence": 0.95,
  "notes": "compute_confidence() ajoutée, score() refactorisé pour l'appeler"
}
```
git add results/FC-FCE-AC004/work_result.json
git commit -m "refactor: FC-FCE-AC004 compute_confidence added"
git push
EOF

# ── REFACTOR AC005 ──────────────────────────────────────────
cat > cards/FC-FCE-AC005/refactor/prompt_refactor_1.txt << 'EOF'
REFACTOR — Tentative 1 — FC-FCE-AC005
Oracle verdict : PARTIAL_FULFILLMENT

Le projet FCE existe. Ne recrée pas la structure.
Fichier cible : src/fce/registry.py

[VIOLATION DÉTECTÉE]
load() est absente — seule get() est implémentée.
Le contrat ACS exige load() comme méthode publique séparée.

[CORRECTION REQUISE]
Ajoute cette méthode dans BuiltinPackRegistry :

```python
def load(self, pack_id: str) -> dict:
    """
    Charge et retourne le pack YAML correspondant à pack_id.
    Accepte : finance_v1, health_v1, career_v1
    Raise ValueError si pack_id inconnu.
    """
    return self.get(pack_id)
```

[NE PAS MODIFIER]
- La logique de get() existante
- Les autres modules

[QUAND C'EST FAIT]
Place work_result.json ici : results/FC-FCE-AC005/work_result.json
```json
{
  "card_id": "FC-FCE-AC005",
  "status": "PASS",
  "files_changed": ["src/fce/registry.py"],
  "test_results": {"T-005": "pass"},
  "confidence": 0.95,
  "notes": "load() ajoutée, délègue à get()"
}
```
git add results/FC-FCE-AC005/work_result.json
git commit -m "refactor: FC-FCE-AC005 load() added"
git push
EOF

# ── REFACTOR AC006 ──────────────────────────────────────────
cat > cards/FC-FCE-AC006/refactor/prompt_refactor_1.txt << 'EOF'
REFACTOR — Tentative 1 — FC-FCE-AC006
Oracle verdict : PARTIAL_FULFILLMENT

Le projet FCE existe. Ne recrée pas la structure.
Fichier cible : src/fce/pack_validator.py

[VIOLATION DÉTECTÉE]
validate() vérifie uniquement pack_id.
Les champs domain (str), constraints (list), actions (list) ne sont pas vérifiés.

[CORRECTION REQUISE]
Remplace validate() par cette version complète :

```python
def validate(self, pack_data: dict) -> dict:
    """
    Champs obligatoires : pack_id (str), domain (str),
                          constraints (list), actions (list)
    Raise ValueError avec le nom du champ manquant si invalide.
    Retourne pack_data enrichi (+ validated_at) si valide.
    """
    import datetime

    if not isinstance(pack_data, dict):
        raise ValueError("pack_data must be a dict")

    required_fields = {
        "pack_id": str,
        "domain": str,
        "constraints": list,
        "actions": list,
    }

    for field, expected_type in required_fields.items():
        if field not in pack_data:
            raise ValueError(f"Missing required field: '{field}'")
        if not isinstance(pack_data[field], expected_type):
            raise ValueError(f"Field '{field}' must be of type {expected_type.__name__}")

    validated = dict(pack_data)
    validated["_validated"] = True
    validated["_validation_version"] = "1.0"
    validated["validated_at"] = datetime.datetime.utcnow().isoformat() + "Z"

    return validated
```

[NE PAS MODIFIER]
- Les autres modules

[QUAND C'EST FAIT]
Place work_result.json ici : results/FC-FCE-AC006/work_result.json
```json
{
  "card_id": "FC-FCE-AC006",
  "status": "PASS",
  "files_changed": ["src/fce/pack_validator.py"],
  "test_results": {"T-006": "pass"},
  "confidence": 0.95,
  "notes": "validate() complété avec vérification domain, constraints, actions"
}
```
git add results/FC-FCE-AC006/work_result.json
git commit -m "refactor: FC-FCE-AC006 full field validation"
git push
EOF

# ── REFACTOR AC007 ──────────────────────────────────────────
cat > cards/FC-FCE-AC007/refactor/prompt_refactor_1.txt << 'EOF'
REFACTOR — Tentative 1 — FC-FCE-AC007
Oracle verdict : PARTIAL_FULFILLMENT

Le projet FCE existe. Ne recrée pas la structure.
Fichier cible : src/fce/engine.py

[VIOLATION DÉTECTÉE]
evaluate() ne vérifie pas si pack_id est None ou vide avant d'appeler registry.get().
La guard clause manquante cause une erreur non conforme au contrat.

[CORRECTION REQUISE]
Ajoute ces deux lignes au début de evaluate() :

```python
def evaluate(self, pack_id: str, context: dict | None = None) -> dict:
    # Guard clause — contrat AC-007
    if not pack_id:
        raise ValueError("Missing required input: pack_id")

    # Pipeline existant — ne pas modifier
    pack = self.registry.get(pack_id)
    validated = self.validator.validate(pack)
    score = self.classifier.score(validated, context)
    constraints = self.activator.activate(validated, score)
    return self.assembler.assemble(validated, constraints, score)
```

[NE PAS MODIFIER]
- Le reste du pipeline
- Les autres modules

[QUAND C'EST FAIT]
Place work_result.json ici : results/FC-FCE-AC007/work_result.json
```json
{
  "card_id": "FC-FCE-AC007",
  "status": "PASS",
  "files_changed": ["src/fce/engine.py"],
  "test_results": {"T-007": "pass"},
  "confidence": 0.95,
  "notes": "Guard clause pack_id ajoutée en début de evaluate()"
}
```
git add results/FC-FCE-AC007/work_result.json
git commit -m "refactor: FC-FCE-AC007 pack_id guard clause"
git push
EOF

# ── REFACTOR AC008 ──────────────────────────────────────────
cat > cards/FC-FCE-AC008/refactor/prompt_refactor_1.txt << 'EOF'
REFACTOR — Tentative 1 — FC-FCE-AC008
Oracle verdict : CONTRACT_VIOLATED (hard stop)

Le projet FCE existe. Ne recrée pas la structure.
Fichier cible : src/fce/registry.py

[VIOLATIONS DÉTECTÉES — 3 violations hard stop]
1. lookup() absent — seul get() existe
2. get() lève FileNotFoundError au lieu de ValueError
3. Message d'erreur non conforme — doit contenir la valeur du domaine + liste disponibles

[CORRECTION REQUISE]
Remplace tout le contenu de registry.py par :

```python
"""BuiltinPackRegistry module for FCE."""
import os
import yaml


class BuiltinPackRegistry:
    """Registry for built-in packs."""

    AVAILABLE_PACKS = ["finance_v1", "health_v1", "career_v1"]

    def __init__(self, packs_dir: str | None = None):
        if packs_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.packs_dir = os.path.join(current_dir, "..", "..", "..", "packs")
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
        """Alias de lookup() pour compatibilité."""
        return self.lookup(pack_id)
```

[QUAND C'EST FAIT]
Place work_result.json ici : results/FC-FCE-AC008/work_result.json
```json
{
  "card_id": "FC-FCE-AC008",
  "status": "PASS",
  "files_changed": ["src/fce/registry.py"],
  "test_results": {"T-008": "pass"},
  "confidence": 0.95,
  "notes": "lookup() implémenté, get() et load() délèguent à lookup(), ValueError conforme"
}
```
git add results/FC-FCE-AC008/work_result.json
git commit -m "refactor: FC-FCE-AC008 lookup() + ValueError conforme"
git push
EOF

echo "✅ 5 prompts de refactor générés"

# Push sur GitHub
git add cards/FC-FCE-AC004/refactor/ \
        cards/FC-FCE-AC005/refactor/ \
        cards/FC-FCE-AC006/refactor/ \
        cards/FC-FCE-AC007/refactor/ \
        cards/FC-FCE-AC008/refactor/

git commit -m "oracle: refactor packets for AC004 AC005 AC006 AC007 AC008 — attempt 1"
git push

echo ""
echo "✅ Pushé sur GitHub"
echo ""
echo "Pour chaque card à corriger, donne à Windsurf :"
echo ""
echo "  AC004 : cat cards/FC-FCE-AC004/refactor/prompt_refactor_1.txt"
echo "  AC005 : cat cards/FC-FCE-AC005/refactor/prompt_refactor_1.txt"
echo "  AC006 : cat cards/FC-FCE-AC006/refactor/prompt_refactor_1.txt"
echo "  AC007 : cat cards/FC-FCE-AC007/refactor/prompt_refactor_1.txt"
echo "  AC008 : cat cards/FC-FCE-AC008/refactor/prompt_refactor_1.txt"
