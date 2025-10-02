// Main JavaScript file for JSON Converter
// Additional utility functions and enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    console.log('JSON Converter initialized');
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to convert text
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const convertBtn = document.getElementById('convert-text-btn');
            if (convertBtn && document.getElementById('json-input').value.trim()) {
                e.preventDefault();
                convertBtn.click();
            }
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            const modal = document.getElementById('progress-modal');
            if (modal && modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        }
    });

    // Add drag and drop functionality for file inputs
    setupDragAndDrop();
    
    // Add auto-resize for textareas
    setupTextareaAutoResize();
    
    // Add copy functionality for output textarea
    setupCopyFunctionality();
});

function setupDragAndDrop() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const wrapper = input.closest('.file-input-wrapper');
        const label = wrapper.querySelector('.file-input-label');
        
        if (!wrapper || !label) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            wrapper.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            wrapper.addEventListener(eventName, () => {
                label.classList.add('drag-highlight');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            wrapper.addEventListener(eventName, () => {
                label.classList.remove('drag-highlight');
            }, false);
        });

        // Handle dropped files
        wrapper.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                // Trigger change event
                const changeEvent = new Event('change', { bubbles: true });
                input.dispatchEvent(changeEvent);
            }
        }, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function setupTextareaAutoResize() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        // Set initial height
        autoResize(textarea);
        
        // Auto-resize on input
        textarea.addEventListener('input', () => autoResize(textarea));
    });
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 200) + 'px';
}

function setupCopyFunctionality() {
    const outputTextarea = document.getElementById('json-output');
    
    if (outputTextarea) {
        // Add double-click to select all
        outputTextarea.addEventListener('dblclick', function() {
            this.select();
        });
        
        // Add context menu with copy option
        outputTextarea.addEventListener('contextmenu', function(e) {
            if (this.value.trim()) {
                // Let the browser handle the context menu
                return true;
            }
            e.preventDefault();
        });
    }
}

// Utility function to format JSON
function formatJSON(jsonString) {
    try {
        const obj = JSON.parse(jsonString);
        return JSON.stringify(obj, null, 2);
    } catch (e) {
        return jsonString;
    }
}

// Utility function to validate JSON
function isValidJSON(jsonString) {
    try {
        JSON.parse(jsonString);
        return true;
    } catch (e) {
        return false;
    }
}

// Add validation for JSON input
document.addEventListener('DOMContentLoaded', function() {
    const jsonInput = document.getElementById('json-input');
    const convertBtn = document.getElementById('convert-text-btn');
    
    if (jsonInput && convertBtn) {
        jsonInput.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (value) {
                if (isValidJSON(value)) {
                    this.style.borderColor = '#38a169';
                    convertBtn.disabled = false;
                } else {
                    this.style.borderColor = '#e53e3e';
                    convertBtn.disabled = false; // Let server handle the error
                }
            } else {
                this.style.borderColor = '#cbd5e0';
                convertBtn.disabled = false;
            }
        });
    }
});

// Add CSS for drag and drop highlight
const style = document.createElement('style');
style.textContent = `
    .drag-highlight {
        background: #e6fffa !important;
        border-color: #38a169 !important;
        color: #38a169 !important;
    }
    
    .file-input-label.drag-highlight i {
        color: #38a169 !important;
    }
`;
document.head.appendChild(style);