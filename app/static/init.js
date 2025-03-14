// Initialize all modules when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded - initializing modules...'); // Debug log
    
    // Initialize the journal module
    if (typeof journalModule !== 'undefined') {
        console.log('Found journal module - initializing...'); // Debug log
        journalModule.init();
    } else {
        console.error('Journal module not found!'); // Debug log
    }
}); 