# SyftBox Daemon Manager

The daemon manager helps you find and manage running SyftBox processes.

## Usage

### Interactive Mode

Run the interactive daemon manager:

```bash
python manage_daemons.py
```

This will show you all running syftbox daemons and provide options to:
- Refresh the list
- Kill specific daemons
- Kill all daemons
- Force kill (SIGKILL) daemons

### Command Line Mode

List all daemons:
```bash
python manage_daemons.py list
```

Kill a specific daemon by PID:
```bash
python manage_daemons.py kill 12345
```

Force kill a daemon:
```bash
python manage_daemons.py kill 12345 --force
```

Kill all daemons:
```bash
python manage_daemons.py killall
```

Force kill all daemons:
```bash
python manage_daemons.py killall --force
```

### Programmatic Usage

```python
import syft_installer as si

# List all running daemons
daemons = si.list_daemons()
for daemon in daemons:
    print(f"PID: {daemon['pid']}, User: {daemon['user']}")

# Kill a specific daemon
si.kill_daemon("12345")  # Returns True if successful

# Kill all daemons
killed_count = si.kill_all_daemons()  # Returns number killed

# Interactive manager
si.interactive_daemon_manager()
```

## Process Information

The daemon manager shows:
- **PID**: Process ID
- **USER**: User running the process
- **CPU%**: CPU usage percentage
- **MEM%**: Memory usage percentage
- **START**: Start time
- **COMMAND**: Full command line

## Notes

- The manager finds all processes containing "syftbox" in the command
- Normal kill uses SIGTERM for graceful shutdown
- Force kill uses SIGKILL for immediate termination
- You may need appropriate permissions to kill processes owned by other users