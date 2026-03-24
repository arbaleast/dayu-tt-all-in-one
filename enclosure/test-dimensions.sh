#!/usr/bin/env bash
#==============================================================================
# TT310 Enclosure - Dimension Data Completeness Test
# US-001 - Research TT310 dimensions and plan enclosure layout
#==============================================================================

set -e

ENCLOSURE_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILED=0

echo "=========================================="
echo "TT310 Enclosure - Dimension Data Test"
echo "=========================================="

# Test 1: dimensions.md exists
echo "[TEST 1] Checking enclosure/dimensions.md exists..."
if [[ -f "$ENCLOSURE_DIR/dimensions.md" ]]; then
    echo "  ✓ PASS: dimensions.md exists"
else
    echo "  ✗ FAIL: dimensions.md not found"
    FAILED=1
fi

# Test 2: layout.txt exists
echo "[TEST 2] Checking enclosure/layout.txt exists..."
if [[ -f "$ENCLOSURE_DIR/layout.txt" ]]; then
    echo "  ✓ PASS: layout.txt exists"
else
    echo "  ✗ FAIL: layout.txt not found"
    FAILED=1
fi

# Test 3: plan.md exists
echo "[TEST 3] Checking enclosure/plan.md exists..."
if [[ -f "$ENCLOSURE_DIR/plan.md" ]]; then
    echo "  ✓ PASS: plan.md exists"
else
    echo "  ✗ FAIL: plan.md not found"
    FAILED=1
fi

# Test 4: Critical dimensions present in dimensions.md
echo "[TEST 4] Checking critical dimensions in dimensions.md..."
CRITICAL_DIMS=(
    "310×310×310"   # Print volume
    "310"            # Print dimensions
    "470"            # Estimated X outer
    "450"            # Estimated Y outer
    "720"            # Estimated Z height
    "2040"           # Profile type
    "510"            # Enclosure outer X
    "490"            # Enclosure outer Y
    "760"            # Enclosure outer Z
    "120"            # Fan size
)

for dim in "${CRITICAL_DIMS[@]}"; do
    if grep -q "$dim" "$ENCLOSURE_DIR/dimensions.md" 2>/dev/null; then
        echo "  ✓ PASS: Found critical dimension '$dim'"
    else
        echo "  ✗ FAIL: Missing critical dimension '$dim'"
        FAILED=1
    fi
done

# Test 5: Panel dimensions in plan.md
echo "[TEST 5] Checking panel dimensions in plan.md..."
PANEL_DIMS=(
    "510.*760"       # Side panels
    "490.*760"       # Back panel / door
    "510.*490"       # Top/bottom panels
)

for dim in "${PANEL_DIMS[@]}"; do
    if grep -qE "$dim" "$ENCLOSURE_DIR/plan.md" 2>/dev/null; then
        echo "  ✓ PASS: Found panel dimension pattern '$dim'"
    else
        echo "  ✗ FAIL: Missing panel dimension pattern '$dim'"
        FAILED=1
    fi
done

# Test 6: Layout sketch in layout.txt (ASCII art check)
echo "[TEST 6] Checking ASCII layout sketch in layout.txt..."
if grep -qE "(┌|┬|┘|│|├|─|└)" "$ENCLOSURE_DIR/layout.txt" 2>/dev/null; then
    echo "  ✓ PASS: ASCII layout sketch found"
else
    echo "  ✗ FAIL: ASCII layout sketch not found"
    FAILED=1
fi

# Test 7: BOM in plan.md
echo "[TEST 7] Checking BOM/成本估算 in plan.md..."
if grep -qE "(成本|合计|¥|CNY)" "$ENCLOSURE_DIR/plan.md" 2>/dev/null; then
    echo "  ✓ PASS: BOM/成本估算 section found"
else
    echo "  ✗ FAIL: BOM/成本估算 section not found"
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
