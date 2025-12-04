let currentTab = 'text';
let extractedText = '';
let generatedCards = [];
let allDecks = []; // Added to store all decks for filtering

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupFileUpload();
    setupGenerateButton();
    loadDecks(); // Initial load of decks
    setupCategoryFilter(); // Setup category filter on load
});

// Reload decks when page becomes visible (e.g., after navigating back)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        loadDecks();
    }
});

// Reload decks when window gains focus
window.addEventListener('focus', () => {
    loadDecks();
});

// Reload decks when navigating back using browser history
window.addEventListener('pageshow', (event) => {
    // If page is restored from bfcache, reload decks
    if (event.persisted) {
        loadDecks();
    }
});

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const tabId = tab.dataset.tab;
            document.getElementById(`${tabId}-tab`).classList.add('active');
            currentTab = tabId;
        });
    });
}

function setupFileUpload() {
    const pdfInput = document.getElementById('pdfInput');
    pdfInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        document.getElementById('fileName').textContent = `Selected: ${file.name}`;

        const formData = new FormData();
        formData.append('file', file);

        showLoading(true);

        try {
            const response = await fetch('/api/upload-pdf', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                extractedText = data.text;
                showMessage('PDF processed successfully! Text extracted: ' + data.text.length + ' characters', 'success');
            } else {
                showMessage(data.error || 'Error processing PDF', 'error');
            }
        } catch (error) {
            showMessage('Error uploading PDF: ' + error.message, 'error');
        } finally {
            showLoading(false);
        }
    });
}

function setupGenerateButton() {
    document.getElementById('generateBtn').addEventListener('click', generateContent);
}

