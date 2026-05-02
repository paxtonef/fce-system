# LOG_DEPLOY.md — Freedom Constraint Engine
**spec_id**: SPEC-FCE-001 | **pivot**: CDFS | **version**: 1.0.0
**Oracle receipts**: 8/8 CONTRACT_FULFILLED
**Deploy date**: 2026-05-01

---

## Phase 1 — Analysis

- **Project**: Python stateless module — pre-decision validity gate
- **Stack**: Python 3.11+, PyYAML, pytest
- **Docker**: NO — module pur, venv suffit
- **Secrets scan**: ✅ CLEAN — aucun secret détecté
- **Oracle status**: 8/8 ACS contracts fulfilled

---

## Phase 2 — Environment Setup

```bash
cd ~/Desktop/spec-fce-001-cards
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Expected output: `Successfully installed freedom-constraint-engine-1.0.0`

---

## Phase 3 — Configuration

Variables d'environnement (module stateless — aucun secret requis) :

| Variable | Test Value | Impact si absent |
|----------|-----------|-----------------|
| FCE_LOG_LEVEL | INFO | Log niveau WARNING par défaut |
| FCE_PACKS_DIR | ./packs | Chemin auto-détecté depuis src/ |

`.env.example` créé — copier en `.env` pour les tests locaux.

---

## Phase 4 — Local Deployment

```bash
# Vérifier l'import
python -c "from fce.engine import Engine; print('OK')"

# Test CLI
python cli/fce_cli.py
```

---

## Phase 5 — Smoke Test

```bash
chmod +x smoke_test.sh
./smoke_test.sh
```

**Expected**: 9/9 tests OK, exit code 0

Tests couverts :
- ✅ Import Engine
- ✅ finance_v1, health_v1, career_v1 chargeables
- ✅ Déterminisme (AC-001)
- ✅ Exclusion mutuelle (AC-002)
- ✅ Domaine inconnu → ValueError (AC-008)
- ✅ Entrée manquante → ValueError (AC-007)
- ✅ Pack invalide → ValueError (AC-006)

---

## Phase 7 — GitHub Versioning

```bash
git add LOG_DEPLOY.md .env.example pyproject.toml requirements.txt smoke_test.sh
git commit -m "test: ✅ env local reproductible - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin HEAD:feature/test-auto-$(date +%Y%m%d-%H%M)
```

---

## Oracle Receipts

| Card | Receipt ID | Verdict |
|------|-----------|---------|
| FC-FCE-AC001 | ORACLE-FC-FCE-AC001-20260430T173500Z | CONTRACT_FULFILLED |
| FC-FCE-AC002 | ORACLE-FC-FCE-AC002-20260430T173500Z | CONTRACT_FULFILLED |
| FC-FCE-AC003 | ORACLE-FC-FCE-AC003-20260430T173500Z | CONTRACT_FULFILLED |
| FC-FCE-AC004 | ORACLE-FC-FCE-AC004-20260501T004800Z | CONTRACT_FULFILLED |
| FC-FCE-AC005 | ORACLE-FC-FCE-AC005-20260501T004800Z | CONTRACT_FULFILLED |
| FC-FCE-AC006 | ORACLE-FC-FCE-AC006-20260501T004800Z | CONTRACT_FULFILLED |
| FC-FCE-AC007 | ORACLE-FC-FCE-AC007-20260501T004800Z | CONTRACT_FULFILLED |
| FC-FCE-AC008 | ORACLE-FC-FCE-AC008-20260501T004800Z | CONTRACT_FULFILLED |
