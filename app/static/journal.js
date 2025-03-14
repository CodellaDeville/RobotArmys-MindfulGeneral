// Journal Module for Mindful General
const journalModule = {
    // Store for journal entries
    entries: [],

    // Initialize the journal module
    init() {
        console.log('Journal module initializing...'); // Debug log
        this.loadEntries();
        this.createModal();
        this.setupEventListeners();
    },

    // Create the modal HTML structure with ARIA attributes
    createModal() {
        console.log('Creating journal modal...'); // Debug log
        const modal = document.createElement('div');
        modal.id = 'journalModal';
        modal.className = 'journal-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', 'journalTitle');
        modal.setAttribute('aria-modal', 'true');

        modal.innerHTML = `
            <div class="journal-modal-content">
                <h2 id="journalTitle" tabindex="-1">Personal Journal</h2>
                <button id="closeJournal" 
                        aria-label="Close journal" 
                        class="close-button">&times;</button>
                
                <div class="journal-input-section">
                    <label for="journalEntry">Record your thoughts and experiences:</label>
                    <select id="entryType" aria-label="Select entry type">
                        <option value="general">General Reflection</option>
                        <option value="incident">Incident Processing</option>
                        <option value="progress">Progress Note</option>
                        <option value="trigger">Trigger Management</option>
                        <option value="goals">Goals & Achievements</option>
                    </select>
                    <textarea 
                        id="journalEntry" 
                        rows="5" 
                        aria-label="Journal entry text area"
                        placeholder="This is a private space to process your experiences, track your progress, or work through challenging moments. Your entries are stored only on your device."></textarea>
                    <div class="entry-tools">
                        <button id="saveEntry" 
                                aria-label="Save journal entry">Save Entry</button>
                        <button id="clearEntry" 
                                aria-label="Clear current entry"
                                class="secondary-button">Clear</button>
                    </div>
                </div>

                <div class="journal-entries" 
                     role="log" 
                     aria-label="Previous journal entries">
                    <h3>Previous Entries</h3>
                    <div id="entriesList" class="entries-list"></div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        console.log('Journal modal created and added to DOM'); // Debug log
    },

    // Set up event listeners
    setupEventListeners() {
        console.log('Setting up event listeners...'); // Debug log
        const journalBtn = document.getElementById('journalButton');
        const modal = document.getElementById('journalModal');
        const closeBtn = document.getElementById('closeJournal');
        const saveBtn = document.getElementById('saveEntry');
        const clearBtn = document.getElementById('clearEntry');

        if (!journalBtn || !modal || !closeBtn || !saveBtn || !clearBtn) {
            console.error('Required journal elements not found');
            return;
        }

        // Make journal button in nav accessible
        journalBtn.setAttribute('aria-label', 'Open journal');
        journalBtn.setAttribute('role', 'button');

        // Use a direct click handler instead of an arrow function
        journalBtn.onclick = () => this.openModal();

        closeBtn.onclick = () => this.closeModal();
        saveBtn.onclick = () => this.saveEntry();
        clearBtn.onclick = () => this.clearEntry();

        // Keyboard accessibility
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                console.log('ESC key pressed - closing modal'); // Debug log
                this.closeModal();
            }
            if (e.key === 'Enter' && e.ctrlKey) {
                this.saveEntry();
            }
        });

        // Announce when journal is opened/closed
        modal.addEventListener('show', () => {
            this.announceToScreenReader('Journal opened');
        });

        modal.addEventListener('hide', () => {
            this.announceToScreenReader('Journal closed');
        });

        console.log('Event listeners setup complete'); // Debug log
    },

    // Open the modal
    openModal() {
        console.log('Opening modal...'); // Debug log
        const modal = document.getElementById('journalModal');
        if (!modal) {
            console.error('Cannot open modal - element not found');
            return;
        }
        modal.classList.add('active');
        modal.style.display = 'flex';
        document.getElementById('journalTitle').focus();
        modal.dispatchEvent(new Event('show'));
        console.log('Modal opened'); // Debug log
    },

    // Close the modal
    closeModal() {
        console.log('Closing modal...'); // Debug log
        const modal = document.getElementById('journalModal');
        if (!modal) {
            console.error('Cannot close modal - element not found');
            return;
        }
        modal.classList.remove('active');
        modal.style.display = 'none';
        document.getElementById('journalButton').focus();
        modal.dispatchEvent(new Event('hide'));
        console.log('Modal closed'); // Debug log
    },

    // Clear the current entry
    clearEntry() {
        const textarea = document.getElementById('journalEntry');
        if (textarea && confirm('Clear current entry? This cannot be undone.')) {
            textarea.value = '';
            textarea.focus();
        }
    },

    // Save a new entry
    saveEntry() {
        const entryText = document.getElementById('journalEntry').value.trim();
        const entryType = document.getElementById('entryType').value;
        
        if (!entryText) {
            this.announceToScreenReader('Please enter some text before saving');
            return;
        }

        const entry = {
            id: Date.now(),
            type: entryType,
            text: entryText,
            date: new Date().toLocaleString()
        };

        this.entries.unshift(entry);
        this.saveEntries();
        this.displayEntries();
        document.getElementById('journalEntry').value = '';
        
        this.announceToScreenReader('Entry saved successfully');
    },

    // Load entries from localStorage
    loadEntries() {
        const savedEntries = localStorage.getItem('journalEntries');
        this.entries = savedEntries ? JSON.parse(savedEntries) : [];
        this.displayEntries();
    },

    // Save entries to localStorage
    saveEntries() {
        localStorage.setItem('journalEntries', JSON.stringify(this.entries));
    },

    // Display entries in the modal
    displayEntries() {
        const entriesList = document.getElementById('entriesList');
        if (!entriesList) {
            console.error('Entries list element not found');
            return;
        }
        entriesList.innerHTML = '';

        this.entries.forEach((entry) => {
            const entryElement = document.createElement('div');
            entryElement.className = 'journal-entry';
            entryElement.setAttribute('role', 'article');
            
            const typeLabel = {
                general: 'General Reflection',
                incident: 'Incident Processing',
                progress: 'Progress Note',
                trigger: 'Trigger Management',
                goals: 'Goals & Achievements'
            }[entry.type] || entry.type;

            entryElement.innerHTML = `
                <div class="entry-header">
                    <span class="entry-type" aria-label="Entry type: ${typeLabel}">${typeLabel}</span>
                    <span class="entry-date" aria-label="Entry from ${entry.date}">${entry.date}</span>
                </div>
                <p class="entry-text">${entry.text}</p>
                <div class="entry-actions">
                    <button 
                        class="delete-entry" 
                        aria-label="Delete entry from ${entry.date}"
                        onclick="journalModule.deleteEntry(${entry.id})">
                        Delete
                    </button>
                </div>
            `;
            entriesList.appendChild(entryElement);
        });
    },

    // Delete an entry
    deleteEntry(id) {
        const entryToDelete = this.entries.find(entry => entry.id === id);
        if (confirm('Delete this entry? This cannot be undone.')) {
            this.entries = this.entries.filter(entry => entry.id !== id);
            this.saveEntries();
            this.displayEntries();
            this.announceToScreenReader('Entry deleted');
        }
    },

    // Helper function to announce messages to screen readers
    announceToScreenReader(message) {
        let announce = document.getElementById('sr-announce');
        if (!announce) {
            announce = document.createElement('div');
            announce.id = 'sr-announce';
            announce.setAttribute('role', 'alert');
            announce.setAttribute('aria-live', 'polite');
            announce.className = 'sr-only';
            document.body.appendChild(announce);
        }
        announce.textContent = message;
    }
}; 