async function generateContent() {
    let text = '';

    if (currentTab === 'text') {
        text = document.getElementById('textInput').value.trim();
    } else if (currentTab === 'pdf') {
        text = extractedText;
    }

    if (!text) {
        showMessage('Please provide some text or upload a PDF', 'warning');
        return;
    }

    // Increased minimum character count for better card generation
    if (text.length < 100) { 
        showMessage('Text is too short. Please provide at least 100 characters (current: ' + text.length + ')', 'warning');
        return;
    }

    const genType = document.querySelector('input[name="genType"]:checked').value;
    // Allow generating up to 100 cards by default, can be adjusted
    const numCards = parseInt(document.getElementById('numCards').value) || 100; 

    showLoading(true);
    document.getElementById('summaryResult').classList.add('hidden');
    document.getElementById('cardsPreview').classList.add('hidden');

    try {
        const apiKey = localStorage.getItem('gemini_api_key');

        const response = await fetch('/api/process-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                action: genType,
                num_cards: numCards,
                num_questions: numCards, // Ensuring num_questions matches num_cards
                api_key: apiKey
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || 'Error generating content', 'error');
            return;
        }

        if (genType === 'summary') {
            if (data.summary) {
                // Format summary with paragraphs
                const formattedSummary = data.summary.split('\n\n').map(para => 
                    `<p class="summary-paragraph">${escapeHtml(para)}</p>`
                ).join('');
                document.getElementById('summaryContent').innerHTML = formattedSummary;
                document.getElementById('summaryResult').classList.remove('hidden');
            }
        } else if (genType === 'flashcards') {
            if (data.flashcards && Array.isArray(data.flashcards)) {
                generatedCards = data.flashcards;
                displayCardsPreview(generatedCards);
            }
        } else if (genType === 'multiple_choice') {
            if (data.questions && Array.isArray(data.questions)) {
                generatedCards = data.questions;
                displayCardsPreview(generatedCards);
            }
        }

        showMessage('Content generated successfully!', 'success');
    } catch (error) {
        showMessage('Error generating content: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function displayCardsPreview(cards) {
    const container = document.getElementById('cardsContainer');

    if (!cards || !Array.isArray(cards) || cards.length === 0) {
        container.innerHTML = '<p class="empty-state">No cards generated. Please try again.</p>';
        return;
    }

    container.innerHTML = cards.map((card, index) => {
        if (card.choices && Array.isArray(card.choices)) {
            // Multiple Choice Card
            return `
                <div class="card-preview-enhanced multiple-choice-card">
                    <div class="card-number">Question #${index + 1}</div>
                    <div class="card-question">
                        <div class="question-label">Question</div>
                        <div class="question-text">${escapeHtml(card.question || 'No question')}</div>
                    </div>
                    <div class="card-choices">
                        <div class="choices-label">Answer Choices</div>
                        <div class="choices-list">
                            ${card.choices.map((choice, i) => `
                                <div class="choice-item ${choice === card.answer ? 'correct-answer' : ''}">
                                    <span class="choice-letter">${String.fromCharCode(65 + i)}</span>
                                    <span class="choice-text">${escapeHtml(choice)}</span>
                                    ${choice === card.answer ? '<span class="correct-badge">✓ Correct</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Q&A Flashcard
            return `
                <div class="card-preview-enhanced flashcard">
                    <div class="card-number">Card #${index + 1}</div>
                    <div class="card-question">
                        <div class="question-label">Question</div>
                        <div class="question-text">${escapeHtml(card.question || 'No question')}</div>
                    </div>
                    <div class="card-answer">
                        <div class="answer-label">Answer</div>
                        <div class="answer-text">${escapeHtml(card.answer || 'No answer')}</div>
                    </div>
                </div>
            `;
        }
    }).join('');

    document.getElementById('cardsPreview').classList.remove('hidden');
    document.getElementById('saveCardsBtn').onclick = saveCards;
    document.getElementById('exportPdfBtn').onclick = exportPdf;
}

// Prevent concurrent PDF exports
let isExportingPdf = false;

async function exportPdf() {
    if (generatedCards.length === 0) {
        showMessage('No cards to export', 'warning');
        return;
    }

    // Prevent concurrent exports
    if (isExportingPdf) {
        showMessage('Export already in progress', 'warning');
        return;
    }

    const deckName = document.getElementById('deckName').value.trim() || 'Flashcards';
    const exportBtn = document.getElementById('exportPdfBtn');

    // Disable button and show loading state
    const originalText = exportBtn.textContent;
    exportBtn.disabled = true;
    exportBtn.textContent = '📄 Exporting...';
    isExportingPdf = true;

    try {
        const response = await fetch('/api/export-cards-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cards: generatedCards,
                deck_name: deckName
            })
        });

        // Check if response is OK before processing
        if (!response.ok) {
            // Only parse JSON for error responses
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                showMessage(data.error || 'Error exporting PDF', 'error');
            } else {
                showMessage('Error exporting PDF', 'error');
            }
            return;
        }

        // For successful responses, treat as binary blob
        const blob = await response.blob();

        // Verify we got a non-empty blob
        if (blob.size === 0) {
            showMessage('Received empty PDF from server', 'error');
            return;
        }

        // Verify content type from headers (more reliable than blob.type)
        const contentType = response.headers.get('content-type');
        if (contentType && !contentType.includes('application/pdf')) {
            showMessage('Invalid PDF format received', 'error');
            return;
        }

        // Download the PDF
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${deckName.replace(/\s+/g, '_')}_flashcards.pdf`;
        document.body.appendChild(a);
        a.click();

        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showMessage('PDF exported successfully!', 'success');
    } catch (error) {
        showMessage('Error exporting PDF: ' + error.message, 'error');
    } finally {
        // Re-enable button and restore text
        exportBtn.disabled = false;
        exportBtn.textContent = originalText;
        isExportingPdf = false;
    }
}

async function saveCards() {
    const deckName = document.getElementById('deckName').value.trim();
    const category = document.getElementById('categorySelect').value; // Get selected category

    if (!deckName) {
        showMessage('Please enter a deck name', 'warning');
        return;
    }

    if (generatedCards.length === 0) {
        showMessage('No cards to save', 'warning');
        return;
    }

    try {
        // First, create or get the deck, including the category
        const deckResponse = await fetch('/api/decks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: deckName, category: category }) // Include category here
        });

        if (!deckResponse.ok) {
            // If deck with this name and category already exists, get its ID
            if (deckResponse.status === 409) { // Assuming 409 Conflict for existing deck
                const existingDeckData = await deckResponse.json();
                const deckId = existingDeckData.id;

                // Optionally, prompt user if they want to add cards to existing deck or create new one
                // For now, we'll assume we add to it if it exists with the same name and category
                // But this logic might need refinement based on desired behavior
                let addConfirmation = confirm(`Deck "${deckName}" with category "${category}" already exists. Add cards to it?`);
                if (!addConfirmation) {
                    showMessage('Save cancelled. Deck already exists.', 'warning');
                    return;
                }
                
                // We need to re-fetch the deck to get the ID if it was a conflict response
                 const fetchDeckResponse = await fetch(`/api/decks?name=${encodeURIComponent(deckName)}&category=${encodeURIComponent(category)}`);
                 const fetchedDeckData = await fetchDeckResponse.json();
                 const deckIdToUse = fetchedDeckData[0].id; // Assuming it returns an array and we take the first match

                 // Proceed to save cards to this existing deck
                 await saveCardsToDeck(deckIdToUse, deckName, category);

            } else {
                 throw new Error('Failed to create or retrieve deck');
            }
            return; // Exit after handling existing deck scenario
        }

        const deckData = await deckResponse.json();
        const deckId = deckData.id;
        
        await saveCardsToDeck(deckId, deckName, category);

    } catch (error) {
        showMessage('Error saving cards: ' + error.message, 'error');
    }
}

async function saveCardsToDeck(deckId, deckName, category) {
    let savedCount = 0;
    for (const card of generatedCards) {
        // Ensure to include category when saving cards if the API supports it
        const cardResponse = await fetch(`/api/decks/${deckId}/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: card.question,
                answer: card.answer,
                choices: card.choices || null,
                category: category // Assuming the card model also has a category field
            })
        });

        if (cardResponse.ok) {
            savedCount++;
        } else {
             console.error(`Failed to save card: ${card.question}`, await cardResponse.text());
        }
    }

    showMessage(`Deck "${deckName}" (${category}) created/updated with ${savedCount} cards!`, 'success');

    // Clear form and generated cards
    document.getElementById('textInput').value = '';
    document.getElementById('deckName').value = '';
    document.getElementById('categorySelect').value = 'General'; // Reset to default category
    document.getElementById('cardsPreview').classList.add('hidden');
    extractedText = '';
    generatedCards = [];

    await loadDecks(); // Reload decks to reflect changes

    // Navigate to the newly created/updated deck
    setTimeout(() => {
        location.href = `/deck/${deckId}`;
    }, 1000);
}


