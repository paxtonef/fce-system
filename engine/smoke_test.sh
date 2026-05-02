#!/bin/bash
# smoke_test.sh — FCE Smoke Test
# Vérifie que le moteur FCE fonctionne avec les 3 packs intégrés
# Exit 0 = succès, Exit 1 = échec

set -e

echo "=================================================="
echo " FCE Smoke Test — SPEC-FCE-001"
echo "=================================================="
echo ""

# Vérifier que l'environnement virtuel est actif
if [ -z "$VIRTUAL_ENV" ]; then
  echo "⚠️  Activation du venv..."
  source .venv/bin/activate
fi

echo "🔍 Test 1 — Import du module FCE"
python -c "from fce.engine import Engine; e = Engine(); print('  ✅ Engine importé')"

echo ""
echo "🔍 Test 2 — Évaluation avec finance_v1"
python -c "
from fce.engine import Engine
e = Engine()
result = e.evaluate('finance_v1')
assert 'confidence_score' in result, 'confidence_score manquant'
assert 'applied_constraints' in result, 'applied_constraints manquant'
assert 'reasoning' in result, 'reasoning manquant'
assert isinstance(result['confidence_score'], float), 'confidence_score non float'
assert 0.0 <= result['confidence_score'] <= 1.0, 'confidence_score hors [0,1]'
assert len(result['applied_constraints']) > 0 or isinstance(result['applied_constraints'], list), 'applied_constraints invalide'
print('  ✅ finance_v1 — OK (score:', round(result[\"confidence_score\"], 3), ')')
"

echo ""
echo "🔍 Test 3 — Évaluation avec health_v1"
python -c "
from fce.engine import Engine
e = Engine()
result = e.evaluate('health_v1')
assert 'confidence_score' in result
print('  ✅ health_v1 — OK (score:', round(result['confidence_score'], 3), ')')
"

echo ""
echo "🔍 Test 4 — Évaluation avec career_v1"
python -c "
from fce.engine import Engine
e = Engine()
result = e.evaluate('career_v1')
assert 'confidence_score' in result
print('  ✅ career_v1 — OK (score:', round(result['confidence_score'], 3), ')')
"

echo ""
echo "🔍 Test 5 — Déterminisme (AC-001)"
python -c "
from fce.engine import Engine
e = Engine()
r1 = e.evaluate('finance_v1')
r2 = e.evaluate('finance_v1')
assert r1['confidence_score'] == r2['confidence_score'], 'Non déterministe!'
print('  ✅ Déterminisme vérifié — score identique sur 2 appels')
"

echo ""
echo "🔍 Test 6 — Exclusion mutuelle (AC-002)"
python -c "
from fce.engine import Engine
e = Engine()
result = e.evaluate('finance_v1')
blocked = set(result.get('blocked_actions', []))
allowed = set(result.get('allowed_actions', []))
intersection = blocked & allowed
assert len(intersection) == 0, f'Violation exclusion mutuelle: {intersection}'
print('  ✅ Exclusion mutuelle vérifiée')
"

echo ""
echo "🔍 Test 7 — Domaine inconnu (AC-008)"
python -c "
from fce.engine import Engine
e = Engine()
try:
    e.evaluate('domaine_inexistant')
    print('  ❌ Aucune erreur levée — FAIL')
    exit(1)
except ValueError as ex:
    assert 'domaine_inexistant' in str(ex), f'Domaine absent du message: {ex}'
    print('  ✅ ValueError conforme:', str(ex)[:60])
"

echo ""
echo "🔍 Test 8 — Entrée manquante (AC-007)"
python -c "
from fce.engine import Engine
e = Engine()
try:
    e.evaluate(None)
    print('  ❌ Aucune erreur levée — FAIL')
    exit(1)
except ValueError as ex:
    assert 'pack_id' in str(ex), f'pack_id absent du message: {ex}'
    print('  ✅ ValueError conforme:', str(ex))
"

echo ""
echo "🔍 Test 9 — Pack invalide (AC-006)"
python -c "
from fce.pack_validator import PackValidator
v = PackValidator()
try:
    v.validate({'pack_id': 'test'})  # manque domain, constraints, actions
    print('  ❌ Aucune erreur levée — FAIL')
    exit(1)
except ValueError as ex:
    print('  ✅ ValueError conforme:', str(ex))
"

echo ""
echo "=================================================="
echo " ✅ SMOKE TEST PASSED — 9/9 tests OK"
echo " FCE est prêt pour le deploy"
echo "=================================================="
exit 0
