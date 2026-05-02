# Freedom Constraint Engine — Core Library
**spec_id**: SPEC-FCE-001 | **layer**: engine | **version**: 1.0.0

> Pure Python library. No UI. No API. No dependencies beyond PyYAML.

## What it does

Evaluates a caller's domain state against a declarative constraint pack
and returns a structured, validity-checked decision space.

```python
from fce.engine import Engine

engine = Engine()
result = engine.evaluate("finance_v1")

print(result["confidence_score"])   # 0.34
print(result["allowed_actions"])    # ["A002"]
print(result["blocked_actions"])    # ["A001"]
```

## Architecture

```
engine.evaluate(pack_id)
  ├── BuiltinPackRegistry.lookup()   ← packs/*.yaml
  ├── PackValidator.validate()
  ├── StateClassifier.score()
  ├── ConstraintActivator.activate()
  └── OutputAssembler.assemble()
```

## Install

```bash
git clone https://github.com/paxtonef/spec-fce-001-cards
cd spec-fce-001-cards
python -m venv .venv
source .venv/bin/activate
pip install pyyaml pytest
export PYTHONPATH="$PWD/src:$PYTHONPATH"
```

## Run tests

```bash
pytest tests/ -v
```

## Smoke test

```bash
chmod +x smoke_test.sh
./smoke_test.sh
```

## Built-in packs

| Pack | Domain |
|------|--------|
| `finance_v1` | Financial constraints |
| `health_v1` | Health constraints |
| `career_v1` | Career constraints |

## Used by

- [fce-api](https://github.com/paxtonef/fce-api) — REST API adapter
- [fce-web](https://github.com/paxtonef/fce-web) — React web interface
- Your CLI, agents, feature cards