// New function to load and render decks with category filtering
function loadDecks() {
    try {
        // Add cache busting parameter to force fresh data
        fetch('/api/decks?_t=' + Date.now(), {
            cache: 'no-store'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(decks => {
            allDecks = decks; // Store all decks
            renderDecks(); // Render with default filter (all)
        })
        .catch(error => {
            console.error('Error loading decks:', error);
            showMessage('Error loading decks: ' + error.message, 'error');
        });
    } catch (error) {
        showMessage('Error loading decks: ' + error.message, 'error');
    }
}

function renderDecks(filterCategory = 'all') {
    const decksList = document.getElementById('decksList');
    const filteredDecks = filterCategory === 'all'
        ? allDecks
        : allDecks.filter(deck => deck.category === filterCategory);

    if (filteredDecks.length === 0) {
        decksList.innerHTML = '<p class="empty-state">No flashcard decks in this category yet.</p>';
        return;
    }

    decksList.innerHTML = filteredDecks.map(deck => `
        <div class="deck-card">
            <div class="deck-header">
                <h3>${escapeHtml(deck.name)}</h3>
                <button onclick="deleteDeck(${deck.id})" class="delete-btn" title="Delete deck">🗑️</button>
            </div>
            <p class="deck-description">${escapeHtml(deck.description || 'No description')}</p>
            <div class="deck-stats">
                <span>📂 ${escapeHtml(deck.category || 'General')}</span>
                <span>📚 ${deck.card_count} cards</span>
            </div>
            <div class="deck-actions">
                <a href="/deck/${deck.id}" class="btn secondary-btn">View Cards</a>
                <a href="/study/${deck.id}" class="btn primary-btn">Study</a>
                <a href="/quiz/${deck.id}" class="btn success-btn">Quiz</a>
            </div>
        </div>
    `).join('');
}

// Setup event listener for category filter
function setupCategoryFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', (e) => {
            renderDecks(e.target.value);
        });
    }
}

// Placeholder for deleteDeck function (assuming it exists elsewhere or will be implemented)
function deleteDeck(deckId) {
    if (!confirm('Are you sure you want to delete this deck? This action cannot be undone.')) {
        return;
    }
    fetch(`/api/decks/${deckId}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete deck');
        }
        showMessage('Deck deleted successfully!', 'success');
        loadDecks(); // Reload the deck list
    })
    .catch(error => {
        console.error('Error deleting deck:', error);
        showMessage('Error deleting deck: ' + error.message, 'error');
    });
}


function showLoading(show) {
    const loading = document.getElementById('loading');
    const btn = document.getElementById('generateBtn');

    if (show) {
        loading.classList.remove('hidden');
        btn.disabled = true;
    } else {
        loading.classList.add('hidden');
        btn.disabled = false;
    }
}

function showMessage(message, type = 'info', container = null) {
    // If no container specified, use the main section
    if (!container) {
        container = document.querySelector('section') || document.querySelector('main');
    }

    // Remove existing messages
    const existingMessages = container.querySelectorAll('.inline-message');
    existingMessages.forEach(msg => msg.remove());

    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `inline-message ${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : type === 'warning' ? '⚠' : 'ℹ';
    messageDiv.innerHTML = `<span style="font-size: 1.2rem;">${icon}</span><span>${message}</span>`;

    // Insert at the top of the container
    container.insertBefore(messageDiv, container.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(-10px)';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

function closeBadgeModal() {
    document.getElementById('badgeModal').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('Service Worker registered'))
        .catch(err => console.log('Service Worker registration failed:', err));
}