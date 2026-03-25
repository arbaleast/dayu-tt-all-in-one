#!/usr/bin/env bash
#==============================================================================
# TT310 Enclosure - Bottom Bracket Design Specification Test
# US-003-01 - Document bottom bracket design specifications
#==============================================================================

set -e

ENCLOSURE_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILED=0

echo "=========================================="
echo "TT310 - Bottom Bracket Design Spec Test"
echo "=========================================="

# Test 1: bottom-bracket-design.md exists
echo "[TEST 1] Checking enclosure/docs/bottom-bracket-design.md exists..."
if [[ -f "$ENCLOSURE_DIR/docs/bottom-bracket-design.md" ]]; then
    echo "  ✓ PASS: bottom-bracket-design.md exists"
else
    echo "  ✗ FAIL: bottom-bracket-design.md not found"
    FAILED=1
fi

DOC="$ENCLOSURE_DIR/docs/bottom-bracket-design.md"

# Test 2: Bottom bracket outer dimensions (40×30×15mm)
echo "[TEST 2] Checking bottom bracket outer dimensions..."
BRACKET_DIMS=(
    "宽度.*40|40.*宽度"
    "深度.*30|30.*深度"
    "高度.*15|15.*高度"
)
for dim in "${BRACKET_DIMS[@]}"; do
    if grep -qiE "$dim" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found bottom bracket dimension '$dim'"
    else
        echo "  ✗ FAIL: Missing bottom bracket dimension '$dim'"
        FAILED=1
    fi
done

# Test 3: Bottom bracket recess pocket (3mm)
echo "[TEST 3] Checking bottom bracket recess pocket (3mm)..."
if grep -qiE "凹槽深度|recess.*3.*mm|3.*mm.*凹槽" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found 3mm recess pocket specification"
else
    echo "  ✗ FAIL: Missing 3mm recess pocket specification"
    FAILED=1
fi

# Test 4: Bottom bracket corner fillet radius
echo "[TEST 4] Checking bottom bracket corner fillet radius..."
if grep -qiE "R[23]|圆角半径.*[23]|fillet.*R[23]" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found corner fillet radius specification"
else
    echo "  ✗ FAIL: Missing corner fillet radius specification"
    FAILED=1
fi

# Test 5: M3 countersunk hole positions (4 corners)
echo "[TEST 5] Checking M3 countersunk hole positions (4 corners)..."
M3_CHECKS=(
    "M3"
    "沉头"
    "[4四].*孔"
    "4.*M3"
    "角落"
)
for check in "${M3_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found M3 countersunk reference '$check'"
    else
        echo "  ✗ FAIL: Missing M3 countersunk reference '$check'"
        FAILED=1
    fi
done

# Test 6: Foot mount dimensions (Ø20×15mm)
echo "[TEST 6] Checking foot mount dimensions (Ø20×15mm)..."
MOUNT_CHECKS=(
    "Ø20|20.*mm.*直径|外径.*20"
    "15.*mm.*高度"
)
for check in "${MOUNT_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found foot mount specification '$check'"
    else
        echo "  ✗ FAIL: Missing foot mount specification '$check'"
        FAILED=1
    fi
done

# Test 7: Foot mount M6 through-hole (Ø12mm)
echo "[TEST 7] Checking foot mount M6 through-hole..."
M6_CHECKS=(
    "M6"
    "Ø12|12.*mm.*孔径"
    "通孔|through-hole"
)
for check in "${M6_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found M6 through-hole reference '$check'"
    else
        echo "  ✗ FAIL: Missing M6 through-hole reference '$check'"
        FAILED=1
    fi
done

# Test 8: Foot mount flange contact ring
echo "[TEST 8] Checking foot mount flange contact ring..."
FLANGE_CHECKS=(
    "法兰|flange"
    "接触环|contact"
)
for check in "${FLANGE_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found flange reference '$check'"
    else
        echo "  ✗ FAIL: Missing flange reference '$check'"
        FAILED=1
    fi
done

# Test 9: Foot pad dimensions (Ø25×5mm)
echo "[TEST 9] Checking foot pad dimensions (Ø25×5mm)..."
PAD_CHECKS=(
    "Ø25|25.*mm.*外径"
    "5.*mm.*高度"
)
for check in "${PAD_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found foot pad specification '$check'"
    else
        echo "  ✗ FAIL: Missing foot pad specification '$check'"
        FAILED=1
    fi
done

# Test 10: Foot pad TPU material
echo "[TEST 10] Checking foot pad TPU material..."
if grep -qiE "TPU" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found TPU material specification"
else
    echo "  ✗ FAIL: Missing TPU material specification"
    FAILED=1
fi

# Test 11: Bottom panel hole positions (4×Ø10mm)
echo "[TEST 11] Checking bottom panel hole positions (4×Ø10mm)..."
PANEL_CHECKS=(
    "Ø10|10.*mm.*孔径"
    "[4四].*孔"
    "底板"
)
for check in "${PANEL_CHECKS[@]}"; do
    if grep -qiE "$check" "$DOC" 2>/dev/null; then
        echo "  ✓ PASS: Found bottom panel hole reference '$check'"
    else
        echo "  ✗ FAIL: Missing bottom panel hole reference '$check'"
        FAILED=1
    fi
done

# Test 12: Bottom panel dimensions
echo "[TEST 12] Checking bottom panel dimensions (510×490mm)..."
if grep -qiE "510.*490|490.*510" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found bottom panel 510×490mm dimensions"
else
    echo "  ✗ FAIL: Missing bottom panel 510×490mm dimensions"
    FAILED=1
fi

# Test 13: PETG material for brackets
echo "[TEST 13] Checking PETG material for brackets..."
if grep -qiE "PETG" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found PETG material specification"
else
    echo "  ✗ FAIL: Missing PETG material specification"
    FAILED=1
fi

# Test 14: Freecad modeling guide section
echo "[TEST 14] Checking FreeCAD modeling guide section..."
if grep -qiE "FreeCAD|建模|modeling" "$DOC" 2>/dev/null; then
    echo "  ✓ PASS: Found FreeCAD modeling guide section"
else
    echo "  ✗ FAIL: Missing FreeCAD modeling guide section"
    FAILED=1
fi

echo ""
echo "=========================================="
if [[ $FAILED -eq 0 ]]; then
    echo "ALL TESTS PASSED ✓"
    exit 0
else
    echo "SOME TESTS FAILED ✗"
    exit 1
fi
