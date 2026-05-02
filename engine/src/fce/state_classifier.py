"""StateClassifier module for FCE."""


class StateClassifier:
    """Classifies pack state and returns deterministic confidence score."""

    def compute_confidence(self, raw_score: float) -> float:
        """
        Clamp raw_score dans [0.0, 1.0].
        raw_score < 0.0 → 0.0
        raw_score > 1.0 → 1.0
        Sinon → raw_score tel quel.
        """
        return max(0.0, min(1.0, raw_score))

    def score(self, pack_data: dict, context: dict | None = None) -> float:
        """
        Retourne un confidence_score dans [0.0, 1.0].
        Déterministe : mêmes entrées + même pack = même sortie.
        """
        context = context or {}

        score_components = []

        # 1. Score basé sur le nombre de contraintes (normalisé)
        constraints = pack_data.get("constraints", [])
        constraint_score = min(len(constraints) / 10.0, 0.3)
        score_components.append(("constraints", constraint_score))

        # 2. Score basé sur le nombre d'actions (normalisé)
        actions = pack_data.get("actions", [])
        action_score = min(len(actions) / 10.0, 0.3)
        score_components.append(("actions", action_score))

        # 3. Score basé sur le contexte (déterministe)
        context_score = self._compute_context_score(context)
        score_components.append(("context", context_score))

        # 4. Score basé sur le domaine (valeur fixe par domaine)
        domain = pack_data.get("domain", "")
        domain_score = self._compute_domain_score(domain)
        score_components.append(("domain", domain_score))

        # Calcul final : somme pondérée déterministe
        total_weight = 0.0
        weighted_sum = 0.0

        for name, value in score_components:
            weight = self._get_weight(name)
            weighted_sum += value * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5

        final_score = weighted_sum / total_weight

        # AC-004 — déléguer à compute_confidence()
        return self.compute_confidence(final_score)

    def _compute_context_score(self, context: dict) -> float:
        """Calcule un score de contexte de manière déterministe."""
        if not context:
            return 0.0

        key_hash_sum = 0
        for key in sorted(context.keys()):
            value = context[key]
            if isinstance(value, (int, float)):
                key_hash_sum += hash(key) + int(value * 1000)
            elif isinstance(value, str):
                key_hash_sum += hash(key) + sum(ord(c) for c in value)
            elif isinstance(value, bool):
                key_hash_sum += hash(key) + (1 if value else 0)
            else:
                key_hash_sum += hash(key)

        return (abs(key_hash_sum) % 1000) / 1000.0 * 0.2

    def _compute_domain_score(self, domain: str) -> float:
        """Retourne un score fixe par domaine (déterministe)."""
        domain_scores = {
            "finance": 0.8,
            "health": 0.75,
            "career": 0.7,
            "test": 0.5,
        }
        return domain_scores.get(domain.lower(), 0.5)

    def _get_weight(self, component_name: str) -> float:
        """Retourne le poids pour un composant donné (déterministe)."""
        weights = {
            "constraints": 0.3,
            "actions": 0.2,
            "context": 0.2,
            "domain": 0.3,
        }
        return weights.get(component_name, 0.1)
