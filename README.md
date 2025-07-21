# syft-installer

Python library for installing SyftBox - follows the official install.sh implementation while providing programmatic capabilities for notebooks and headless environments.

## Architecture

This installer provides a hybrid approach:

1. **Terminal environments**: Delegates to `syftbox login` TUI (just like install.sh)
2. **Notebook/headless environments**: Implements the OTP flow in Python, then creates the config.json that syftbox expects

Both approaches result in the same outcome - a valid `~/.syftbox/config.json` file that the syftbox client can use.

## Installation

```bash
pip install syft-installer
```

## Quick Start

```python
import syft_installer as si

# Simple one-liner installation
si.install()
```

## Features

- 🎯 **Follows install.sh exactly** - Uses the same flow as the official installer
- 🖥️ **Terminal mode** - Delegates to `syftbox login` TUI when in terminal
- 📓 **Notebook support** - Falls back to programmatic auth in Jupyter/Colab
- 🌍 **Environment variables** - Supports all install.sh environment variables
- 🚀 **Multiple install modes** - interactive, download-only, setup-only
- 📦 **App installation** - Install SyftBox apps during setup
- 🛠️ **PATH management** - Automatically updates shell profiles

## Environment Variables

The installer supports all environment variables from install.sh:

```bash
export INSTALL_MODE=download-only  # or setup-only, interactive (default)
export INSTALL_APPS=app1,app2      # Comma-separated list of apps
export DEBUG=true                  # Enable debug output
export ARTIFACT_BASE_URL=https://custom.url  # Custom download URL
```

## Usage Examples

### Basic Installation

```python
import syft_installer as si

# Create installer instance
installer = si.Installer()
installer.install()  # Interactive installation
```

### Pre-configured Installation

```python
import syft_installer as si

# Skip email prompt
installer = si.Installer(email="user@example.com")
installer.install()  # Only prompts for OTP
```

### Programmatic Installation

```python
import syft_installer as si

# Full control over the process
installer = si.Installer(email="user@example.com")
installer.request_otp()

# Get OTP from email
otp = input("Enter OTP: ")  # Or get programmatically
installer.verify_otp(otp)

# Start client
installer.start_client(background=True)
```

### Google Colab

The library automatically detects and adapts to the Colab environment:

```python
import syft_installer as si

# Works seamlessly in Colab notebooks
si.install()  # Uses widgets for input
```

### Installation Modes

```python
import syft_installer as si

# Download only (no setup)
si.install(install_mode="download-only")

# Setup only (assumes binary already downloaded)
si.install(install_mode="setup-only")

# Interactive (default) - full installation with prompts
si.install(install_mode="interactive")

# With app installation
si.install(install_apps="dataroom,whisper")

# Debug mode
si.install(debug=True)
```

### Headless/CI Mode

```python
import syft_installer as si

# For automated environments
installer = si.Installer(
    email="user@example.com",
    headless=True
)

installer.request_otp()
# Get OTP from email programmatically
installer.verify_otp("ABCD1234")
installer.start_client(background=True)
```

## Features

- 🚀 Simple one-liner installation
- 🔧 Full programmatic control
- 📱 OTP-based authentication
- 🌍 Environment auto-detection (terminal, Jupyter, Colab)
- 🤖 Headless mode for CI/CD
- ⚡ Background process management
- 🔄 Token refresh handling

## License

Apache License 2.0