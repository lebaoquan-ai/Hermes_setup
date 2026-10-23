---
name: laptop-manager
description: "Comprehensive system administration, health monitoring, package updates, and hardware control for Arch Linux on ASUS ROG Zephyrus G14."
version: 1.0.0
author: Antigravity
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [System, ArchLinux, Hardware, G14, Asus, Pacman, Monitoring, Maintenance]
---

# Laptop Manager (Arch Linux & ASUS ROG G14)

Manage system updates, monitor hardware health, diagnose system services, and adjust ASUS ROG Zephyrus G14 power profiles.

---

## 1. Quick Health Snapshot

To obtain an instantaneous overview of system health, run the helper script:

```bash
~/.hermes/skills/laptop-manager/scripts/health_check.sh
```

This checks:
- CPU & GPU temperatures via `sensors`
- Memory and Swap usage via `free -h`
- Disk capacity on `/` and `/home`
- Number of pending official package updates
- Failed systemd units

---

## 2. Package Management & Updates (Arch Linux)

Always check pending updates before executing package operations:

### Check Pending Updates (Safe & Non-blocking)
```bash
# Check official repo updates:
checkupdates

# Check AUR updates via yay:
yay -Qua
```

### System Upgrade
```bash
# Full system upgrade including AUR:
yay -Syu
```
> [!IMPORTANT]
> If updates contain `linux`, `linux-headers`, or NVIDIA packages (`nvidia-open`, `nvidia-dkms`), remind the user that a system reboot or dkms module check will be required after updating.

### Maintenance & Cache Cleanup
```bash
# List orphaned packages:
pacman -Qtdq

# Remove orphaned packages:
sudo pacman -Rns $(pacman -Qtdq)

# Clean old cached package archives (keep last 2 versions):
paccache -r
```

---

## 3. Hardware & Power Management (ASUS G14)

Use `asusctl` to manage Zephyrus G14 hardware features:

### Fan & Power Profiles
```bash
# View active profile:
asusctl profile -p

# Cycle or set profile (Quiet, Balanced, Performance):
asusctl profile -n
```

### Battery Charge Limit
```bash
# Set charge limit to 80% to preserve battery longevity:
asusctl battery -c 80
```

### Keyboard Backlight
```bash
# Toggle / adjust keyboard brightness:
asusctl leds -n
```

---

## 4. Diagnostics & Troubleshooting

### Check Failed Services
```bash
systemctl --failed
```

### Inspect High-Priority System Logs
```bash
# Show errors from the current boot:
journalctl -p 3 -xb -n 30 --no-pager
```

### Process Inspection
```bash
# Identify top CPU-consuming processes:
ps aux --sort=-%cpu | head -n 10

# Identify top memory-consuming processes:
ps aux --sort=-%mem | head -n 10
```

---

## Safety Guardrails
1. **Never run destructive mass deletions** (`rm -rf` on root or user home folders).
2. **Never blindly kill core system processes** (`systemd`, `dbus-daemon`, `pipewire`, `wayland/hyprland` compositors).
3. **Always inform the user** when updates require `sudo` permissions or rebooting.
