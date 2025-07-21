# SyftBox Installer

A beautifully simple Python interface for installing and managing [SyftBox](https://syftbox.net).

## Installation

```bash
pip install syft-installer
```

## Quick Start

```python
import syftbox

# Install and run SyftBox with one line
syftbox.run()
```

That's it! This single command:
- ✅ Downloads SyftBox 
- ✅ Handles authentication (email + OTP)
- ✅ Creates necessary directories
- ✅ Starts the background daemon
- ✅ Shows you the status

## Simple API

```python
import syftbox

syftbox.run()        # Install (if needed) and start
syftbox.status()     # Show current status
syftbox.stop()       # Stop the daemon
syftbox.restart()    # Restart the daemon
syftbox.uninstall()  # Remove everything

# Quick checks
syftbox.check.is_installed  # -> True/False
syftbox.check.is_running    # -> True/False
```

## Examples

See the [`examples/`](examples/) directory for:
- Notebook tutorials
- Command-line scripts
- Advanced usage patterns

## Advanced Usage

For more control, you can use the underlying installer classes:

```python
import syft_installer as si

# Simple installer
installer = si.SimpleInstaller(email="user@example.com")
installer.step1_download_and_request_otp()
installer.step2_verify_otp("ABCD1234")

# Or use the full installer
installer = si.Installer()
installer.install()
```

## Documentation

See the [`docs/`](docs/) directory for:
- [Simple API Guide](docs/README_SIMPLE.md)
- [Daemon Manager](docs/DAEMON_MANAGER.md)
- [Installation Details](docs/INSTALL_SH_COMPARISON_REPORT.md)

## License

MIT License - see [LICENSE](LICENSE) file.