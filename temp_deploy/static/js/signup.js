// Real-time password validation
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");
const passwordStrength = document.getElementById("passwordStrength");
const commonPasswordWarning = document.getElementById("commonPasswordWarning");
const strengthMeterFill = document.getElementById("strengthMeterFill");

// Get requirement elements
const lengthReq = document.getElementById("length-requirement");
const uppercaseReq = document.getElementById("uppercase-requirement");
const lowercaseReq = document.getElementById("lowercase-requirement");
const numberReq = document.getElementById("number-requirement");
const specialReq = document.getElementById("special-requirement");

const commonPasswords = [
  "123456",
  "password",
  "123456789",
  "12345678",
  "12345",
  "1234567",
  "qwerty",
  "abc123",
  "password1",
  "123123",
];

// OTP Verification references
const signupForm = document.getElementById("signupForm");
const otpContainer = document.getElementById("otpContainer");
const otpFields = document.querySelectorAll(".otp-field");
const otpTimer = document.getElementById("otpTimer");
const resendOtpBtn = document.getElementById("resendOtpBtn");
const otpSpinner = document.getElementById("otpSpinner");
const otpError = document.getElementById("otpError");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");

// Keep track of user data after form submission
let userData = {};
let timerInterval;
let otpExpiryTime;

const confirmPasswordInput = document.getElementById("confirm_password");
const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
const confirmPasswordError = document.getElementById("confirmPasswordError");

// Real-time validation for confirm password match
confirmPasswordInput.addEventListener("input", function () {
  if (this.value === passwordInput.value) {
    confirmPasswordError.textContent = "";
    confirmPasswordInput.style.borderColor = "";
  } else {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
  }
});

