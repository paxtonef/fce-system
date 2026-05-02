# Blueprint — Freedom Constraint Engine
spec_id: SPEC-FCE-001 | hash: 17696fc3...

## Architecture

Moteur de contraintes stateless — porte de validité pré-décision.

```
engine.evaluate(pack_id, context)
  ├── PackValidator.validate(pack)
  ├── BuiltinPackRegistry.get(pack_id)
  ├── StateClassifier.score(pack, context)
  ├── ConstraintActivator.activate(pack, score)
  └── OutputAssembler.assemble(pack, constraints, score)
```

## Tech Stack
- Python 3.11+
- pytest + pytest-bdd
- YAML (constraint packs)
- CLI wrapper : cli/fce_cli.py

## Structure projet
```
src/fce/
  engine.py
  pack_validator.py
  registry.py
  state_classifier.py
  constraint_activator.py
  output_assembler.py
packs/
  finance_v1.yaml
  health_v1.yaml
  career_v1.yaml
tests/unit/
tests/fixtures/
cli/fce_cli.py
```

## Règles absolues
1. engine.py = ZÉRO logique domaine
2. Jamais de sélection/exécution d'action
3. Output toujours complet (applied_constraints + reasoning)
4. Pack toujours validé avant exécution
5. Résultat déterministe
6. blocked_actions ∩ allowed_actions = ∅
