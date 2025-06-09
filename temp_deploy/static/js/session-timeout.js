// Session timeout functionality
document.addEventListener('DOMContentLoaded', function() {
    // Timeout duration in milliseconds (15 minutes)
    const SESSION_TIMEOUT = 15 * 60 * 1000;
    let timeoutId;

    // Function to reset the timer
    function resetTimer() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(logoutUser, SESSION_TIMEOUT);
    }

    // Function to logout the user
    function logoutUser() {
        // Redirect to logout route
        window.location.href = '/logout';
    }

    // Watching for user activity to reset timer
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetTimer, false);
    });

    resetTimer();
});

// Script to handle CSRF token refresh
document.addEventListener('DOMContentLoaded', function() {
    // For AJAX requests, add CSRF token to all requests
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    if (csrfToken) {
        // Adding CSRF token to AJAX requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (options.method === 'POST' && !url.includes('://')) {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = csrfToken;
            }
            return originalFetch(url, options);
        };
    }
});