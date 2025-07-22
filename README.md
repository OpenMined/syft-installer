# syft-installer

> A Python API for installing and managing the SyftBox daemon — perfect for notebooks and automation

## 🚀 ONE-LINE Installation

```python
import syft_installer as si
si.install_and_run()
```

## Why We Built This

Build SyftBox-based APIs, apps, and libraries that "just work" for your users — no manual SyftBox setup required.

- **🔄 Zero-Setup Experience**: Your users import your library and it works instantly. No "install SyftBox first" instructions, no separate daemon management, no confusing setup guides.

- **🛠️ Eliminate Error Handling**: No more awkward "SyftBox not running" errors when users try your API. The SyftBox network starts automatically when needed, seamlessly in the background.

- **📓 Perfect for Builders**: Focus on your application logic, not infrastructure setup. Include syft-installer in your package and your users get the full SyftBox experience effortlessly.

## Installation

```bash
pip install syft-installer
```

## The Syft Network Just Works

Forget about infrastructure — focus on your data science. The entire Syft network is invisible, automatic, and always one line away.

- **⏰ Always One Line**: Every Syft-based app, library, or tool installs with a single import. No setup docs, no "install this first" — just import and use.

- **💫 Invisible Infrastructure**: The entire Syft network runs invisibly in the background. Users never think about daemons, networks, or configuration — it's just there.

- **✨ It Just Works**: Data scientists focus on data science. Developers focus on building apps. The Syft network handles itself automatically and reliably.

## Complete API

```python
import syft_installer as si

# Quick Start
si.install_and_run() # Install and start
si.install()         # Install only
si.install_and_run() # Explicit install + run

# Status & Control
si.status()
si.is_installed()
si.is_running()
si.stop()
si.run_if_stopped()

# Google Colab Integration
si.install_and_run()                    # Auto-detects Google email
si.install_and_run("custom@email.com") # Specify email

# Non-Interactive Mode
session = si.install("email@example.com", interactive=False)
session.submit_otp("ABC123")

# Clean Uninstall
si.uninstall()  # Removes everything
```

## What SyftBox Creates

When installed, SyftBox creates a complete local environment:

```
~/.syftbox/
  ├── config.json          # Authentication and server settings
  ├── logs/                 # Daemon and application logs
  └── cache/                # Downloaded binaries and temp files

~/SyftBox/
  ├── apps/                 # Installed SyftBox applications
  ├── datasites/            # Connected data sources and sites
  ├── apis/                 # API endpoints and services  
  └── sync/                 # Synchronized data and files

# Plus the daemon binary at ~/.local/bin/syftbox
```

## Try It Out

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/OpenMined/syft-installer/blob/main/examples/quickstart.ipynb)

## Documentation

- **[API Reference](https://openmined.github.io/syft-installer/api/)** - Complete method documentation
- **[Website](https://openmined.github.io/syft-installer/)** - Full documentation site

## Platform Support

- **macOS** (Intel & Apple Silicon)
- **Linux** (x86_64 & ARM64)  
- **Google Colab**
- **Jupyter** environments

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.

---

Built with ❤️ by [OpenMined](https://openmined.org)