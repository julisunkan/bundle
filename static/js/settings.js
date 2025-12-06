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