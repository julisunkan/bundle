document.addEventListener('DOMContentLoaded', () => {
    loadApiKey();
});

function loadApiKey() {
    const apiKey = localStorage.getItem('gemini_api_key');
    if (apiKey) {
        document.getElementById('apiKeyInput').value = apiKey;
        showStatus('✓ API key loaded', 'success');
    }
}

function saveApiKey() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();

    if (!apiKey) {
        showStatus('⚠ Please enter an API key', 'warning');
        return;
    }

    localStorage.setItem('gemini_api_key', apiKey);
    showStatus('✓ API key saved successfully!', 'success');
}

async function testApiKey() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();

    if (!apiKey) {
        showStatus('⚠ Please enter an API key first', 'warning');
        return;
    }

    showStatus('⏳ Testing API key...', 'info');

    try {
        const response = await fetch('/api/test-gemini', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('✓ API key is valid and working!', 'success');
            localStorage.setItem('gemini_api_key', apiKey);
        } else {
            showStatus('✗ ' + (data.error || 'API key test failed'), 'error');
        }
    } catch (error) {
        showStatus('✗ Error testing API key: ' + error.message, 'error');
    }
}

function clearApiKey() {
    if (confirm('Are you sure you want to clear your API key?')) {
        localStorage.removeItem('gemini_api_key');
        document.getElementById('apiKeyInput').value = '';
        showStatus('✓ API key cleared', 'success');
    }
}

function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('apiStatus');
    statusEl.textContent = message;

    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };

    statusEl.style.color = colors[type] || colors.info;

    // Auto-clear after 5 seconds
    setTimeout(() => {
        statusEl.textContent = '';
    }, 5000);
}

async function generateDeck() {
            const deckName = document.getElementById('genDeckName').value.trim();
            const deckDescription = document.getElementById('genDeckDescription').value.trim();
            const topic = document.getElementById('genTopic').value.trim();
            const numCards = parseInt(document.getElementById('genNumCards').value) || 10;
            const category = document.getElementById('genCategory').value;
            const apiKey = document.getElementById('genApiKey').value.trim();
            const statusEl = document.getElementById('genStatus');

            if (!deckName) {
                statusEl.textContent = '⚠ Please enter a deck name';
                statusEl.style.color = '#ff8c00';
                return;
            }

            if (!topic) {
                statusEl.textContent = '⚠ Please describe the topic';
                statusEl.style.color = '#ff8c00';
                return;
            }

            statusEl.textContent = '⏳ Generating deck...';
            statusEl.style.color = '#3b82f6';

            try {
                // Create deck
                const deckResponse = await fetch('/api/decks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        name: deckName, 
                        description: deckDescription || `AI-generated deck about: ${topic}`,
                        category: category 
                    })
                });

                if (!deckResponse.ok) {
                    const errorData = await deckResponse.json();
                    throw new Error(errorData.error || 'Failed to create deck');
                }

                const deckData = await deckResponse.json();
                const deckId = deckData.id;

                // Generate cards
                const cardsResponse = await fetch('/api/decks/' + deckId + '/generate-cards', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        topic: topic, 
                        num_cards: numCards, 
                        api_key: apiKey 
                    })
                });

                if (!cardsResponse.ok) {
                    const errorData = await cardsResponse.json();
                    throw new Error(errorData.error || 'Failed to generate cards');
                }

                const cardsData = await cardsResponse.json();
                statusEl.textContent = '✓ Deck and cards generated successfully!';
                statusEl.style.color = '#10b981';

                // Clear form
                document.getElementById('genDeckName').value = '';
                document.getElementById('genDeckDescription').value = '';
                document.getElementById('genTopic').value = '';
                document.getElementById('genNumCards').value = '10';
                document.getElementById('genCategory').value = 'General';

            } catch (error) {
                statusEl.textContent = '✗ ' + error.message;
                statusEl.style.color = '#ef4444';
            }
        }