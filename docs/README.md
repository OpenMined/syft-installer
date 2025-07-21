# Syft Installer Documentation

Static documentation site for the syft-installer Python library.

## Structure

```
docs/
├── index.html           # Main landing page
├── quickstart.html      # Installation and usage guide
├── core-concept.html    # Architecture and design concepts
├── api/
│   └── index.html       # API reference
├── css/
│   └── style.css        # Styles (matches syft-perm design)
├── js/
│   └── main.js          # Interactive features
└── images/
    └── syft-logo.svg    # Logo and assets
```

## Features

- 🎨 Clean, modern design matching OpenMined branding
- 📱 Fully responsive layout
- 🔍 Interactive code examples with copy-to-clipboard
- 📚 Comprehensive API documentation
- 🚀 Environment-specific usage guides
- ⚡ Fast loading with optimized assets

## Development

To serve locally during development:

```bash
# Using Python's built-in server
cd docs
python -m http.server 8000

# Using Node.js serve
npx serve docs

# Using any other static file server
```

Then open http://localhost:8000 in your browser.

## Deployment

This is a static site that can be deployed to:

- **GitHub Pages**: Push to `gh-pages` branch or use `docs/` folder
- **Netlify**: Connect repository and set build directory to `docs/`
- **Vercel**: Deploy static files from `docs/` directory
- **Any static hosting**: Upload `docs/` folder contents

## Customization

The design follows the syft-perm color scheme and layout patterns. Key customization points:

- **Colors**: Modify CSS variables in `css/style.css`
- **Content**: Edit HTML files directly
- **Branding**: Update logo in `images/syft-logo.svg`
- **Interactivity**: Extend functionality in `js/main.js`

## Links

- [Syft Installer Repository](https://github.com/OpenMined/syft-installer)
- [OpenMined](https://openmined.org)
- [SyftBox](https://syftbox.openmined.org)