passwordInput.addEventListener("input", function () {
  const password = this.value;

  // Check each requirement
  // 1. Length check
  if (password.length >= 8) {
    lengthReq.classList.add("fulfilled");
    lengthReq.classList.remove("unfulfilled");
    lengthReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    lengthReq.classList.add("unfulfilled");
    lengthReq.classList.remove("fulfilled");
    lengthReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 2. Uppercase check
  if (/[A-Z]/.test(password)) {
    uppercaseReq.classList.add("fulfilled");
    uppercaseReq.classList.remove("unfulfilled");
    uppercaseReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    uppercaseReq.classList.add("unfulfilled");
    uppercaseReq.classList.remove("fulfilled");
    uppercaseReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 3. Lowercase check
  if (/[a-z]/.test(password)) {
    lowercaseReq.classList.add("fulfilled");
    lowercaseReq.classList.remove("unfulfilled");
    lowercaseReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    lowercaseReq.classList.add("unfulfilled");
    lowercaseReq.classList.remove("fulfilled");
    lowercaseReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 4. Number check
  if (/[0-9]/.test(password)) {
    numberReq.classList.add("fulfilled");
    numberReq.classList.remove("unfulfilled");
    numberReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    numberReq.classList.add("unfulfilled");
    numberReq.classList.remove("fulfilled");
    numberReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 5. Special character check
  if (/[^A-Za-z0-9]/.test(password)) {
    specialReq.classList.add("fulfilled");
    specialReq.classList.remove("unfulfilled");
    specialReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    specialReq.classList.add("unfulfilled");
    specialReq.classList.remove("fulfilled");
    specialReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // Password strength check
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;

  if (strength <= 2) {
    passwordStrength.textContent = "Very Weak";
    passwordStrength.className = "password-strength very-weak";
    strengthMeterFill.className = "strength-meter-fill very-weak";
  } else if (strength === 3) {
    passwordStrength.textContent = "Weak";
    passwordStrength.className = "password-strength weak";
    strengthMeterFill.className = "strength-meter-fill weak";
  } else if (strength === 4) {
    passwordStrength.textContent = "Medium";
    passwordStrength.className = "password-strength medium";
    strengthMeterFill.className = "strength-meter-fill medium";
  } else if (strength === 5) {
    passwordStrength.textContent = "Strong";
    passwordStrength.className = "password-strength strong";
    strengthMeterFill.className = "strength-meter-fill strong";
  }

  // Common password check
  if (commonPasswords.includes(password)) {
    commonPasswordWarning.style.display = "block";
  } else {
    commonPasswordWarning.style.display = "none";
  }

  // Check if confirm password matches
  if (confirmPasswordInput.value) {
    if (confirmPasswordInput.value === password) {
      confirmPasswordError.textContent = "";
      confirmPasswordInput.style.borderColor = "";
    } else {
      confirmPasswordError.textContent = "Passwords do not match";
      confirmPasswordInput.style.borderColor = "red";
    }
  }
});

togglePassword.addEventListener("click", function () {
  const type =
    passwordInput.getAttribute("type") === "password" ? "text" : "password";
  passwordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});

toggleConfirmPassword.addEventListener("click", function () {
  const type =
    confirmPasswordInput.getAttribute("type") === "password"
      ? "text"
      : "password";
  confirmPasswordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});

// Form submission logic for OTP request
signupForm.addEventListener("submit", function (event) {
  event.preventDefault();
  
  let isValid = true;

  // Full Name validation
  const nameInput = document.getElementById("name");
  const nameError = document.getElementById("nameError");

  if (nameInput.value.trim() === "" || nameInput.value.trim().length < 2) {
    nameError.textContent = "Please enter your full name";
    nameInput.style.borderColor = "red";
    isValid = false;
  } else {
    nameError.textContent = "";
    nameInput.style.borderColor = "";
  }

  // Email validation
  const emailInput = document.getElementById("email");
  const emailError = document.getElementById("emailError");
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(emailInput.value)) {
    emailError.textContent = "Please enter a valid email address";
    emailInput.style.borderColor = "red";
    isValid = false;
  } else {
    emailError.textContent = "";
    emailInput.style.borderColor = "";
  }

  // Password validation
  const passwordError = document.getElementById("passwordError");
  const passwordPattern = new RegExp(
    "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$"
  );

  if (!passwordPattern.test(passwordInput.value)) {
    passwordError.textContent = "Password must meet all the requirements";
    passwordInput.style.borderColor = "red";
    isValid = false;
  } else {
    passwordError.textContent = "";
    passwordInput.style.borderColor = "";
  }

  // Confirm Password validation
  const confirmPasswordError = document.getElementById(
    "confirmPasswordError"
  );

  if (confirmPasswordInput.value !== passwordInput.value) {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
    isValid = false;
  } else {
    confirmPasswordError.textContent = "";
    confirmPasswordInput.style.borderColor = "";
  }

  // reCAPTCHA validation
  const recaptchaResponse = grecaptcha.getResponse();
  const recaptchaError = document.getElementById("recaptchaError");

  if (!recaptchaResponse) {
    recaptchaError.style.display = "block";
    isValid = false;
  } else {
    recaptchaError.style.display = "none";
  }

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

// Handle OTP field input
otpFields.forEach((field, index) => {
  field.addEventListener('keyup', (e) => {
    if (!/^[0-9]$/.test(e.key) && e.key !== 'Backspace' && e.key !== 'Delete') {
      return;
    }
    
    // If a digit is entered, move to next field
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
    
    // If the pasted content contains 6 digits
    if (/^\d{6}$/.test(paste)) {
      // Fill all fields
      for (let i = 0; i < otpFields.length; i++) {
        otpFields[i].value = paste.charAt(i);
      }
      
      // Enable verify button
      checkVerifyButton();
    }
  });
  
  // Handle backspace to move to previous field
  field.addEventListener('keydown', (e) => {
    if (e.key === 'Backspace' && field.value === '' && index > 0) {
      otpFields[index - 1].focus();
    }
  });
});

// Function to check if all OTP fields are filled to enable verify button
function checkVerifyButton() {
  const isComplete = Array.from(otpFields).every(field => field.value !== '');
  verifyOtpBtn.disabled = !isComplete;
}

// Function to request OTP
function requestOTP() {
  const requestOtpBtn = document.getElementById("requestOtpBtn");
  const formSpinner = document.getElementById("formSpinner") || otpSpinner; // Use existing otpSpinner if formSpinner doesn't exist
  
  // Disable button and show spinner
  requestOtpBtn.disabled = true;
  requestOtpBtn.textContent = "Sending...";
  formSpinner.classList.add('active'); // Show the spinner
  otpError.textContent = ''; // Clear any previous errors
  
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
  .then(response => response.json())
  .then(data => {
    // Hide spinner regardless of result
    formSpinner.classList.remove('active');
    
    if (data.success) {
      // Show OTP container
      signupForm.style.display = 'none';
      otpContainer.classList.add('active');
      
      // Start the timer
      startOtpTimer();
      
      // Focus the first OTP field
      otpFields[0].focus();
    } else {
      // Show error and re-enable button
      otpError.textContent = data.message || "Failed to send OTP. Please try again.";
      requestOtpBtn.disabled = false;
      requestOtpBtn.textContent = "Request OTP";
      
      grecaptcha.reset();
    }
  })
  .catch(error => {
    console.error('Error:', error);
    formSpinner.classList.remove('active'); // Hide spinner on error
    otpError.textContent = "An error occurred. Please try again later.";
    requestOtpBtn.disabled = false;
    requestOtpBtn.textContent = "Request OTP";
    
    // Reset reCAPTCHA
    grecaptcha.reset();
  });
}

// Function to start OTP timer (3 minutes)
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

// Function to update timer display
function updateTimerDisplay() {
  const now = new Date().getTime();
  const distance = otpExpiryTime - now;
  
  if (distance <= 0) {
    // Timer expired
    clearInterval(timerInterval);
    otpTimer.textContent = "00:00";
    otpError.textContent = "OTP has expired. Please request a new one.";
    verifyOtpBtn.disabled = true;
    resendOtpBtn.disabled = false;
    return;
  }
  
  // Calculate minutes and seconds
  const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
  // Display the time
  otpTimer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Handle resend OTP button click
resendOtpBtn.addEventListener('click', function() {
  if (this.disabled) return;
  
  // Show spinner and disable button
  this.disabled = true;
  otpSpinner.classList.add('active');
  otpError.textContent = '';
  
  // Clear OTP fields
  otpFields.forEach(field => field.value = '');
  
  // Request new OTP
  fetch('/request_otp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': userData.csrf_token
    },
    body: JSON.stringify({
      email: userData.email,
      name: userData.name,
      resend: true
    })
  })
  .then(response => response.json())
  .then(data => {
    otpSpinner.classList.remove('active');
    
    if (data.success) {
      // Reset timer
      startOtpTimer();
      
      // Focus first field
      otpFields[0].focus();
    } else {
      otpError.textContent = data.message || "Failed to resend OTP. Please try again.";
      resendOtpBtn.disabled = false;
    }
  })
  .catch(error => {
    console.error('Error:', error);
    otpSpinner.classList.remove('active');
    otpError.textContent = "An error occurred. Please try again later.";
    resendOtpBtn.disabled = false;
  });
});

// Handle verify OTP button click
verifyOtpBtn.addEventListener('click', function() {
  // Collect OTP from fields
  const otpValue = Array.from(otpFields).map(field => field.value).join('');
  
  // Disable button and show progress
  this.disabled = true;
  this.textContent = "Verifying...";
  otpError.textContent = '';
  
  // Verify OTP
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
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Stop timer
      if (timerInterval) {
        clearInterval(timerInterval);
      }
      
      // Show success message and redirect
      window.location.href = data.redirectUrl || '/login?success=Account created successfully! Please login.';
    } else {
      // Show error
      otpError.textContent = data.message || "Invalid OTP. Please try again.";
      verifyOtpBtn.disabled = false;
      verifyOtpBtn.textContent = "Verify & Create Account";
      
      // Clear OTP fields
      otpFields.forEach(field => field.value = '');
      otpFields[0].focus();
    }
  })
  .catch(error => {
    console.error('Error:', error);
    otpError.textContent = "An error occurred. Please try again later.";
    verifyOtpBtn.disabled = false;
    verifyOtpBtn.textContent = "Verify & Create Account";
  });
});
