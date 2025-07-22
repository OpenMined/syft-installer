// ================================
// Copy to Clipboard Functionality
// ================================
document.addEventListener('DOMContentLoaded', function() {
    // Add copy functionality to all copy buttons
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const textToCopy = this.getAttribute('data-copy');
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                
                // Show success state
                this.classList.add('copied');
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                
                // Reset after 2 seconds
                setTimeout(() => {
                    this.classList.remove('copied');
                    this.textContent = originalText;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
    });
    
    // ================================
    // Basic Syntax Highlighting
    // ================================
    const codeBlocks = document.querySelectorAll('code.language-python');
    
    codeBlocks.forEach(block => {
        // Get the raw text content
        let text = block.textContent || '';
        
        // Store original text for processing
        const lines = text.split('\n');
        const processedLines = lines.map(line => {
            // First escape HTML
            let processedLine = line
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            
            // Check if this line has a comment
            const commentIndex = processedLine.indexOf('#');
            let beforeComment = processedLine;
            let commentPart = '';
            
            if (commentIndex !== -1) {
                // Check if # is inside a string
                const beforeHash = processedLine.substring(0, commentIndex);
                const singleQuotes = (beforeHash.match(/'/g) || []).length;
                const doubleQuotes = (beforeHash.match(/"/g) || []).length;
                
                // If both are even, # is not in a string
                if (singleQuotes % 2 === 0 && doubleQuotes % 2 === 0) {
                    beforeComment = processedLine.substring(0, commentIndex);
                    commentPart = processedLine.substring(commentIndex);
                }
            }
            
            // Process the non-comment part
            // Handle strings first
            beforeComment = beforeComment.replace(/"([^"]*)"/g, '<span class="string">"$1"</span>');
            beforeComment = beforeComment.replace(/'([^']*)'/g, '<span class="string">\'$1\'</span>');
            
            // Handle functions
            beforeComment = beforeComment.replace(/\b([a-zA-Z_]\w*)\s*\(/g, '<span class="function">$1</span>(');
            
            // Handle keywords - only if not already inside a span
            const keywords = ['import', 'from', 'if', 'else', 'elif', 'def', 'class', 'return', 
                            'for', 'while', 'in', 'or', 'and', 'not', 'True', 'False', 'None', 'print'];
            
            keywords.forEach(keyword => {
                // More precise regex that won't match inside tags
                const regex = new RegExp(`\\b(${keyword})\\b(?![^<]*>|[^<]*</span>)`, 'g');
                beforeComment = beforeComment.replace(regex, '<span class="keyword">$1</span>');
            });
            
            // Add comment part with styling if it exists
            if (commentPart) {
                commentPart = '<span class="comment">' + commentPart + '</span>';
            }
            
            return beforeComment + commentPart;
        });
        
        // Join lines and set the HTML
        block.innerHTML = processedLines.join('\n');
    });
    
    // ================================
    // YAML Syntax Highlighting
    // ================================
    const yamlBlocks = document.querySelectorAll('code.language-yaml');
    
    yamlBlocks.forEach(block => {
        // Get the raw text content
        let text = block.textContent || '';
        
        // Process line by line
        const lines = text.split('\n');
        const processedLines = lines.map(line => {
            // First escape HTML
            let processedLine = line
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            
            // Check if this line has a comment
            const commentIndex = processedLine.indexOf('#');
            let beforeComment = processedLine;
            let commentPart = '';
            
            if (commentIndex !== -1) {
                // Check if # is inside a string
                const beforeHash = processedLine.substring(0, commentIndex);
                const singleQuotes = (beforeHash.match(/'/g) || []).length;
                const doubleQuotes = (beforeHash.match(/"/g) || []).length;
                
                // If both are even, # is not in a string
                if (singleQuotes % 2 === 0 && doubleQuotes % 2 === 0) {
                    beforeComment = processedLine.substring(0, commentIndex);
                    commentPart = processedLine.substring(commentIndex);
                }
            }
            
            // Process the non-comment part
            // Handle strings first
            beforeComment = beforeComment.replace(/"([^"]*)"/g, '<span class="string">"$1"</span>');
            beforeComment = beforeComment.replace(/'([^']*)'/g, '<span class="string">\'$1\'</span>');
            
            // Handle list items (dash)
            beforeComment = beforeComment.replace(/^(\s*)(-)(\s+)/, '$1<span class="keyword">$2</span>$3');
            
            // Handle keys (before colon) - only if not inside a string span
            beforeComment = beforeComment.replace(/^(\s*)([a-zA-Z_-]+)(?=:)/, '$1<span class="keyword">$2</span>');
            
            // Add comment part with styling if it exists
            if (commentPart) {
                commentPart = '<span class="comment">' + commentPart + '</span>';
            }
            
            return beforeComment + commentPart;
        });
        
        // Join lines and set the HTML
        block.innerHTML = processedLines.join('\n');
    });
    
    // ================================
    // Smooth Scroll for Anchor Links
    // ================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ================================
    // Add Active State to Current Page
    // ================================
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath || 
            (currentPath.endsWith('/') && link.getAttribute('href') === 'index.html')) {
            link.classList.add('active');
        }
    });
});

// ================================
// Mobile Menu Toggle (if needed)
// ================================
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('mobile-active');
}