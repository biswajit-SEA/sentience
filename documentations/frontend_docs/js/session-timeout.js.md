# `session-timeout.js` Documentation

## Overview
This JavaScript file implements two critical security features for the Customer Churn Prediction System:
1. Automatic session timeout management to protect user accounts when inactive
2. CSRF token integration for secure AJAX requests

## Key Features
- Automatic logout after 15 minutes of inactivity
- Activity detection across multiple user interaction types
- Transparent CSRF token injection for all fetch requests
- No user interface disruption during normal usage

## Session Timeout Management

### Timeout Configuration
The script sets up a 15-minute inactivity timer:

```javascript
// Timeout duration in milliseconds (15 minutes)
const SESSION_TIMEOUT = 15 * 60 * 1000;
let timeoutId;
```

### Activity Detection
Monitors multiple user interaction events to detect activity:

```javascript
['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, resetTimer, false);
});
```

### Timer Management
Resets the timer whenever user activity is detected:

```javascript
function resetTimer() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(logoutUser, SESSION_TIMEOUT);
}
```

### Automatic Logout
Redirects to the logout route when the session expires:

```javascript
function logoutUser() {
    // Redirect to logout route
    window.location.href = '/logout';
}
```

## CSRF Protection

### Token Retrieval
Gets the CSRF token from the page metadata:

```javascript
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
```

### Request Interception
Overrides the native `fetch` function to automatically include CSRF tokens:

```javascript
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    if (options.method === 'POST' && !url.includes('://')) {
        options.headers = options.headers || {};
        options.headers['X-CSRFToken'] = csrfToken;
    }
    return originalFetch(url, options);
};
```

This intercepts all `fetch` calls and adds the CSRF token to:
- POST requests only (where CSRF protection is needed)
- Same-origin requests only (excluding external API calls)

## Security Benefits

### Session Security
- Prevents unauthorized access if a user leaves their device unattended
- Protects sensitive admin functions from access after user walks away
- Enforces consistent session timeout policy across the application

### CSRF Protection
- Seamlessly adds CSRF tokens to all AJAX POST requests
- Works with existing form submission handlers without modification
- Prevents cross-site request forgery attacks

## Implementation Notes

### Script Loading
The script is loaded on all protected pages through template inclusion:

```html
<script src="{{ url_for('static', filename='js/session-timeout.js') }}"></script>
```

### Event Initialization
Both features initialize when the DOM is fully loaded:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Implementation code
});
```

### Integration
- Works alongside other JavaScript files without conflicts
- No dependencies on external libraries
- Compatible with modern browsers