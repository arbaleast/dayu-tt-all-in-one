#!/usr/bin/env bash
#==============================================================================
# TT310 Enclosure - FreeCAD Project Structure Test
# US-002 - Set up FreeCAD project and directory structure
#==============================================================================

set -e

ENCLOSURE_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILED=0

echo "=========================================="
echo "TT310 Enclosure - Project Structure Test"
echo "=========================================="

# Test 1: freecad directory exists
echo "[TEST 1] Checking enclosure/freecad/ directory exists..."
if [[ -d "$ENCLOSURE_DIR/freecad" ]]; then
    echo "  ✓ PASS: freecad/ directory exists"
else
    echo "  ✗ FAIL: freecad/ directory not found"
    FAILED=1
fi

# Test 2: Assembly.FCStd exists and is a valid SQLite/FreeCAD file
echo "[TEST 2] Checking enclosure/freecad/Assembly.FCStd is a valid SQLite database..."
FCSTD="$ENCLOSURE_DIR/freecad/Assembly.FCStd"
if [[ -f "$FCSTD" ]]; then
    # Verify it's a valid SQLite database (FreeCAD 0.19+ format)
    if python3 -c "
import sqlite3, sys
try:
    conn = sqlite3.connect('$FCSTD')
    cur = conn.cursor()
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
    tables = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT * FROM Document')
    doc = cur.fetchone()
    cur.execute('SELECT * FROM Objects WHERE Parent IS NULL')
    root = cur.fetchone()
    conn.close()
    required = {'Document', 'Objects', 'Part', 'Property', 'Extension'}
    if required.issubset(set(tables)):
        print('OK: Valid FreeCAD SQLite database')
        print('Tables:', tables)
        print('Document:', doc)
        print('Root assembly:', root)
    else:
        print('FAIL: Missing required tables')
        sys.exit(1)
except Exception as e:
    print('FAIL:', e)
    sys.exit(1)
" 2>&1 | grep -q "^OK:"; then
        echo "  ✓ PASS: Assembly.FCStd is a valid FreeCAD SQLite file"
    else
        echo "  ✗ FAIL: Assembly.FCStd is not a valid FreeCAD file"
        FAILED=1
    fi
else
    echo "  ✗ FAIL: Assembly.FCStd not found"
    FAILED=1
fi

# Test 3: Assembly.FCStd contains sub-containers for each panel group
echo "[TEST 3] Checking Assembly.FCStd has required sub-containers..."
REQUIRED_GROUPS=("Assembly_Top" "Assembly_Left" "Assembly_Right" "Assembly_Back" "Assembly_Front" "Assembly_Bottom")
MISSING_GROUPS=()
for group in "${REQUIRED_GROUPS[@]}"; do
    if ! python3 -c "
import sqlite3
conn = sqlite3.connect('$FCSTD')
cur = conn.cursor()
cur.execute('SELECT Name FROM Objects WHERE Name=?', ('$group',))
result = cur.fetchone()
conn.close()
exit(0 if result else 1)
" 2>/dev/null; then
        MISSING_GROUPS+=("$group")
    fi
done
if [[ ${#MISSING_GROUPS[@]} -eq 0 ]]; then
    echo "  ✓ PASS: All 6 panel group sub-containers present"
else
    echo "  ✗ FAIL: Missing groups: ${MISSING_GROUPS[*]}"
    FAILED=1
fi

# Test 4: stls directory exists
echo "[TEST 4] Checking enclosure/stls/ directory exists..."
if [[ -d "$ENCLOSURE_DIR/stls" ]]; then
    echo "  ✓ PASS: stls/ directory exists"
else
    echo "  ✗ FAIL: stls/ directory not found"
    FAILED=1
fi

# Test 5: steps directory exists
echo "[TEST 5] Checking enclosure/steps/ directory exists..."
if [[ -d "$ENCLOSURE_DIR/steps" ]]; then
    echo "  ✓ PASS: steps/ directory exists"
else
    echo "  ✗ FAIL: steps/ directory not found"
    FAILED=1
fi

# Test 6: docs directory exists
echo "[TEST 6] Checking enclosure/docs/ directory exists..."
if [[ -d "$ENCLOSURE_DIR/docs" ]]; then
    echo "  ✓ PASS: docs/ directory exists"
else
    echo "  ✗ FAIL: docs/ directory not found"
    FAILED=1
fi

# Test 7: README.md exists with project overview
echo "[TEST 7] Checking enclosure/README.md exists with project overview..."
README="$ENCLOSURE_DIR/README.md"
if [[ -f "$README" ]]; then
    # Check for key content in README
    HAS_OVERVIEW=0
    grep -qi "大鱼TT 310\|TT310\|enclosure" "$README" && HAS_OVERVIEW=1
    grep -qi "软件要求\|Software Requirements\|FreeCAD" "$README" && ((HAS_OVERVIEW++))
    grep -qi "freecad\|stls\|steps\|docs" "$README" && ((HAS_OVERVIEW++))
    if [[ $HAS_OVERVIEW -ge 3 ]]; then
        echo "  ✓ PASS: README.md exists with project overview"
    else
        echo "  ✗ FAIL: README.md missing key content"
        FAILED=1
    fi
else
    echo "  ✗ FAIL: README.md not found"
    FAILED=1
fi

# Test 8: Unit system set to mm in Assembly.FCStd
echo "[TEST 8] Checking Assembly.FCStd unit system is mm..."
UNIT_OK=$(python3 -c "
import sqlite3
conn = sqlite3.connect('$FCSTD')
cur = conn.cursor()
cur.execute('SELECT UnitSystem FROM Document')
row = cur.fetchone()
conn.close()
print('OK' if row and row[0] == 'mm' else 'FAIL')
" 2>/dev/null)
if [[ "$UNIT_OK" == "OK" ]]; then
    echo "  ✓ PASS: Unit system is mm"
else
    echo "  ✗ FAIL: Unit system is not mm"
    FAILED=1
fi

echo "=========================================="
if [[ $FAILED -eq 0 ]]; then
    echo "All tests PASSED"
    exit 0
else
    echo "Some tests FAILED"
    exit 1
fi
