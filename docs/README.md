# SyftPerm Documentation Website

This directory contains the complete documentation website for SyftPerm, built with modern web standards and styled after the OpenMined design system.

## Structure

```
docs/
├── index.html              # Homepage
├── installation.html       # Installation guide
├── quickstart.html         # 5-minute quick start
├── tutorials/
│   ├── index.html          # Tutorial series overview
│   └── [tutorial pages]    # Individual tutorial pages
├── api/
│   ├── index.html          # API reference
│   └── [api pages]         # Detailed API documentation
├── css/
│   └── style.css           # Main stylesheet (OpenMined design system)
├── js/
│   └── main.js             # Interactive functionality
├── images/
│   └── favicon.svg         # Site favicon
└── README.md               # This file
```

## Design System

The documentation website uses the OpenMined design system with:

- **Colors**: OpenMined's gradient palette (gold, orange, blue, teal, etc.)
- **Typography**: Inter (body) and Rubik (headings) fonts
- **Layout**: Responsive grid system with mobile-first design
- **Components**: Cards, buttons, alerts, and code blocks
- **Dark mode**: Automatic detection with `prefers-color-scheme`

## Features

### 📚 Comprehensive Documentation
- Complete installation instructions
- 5-minute quick start guide
- Step-by-step tutorial series
- Full Python API reference

### 🎨 Modern Design
- Clean, professional styling
- Responsive mobile layout
- Syntax-highlighted code blocks
- Interactive navigation

### 🔍 Developer-Friendly
- Copy-to-clipboard code blocks
- Smooth scrolling navigation
- Search functionality
- Print-friendly styles

### ♿ Accessibility
- Semantic HTML structure
- Keyboard navigation support
- High contrast colors
- Screen reader friendly

## Local Development

To serve the documentation locally:

```bash
# Using Python's built-in server
cd docs
python -m http.server 8000

# Using Node.js serve
npx serve docs

# Using any static file server
```

Then open http://localhost:8000 in your browser.

## Content Updates

### Adding New Pages
1. Create new HTML file using existing pages as templates
2. Include the standard header and footer
3. Link from navigation and relevant index pages
4. Update sitemap if needed

### Updating Styles
- Main styles are in `css/style.css`
- CSS variables at the top control colors and fonts
- Use existing utility classes when possible
- Test on mobile devices

### Adding Interactive Features
- JavaScript goes in `js/main.js`
- Use modern ES6+ syntax
- Test across browsers
- Keep functionality optional (progressive enhancement)

## Deployment

The documentation site is designed to be deployed as static files:

### GitHub Pages
1. Push docs/ directory to repository
2. Enable GitHub Pages in repository settings
3. Set source to `/docs` folder

### Netlify/Vercel
1. Connect repository
2. Set build directory to `docs/`
3. Deploy automatically on commits

### Custom Server
1. Copy docs/ contents to web root
2. Configure server for HTML5 history mode
3. Set up HTTPS

## Browser Support

- **Modern browsers**: Full functionality
- **IE 11**: Basic functionality (no CSS Grid)
- **Mobile**: Responsive design optimized for touch

## Contributing

To contribute to the documentation:

1. Follow the existing style and structure
2. Test on multiple devices and browsers
3. Validate HTML and CSS
4. Check for accessibility issues
5. Update this README if adding new features

## Performance

The site is optimized for performance:
- Minimal external dependencies
- Optimized images and fonts
- Compressed CSS and JavaScript
- Fast loading on slow connections

## License

Same as the main SyftPerm project - MIT License.