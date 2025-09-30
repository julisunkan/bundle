// Client-side admin password gate
// WARNING: This is NOT secure - credentials can be easily found in the source code

(function() {
    'use strict';
    
    const ADMIN_USERNAME = 'julisunkan';
    const ADMIN_PASSWORD = 'bidexy88';
    const SESSION_KEY = 'admin_authenticated';
    
    function isAuthenticated() {
        return sessionStorage.getItem(SESSION_KEY) === 'true';
    }
    
    function authenticate(username, password) {
        if (username === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
            sessionStorage.setItem(SESSION_KEY, 'true');
            return true;
        }
        return false;
    }
    
    function logout() {
        sessionStorage.removeItem(SESSION_KEY);
        window.location.reload();
    }
    
    function showLoginModal() {
        const mainContent = document.querySelector('body > *:not(script)');
        
        const modal = document.createElement('div');
        modal.id = 'admin-gate-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
            ">
                <h2 style="margin: 0 0 20px 0; color: #333; text-align: center;">
                    Admin Access
                </h2>
                <form id="adminLoginForm" style="display: flex; flex-direction: column; gap: 15px;">
                    <div>
                        <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">
                            Username
                        </label>
                        <input 
                            type="text" 
                            id="adminUsername" 
                            style="
                                width: 100%;
                                padding: 10px;
                                border: 2px solid #ddd;
                                border-radius: 6px;
                                font-size: 14px;
                                box-sizing: border-box;
                            "
                            required
                            autocomplete="off"
                        />
                    </div>
                    <div>
                        <label style="display: block; margin-bottom: 5px; color: #555; font-weight: 500;">
                            Password
                        </label>
                        <input 
                            type="password" 
                            id="adminPassword" 
                            style="
                                width: 100%;
                                padding: 10px;
                                border: 2px solid #ddd;
                                border-radius: 6px;
                                font-size: 14px;
                                box-sizing: border-box;
                            "
                            required
                        />
                    </div>
                    <div id="errorMessage" style="
                        color: #dc3545;
                        font-size: 14px;
                        display: none;
                        text-align: center;
                    ">
                        Invalid username or password
                    </div>
                    <button 
                        type="submit"
                        style="
                            padding: 12px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            border-radius: 6px;
                            font-size: 16px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: transform 0.2s;
                        "
                        onmouseover="this.style.transform='scale(1.02)'"
                        onmouseout="this.style.transform='scale(1)'"
                    >
                        Login
                    </button>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        document.body.style.visibility = 'visible';
        
        const form = document.getElementById('adminLoginForm');
        const usernameInput = document.getElementById('adminUsername');
        const passwordInput = document.getElementById('adminPassword');
        const errorMessage = document.getElementById('errorMessage');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = usernameInput.value;
            const password = passwordInput.value;
            
            if (authenticate(username, password)) {
                document.getElementById('admin-gate-modal').remove();
                document.body.style.overflow = '';
                showContent();
            } else {
                errorMessage.style.display = 'block';
                passwordInput.value = '';
                usernameInput.focus();
            }
        });
        
        usernameInput.focus();
    }
    
    function hideContent() {
        const content = document.querySelector('body');
        content.style.visibility = 'hidden';
        document.body.style.overflow = 'hidden';
    }
    
    function showContent() {
        const content = document.querySelector('body');
        content.style.visibility = 'visible';
        document.body.style.overflow = '';
    }
    
    function init() {
        if (!isAuthenticated()) {
            hideContent();
            showLoginModal();
        }
    }
    
    // Add logout button functionality
    window.adminLogout = logout;
    
    // Check authentication on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
