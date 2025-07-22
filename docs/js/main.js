// Main JavaScript for syft-installer documentation
document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    initializeTabs();
    
    // Copy to clipboard functionality
    initializeCopyButtons();
    
    // Smooth scrolling for anchor links
    initializeSmoothScrolling();
    
    // Header scroll effects
    initializeHeaderEffects();
});

// Tab functionality for examples section
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            const targetPane = document.getElementById(targetTab);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

// Copy to clipboard functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            
            if (navigator.clipboard && window.isSecureContext) {
                // Modern clipboard API
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showCopyFeedback(this);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                    fallbackCopyTextToClipboard(textToCopy, this);
                });
            } else {
                // Fallback for older browsers
                fallbackCopyTextToClipboard(textToCopy, this);
            }
        });
    });
}

// Fallback copy method for older browsers
function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopyFeedback(button);
        } else {
            console.error('Fallback: Failed to copy');
        }
    } catch (err) {
        console.error('Fallback: Unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

// Show visual feedback when text is copied
function showCopyFeedback(button) {
    const originalText = button.textContent;
    button.textContent = '✅';
    button.style.color = 'var(--color-success)';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.color = '';
    }, 2000);
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#" or empty
            if (href === '#' || href === '') {
                return;
            }
            
            const targetElement = document.querySelector(href);
            
            if (targetElement) {
                e.preventDefault();
                
                // Calculate offset for fixed header
                const headerHeight = document.querySelector('header').offsetHeight;
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerHeight - 20; // 20px extra padding
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Header scroll effects
function initializeHeaderEffects() {
    const header = document.querySelector('header');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add/remove shadow based on scroll position
        if (scrollTop > 10) {
            header.style.boxShadow = 'var(--shadow)';
        } else {
            header.style.boxShadow = 'none';
        }
        
        lastScrollTop = scrollTop;
    });
}

// Syntax highlighting for code blocks (simple version)
function initializeSyntaxHighlighting() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(block => {
        const language = block.className.replace('language-', '');
        
        if (language === 'python') {
            highlightPython(block);
        } else if (language === 'bash') {
            highlightBash(block);
        }
    });
}

// Simple Python syntax highlighting
function highlightPython(block) {
    let html = block.innerHTML;
    
    // Keywords
    const keywords = ['import', 'as', 'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None'];
    keywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'g');
        html = html.replace(regex, `<span class="keyword">${keyword}</span>`);
    });
    
    // Strings
    html = html.replace(/(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, '<span class="string">$1$2$1</span>');
    
    // Comments
    html = html.replace(/(#.*$)/gm, '<span class="comment">$1</span>');
    
    block.innerHTML = html;
}

// Simple Bash syntax highlighting
function highlightBash(block) {
    let html = block.innerHTML;
    
    // Commands
    html = html.replace(/^(\$\s+)([a-zA-Z0-9_-]+)/gm, '$1<span class="command">$2</span>');
    
    // Comments
    html = html.replace(/(#.*$)/gm, '<span class="comment">$1</span>');
    
    // Export statements
    html = html.replace(/\b(export)\b/g, '<span class="keyword">$1</span>');
    
    block.innerHTML = html;
}

// Add CSS for syntax highlighting
function addSyntaxHighlightingCSS() {
    const style = document.createElement('style');
    style.textContent = `
        .keyword {
            color: #ff7b72;
            font-weight: 600;
        }
        
        .string {
            color: #a5d6ff;
        }
        
        .comment {
            color: #8b949e;
            font-style: italic;
        }
        
        .command {
            color: #79c0ff;
            font-weight: 600;
        }
    `;
    document.head.appendChild(style);
}

// Initialize syntax highlighting when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    addSyntaxHighlightingCSS();
    initializeSyntaxHighlighting();
});

// Utility function to check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Add animation on scroll (optional enhancement)
function initializeScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .workflow-item, .tech-item');
    
    function checkAnimation() {
        animatedElements.forEach(element => {
            if (isInViewport(element)) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Initial setup
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // Check on scroll
    window.addEventListener('scroll', checkAnimation);
    
    // Check initially
    checkAnimation();
}

// Initialize scroll animations (optional)
document.addEventListener('DOMContentLoaded', function() {
    // Uncomment to enable scroll animations
    // initializeScrollAnimations();
});