# syft-installer

Python library for installing SyftBox - a programmatic alternative to the TUI installer.

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