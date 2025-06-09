document
  .getElementById("resetPasswordForm")
  .addEventListener("submit", function (event) {
    let isValid = true;

    // Password validation
    const passwordError = document.getElementById("passwordError");
    const passwordPattern = new RegExp(
      "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$"
    );

    if (!passwordPattern.test(passwordInput.value)) {
      passwordError.textContent =
        "Password must meet all the requirements";
      passwordInput.style.borderColor = "red";
      isValid = false;
    } else {
      passwordError.textContent = "";
      passwordInput.style.borderColor = "";
    }

    // Confirm password validation
    if (confirmPasswordInput.value !== passwordInput.value) {
      confirmPasswordError.textContent = "Passwords do not match";
      confirmPasswordInput.style.borderColor = "red";
      isValid = false;
    } else {
      confirmPasswordError.textContent = "";
      confirmPasswordInput.style.borderColor = "";
    }

    if (!isValid) {
      event.preventDefault();
    } else {
      // Show loading spinner when the form is submitted and validation passes
      document.getElementById("spinnerOverlay").style.display = "flex";
    }
  });

// Real-time password validation
const passwordInput = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");
const passwordStrength = document.getElementById("passwordStrength");
const commonPasswordWarning = document.getElementById("commonPasswordWarning");
const strengthMeterFill = document.getElementById("strengthMeterFill");
const confirmPasswordInput = document.getElementById("confirm_password");
const confirmPasswordError = document.getElementById("confirmPasswordError");

// Getting requirement elements
const lengthReq = document.getElementById("length-requirement");
const uppercaseReq = document.getElementById("uppercase-requirement");
const lowercaseReq = document.getElementById("lowercase-requirement");
const numberReq = document.getElementById("number-requirement");
const specialReq = document.getElementById("special-requirement");

// Common passwords list
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

// Real-time password validation and strength meter
passwordInput.addEventListener("input", function () {
  const password = this.value;

  // Checking each requirement
  // 1. Length check
  if (password.length >= 8) {
    lengthReq.classList.add("fulfilled");
    lengthReq.classList.remove("unfulfilled");
    lengthReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    lengthReq.classList.remove("fulfilled");
    lengthReq.classList.add("unfulfilled");
    lengthReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 2. Uppercase check
  if (/[A-Z]/.test(password)) {
    uppercaseReq.classList.add("fulfilled");
    uppercaseReq.classList.remove("unfulfilled");
    uppercaseReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    uppercaseReq.classList.remove("fulfilled");
    uppercaseReq.classList.add("unfulfilled");
    uppercaseReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 3. Lowercase check
  if (/[a-z]/.test(password)) {
    lowercaseReq.classList.add("fulfilled");
    lowercaseReq.classList.remove("unfulfilled");
    lowercaseReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    lowercaseReq.classList.remove("fulfilled");
    lowercaseReq.classList.add("unfulfilled");
    lowercaseReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 4. Number check
  if (/[0-9]/.test(password)) {
    numberReq.classList.add("fulfilled");
    numberReq.classList.remove("unfulfilled");
    numberReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    numberReq.classList.remove("fulfilled");
    numberReq.classList.add("unfulfilled");
    numberReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // 5. Special character check
  if (/[^A-Za-z0-9]/.test(password)) {
    specialReq.classList.add("fulfilled");
    specialReq.classList.remove("unfulfilled");
    specialReq.querySelector(".requirement-icon").textContent = "✓";
  } else {
    specialReq.classList.remove("fulfilled");
    specialReq.classList.add("unfulfilled");
    specialReq.querySelector(".requirement-icon").textContent = "✕";
  }

  // Password strength check
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;

  // Updating strength meter based on strength level
  strengthMeterFill.style.width = (strength * 20) + "%";

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

  // Checking if confirm password matches
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

// Toggle password visibility
togglePassword.addEventListener("click", function () {
  const type =
    passwordInput.getAttribute("type") === "password" ? "text" : "password";
  passwordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});

// Toggle password visibility for confirm password field
const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");

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
