# SyftBox Installer - The Simplest API Ever

## Installation

```bash
pip install syft-installer
```

## Usage

```python
import syftbox

# That's it! One line installs and runs everything:
syftbox.run()
```

This single command:
- ✅ Downloads SyftBox if not installed
- ✅ Handles email/OTP authentication
- ✅ Creates all necessary directories
- ✅ Starts the background client
- ✅ Shows you the status

## The Complete API (Yes, This Is Everything)

```python
import syftbox

# Main commands
syftbox.run()        # Install (if needed) and start
syftbox.stop()       # Stop the client
syftbox.status()     # Show pretty status
syftbox.restart()    # Restart the client
syftbox.uninstall()  # Remove everything

# Quick checks
syftbox.check.is_installed  # -> True/False
syftbox.check.is_running    # -> True/False
```

## Beautiful Status Output

```python
>>> syftbox.status()
╭─────────────────────────────── SyftBox Status ───────────────────────────────╮
│                                                                              │
│   Installed   ✅ True                                                        │
│   Running     ✅ True                                                        │
│   Email       user@example.com                                               │
│   Server      https://syftbox.net                                            │
│   Data Dir    /home/user/SyftBox                                             │
│   Daemons     1 running (PIDs: 12345)                                        │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## For Google Colab

```python
# In a Colab cell:
!pip install syft-installer

import syftbox
syftbox.run()  # Handles everything!
```

## Advanced Usage (Only If You Really Need It)

```python
# Specify email upfront
syftbox.run(email="your@email.com")

# Run in foreground instead of background
syftbox.run(background=False)

# Stop all daemons (not just ours)
syftbox.stop(all=True)

# Skip confirmation on uninstall
syftbox.uninstall(confirm=False)
```

## Custom Configuration (For the <1% Who Need It)

```python
# Create a custom instance
custom = syftbox.SyftBox(
    email="user@example.com",
    server="https://custom.server.com",
    data_dir="/custom/data/path"
)
custom.run()
```

## Design Philosophy

1. **One-line operation**: `syftbox.run()` does everything
2. **Smart defaults**: Background mode, standard paths, auto-install
3. **Clear verbs**: run, stop, status, uninstall (not start/launch/init/etc)
4. **Self-documenting**: The API is so simple it barely needs docs
5. **Beautiful output**: Rich formatting shows status clearly
6. **Zero configuration**: Works perfectly for 99% of users

## Why This API Is Perfect

- **For beginners**: One command to rule them all
- **For notebooks**: Clean, simple, works everywhere  
- **For experts**: Full control when needed
- **For everyone**: Intuitive, predictable, delightful

The entire useful API literally fits on a Post-it note! 📝