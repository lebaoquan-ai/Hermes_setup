#!/usr/bin/env bash
# Quick System Health Snapshot for Arch Linux & ASUS ROG Zephyrus G14
set -euo pipefail

echo "=== System Health Snapshot ==="
echo "Host: $(uname -n) ($(uname -r))"
echo "Uptime: $(uptime -p 2>/dev/null || uptime)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2 " used (" $7 " available)"}')"
echo "Disk /: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo "Disk /home: $(df -h /home 2>/dev/null | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}' || echo "N/A")"

if command -v sensors >/dev/null 2>&1; then
    echo "Temperatures:"
    sensors 2>/dev/null | grep -E "temp1:|edge:|Tctl:|junction:" | head -n 5 | awk '{print "  " $0}' || echo "  Sensors unavailable"
fi

if command -v checkupdates >/dev/null 2>&1; then
    UPDATES=$(checkupdates 2>/dev/null | wc -l || echo "0")
    echo "Pending Official Updates: $UPDATES"
fi

if command -v systemctl >/dev/null 2>&1; then
    FAILED=$(systemctl --failed --no-legend 2>/dev/null | wc -l || echo "0")
    echo "Failed Systemd Services: $FAILED"
fi

if command -v asusctl >/dev/null 2>&1; then
    echo "ASUS G14 Profile:"
    asusctl profile -p 2>/dev/null | awk '{print "  " $0}' || echo "  asusctl daemon not reached"
fi
