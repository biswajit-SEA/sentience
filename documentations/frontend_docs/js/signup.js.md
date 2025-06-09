# `signup.js` Documentation

## Overview
This JavaScript file implements the user registration flow with a secure two-step verification process using one-time passwords (OTP). It includes real-time password strength validation, form validation, OTP generation and verification, and secure account creation.

## Key Features
- Real-time password strength evaluation
- Visual password requirement indicators
- Password visibility toggle
- Form validation with detailed error messages
- Email verification with time-limited OTP
- CSRF protection for secure form submission
- reCAPTCHA integration for bot prevention

## Password Validation System

### Strength Indicators
```javascript
const passwordStrength = document.getElementById("passwordStrength");
const strengthMeterFill = document.getElementById("strengthMeterFill");
```

The script visualizes password strength with:
- Color-coded text indicator (very weak, weak, medium, strong)
- Progress bar that fills based on strength level
- Requirement checkboxes that update in real-time

### Password Requirements
The system checks for five password requirements:
1. Minimum length (8 characters)
2. Uppercase letters
3. Lowercase letters
4. Numbers
5. Special characters

```javascript
// Check each requirement
if (password.length >= 8) {
  lengthReq.classList.add("fulfilled");
  lengthReq.classList.remove("unfulfilled");
  lengthReq.querySelector(".requirement-icon").textContent = "✓";
} else {
  lengthReq.classList.add("unfulfilled");
  lengthReq.classList.remove("fulfilled");
  lengthReq.querySelector(".requirement-icon").textContent = "✕";
}
```

### Common Password Detection
```javascript
const commonPasswords = [
  "123456", "password", "123456789", "12345678", "12345",
  // ...more common passwords
];

// Common password check
if (commonPasswords.includes(password)) {
  commonPasswordWarning.style.display = "block";
} else {
  commonPasswordWarning.style.display = "none";
}
```

## OTP Verification Flow

### OTP Container Elements
```javascript
const otpContainer = document.getElementById("otpContainer");
const otpFields = document.querySelectorAll(".otp-field");
const otpTimer = document.getElementById("otpTimer");
const resendOtpBtn = document.getElementById("resendOtpBtn");
```

### Form Submission and OTP Request
1. Form validation occurs on submit
2. User data is collected and stored temporarily
3. Request is sent to the server to generate and email an OTP
4. UI transitions to OTP verification screen

```javascript
signupForm.addEventListener("submit", function (event) {
  event.preventDefault();
  // Validate form
  // ...
  if (isValid) {
    // Store the form data
    userData = {
      name: nameInput.value.trim(),
      email: emailInput.value.trim(),
      password: passwordInput.value,
      csrf_token: document.querySelector('input[name="csrf_token"]').value,
      recaptcha: recaptchaResponse
    };
    
    // Request OTP through AJAX
    requestOTP();
  }
});
```

### OTP Input Management
The script implements an enhanced user experience for OTP entry:
- Auto-focus to next field after number entry
- Backspace to previous field when empty
- Support for paste operation (for the full 6-digit code)
- Auto-enable verification button when all fields are filled

```javascript
otpFields.forEach((field, index) => {
  field.addEventListener('keyup', (e) => {
    // Move to next field after digit entry
    if (/^[0-9]$/.test(e.key) && index < otpFields.length - 1) {
      otpFields[index + 1].focus();
    }
    // Enable verify button if all fields have a value
    checkVerifyButton();
  });
  
  // Handle paste event for OTP
  field.addEventListener('paste', (e) => {
    e.preventDefault();
    const paste = (e.clipboardData || window.clipboardData).getData('text');
    // If the pasted content contains 6 digits, fill all fields
    if (/^\d{6}$/.test(paste)) {
      for (let i = 0; i < otpFields.length; i++) {
        otpFields[i].value = paste.charAt(i);
      }
      // Enable verify button
      checkVerifyButton();
    }
  });
});
```

### OTP Timer Implementation
The OTP has a limited validity period (3 minutes), displayed with a countdown timer:
- Timer starts when OTP is requested
- Updates every second
- Disables verification when expired
- Prevents immediate resend requests (30-second cooldown)

```javascript
function startOtpTimer() {
  // Clear any existing timer
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  
  // Set expiry time to 3 minutes from now
  otpExpiryTime = new Date().getTime() + (3 * 60 * 1000);
  
  // Update timer display immediately and then every second
  updateTimerDisplay();
  timerInterval = setInterval(updateTimerDisplay, 1000);
  
  // Disable resend button for first 30 seconds
  resendOtpBtn.disabled = true;
  setTimeout(() => {
    resendOtpBtn.disabled = false;
  }, 30000);
}
```

## API Integration

### Request OTP Endpoint
```javascript
fetch('/request_otp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': userData.csrf_token
  },
  body: JSON.stringify({
    email: userData.email,
    name: userData.name,
    recaptcha: userData.recaptcha
  })
})
```

### Verify OTP and Account Creation
```javascript
fetch('/verify_otp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': userData.csrf_token
  },
  body: JSON.stringify({
    email: userData.email,
    otp: otpValue,
    userData: userData // Send all user data for account creation
  })
})
```

## Loading States

### Request Spinners
Visual indicators for asynchronous operations:
- Form submission spinner
- OTP verification spinner
- Resend OTP spinner

```javascript
// Show spinner and disable button
requestOtpBtn.disabled = true;
requestOtpBtn.textContent = "Sending...";
formSpinner.classList.add('active');
```

## Error Handling

### Form Validation Errors
```javascript
if (!emailPattern.test(emailInput.value)) {
  emailError.textContent = "Please enter a valid email address";
  emailInput.style.borderColor = "red";
  isValid = false;
} else {
  emailError.textContent = "";
  emailInput.style.borderColor = "";
}
```

### API Error Handling
```javascript
.catch(error => {
  console.error('Error:', error);
  otpSpinner.classList.remove('active');
  otpError.textContent = "An error occurred. Please try again later.";
  resendOtpBtn.disabled = false;
});
```

## Security Features

- CSRF token inclusion in all API requests
- reCAPTCHA verification
- Timed OTP expiration
- Password strength requirements
- Limited OTP attempts
- Cooldown periods for OTP resend