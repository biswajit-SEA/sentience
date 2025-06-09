// Real-time password validation
const newPasswordInput = document.getElementById("new_password");
const toggleNewPassword = document.getElementById("toggleNewPassword");
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

// Real-time validation for confirm password match
confirmPasswordInput.addEventListener("input", function () {
  if (this.value === newPasswordInput.value) {
    confirmPasswordError.textContent = "";
    confirmPasswordInput.style.borderColor = "";
  } else {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
  }
});

newPasswordInput.addEventListener("input", function () {
  const password = this.value;

  // Checking each requirement
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

// Toggle current password visibility
const currentPasswordInput = document.getElementById("current_password");
const toggleCurrentPassword = document.getElementById("toggleCurrentPassword");

toggleCurrentPassword.addEventListener("click", function () {
  const type =
    currentPasswordInput.getAttribute("type") === "password"
      ? "text"
      : "password";
  currentPasswordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});

// Toggle new password visibility
toggleNewPassword.addEventListener("click", function () {
  const type =
    newPasswordInput.getAttribute("type") === "password" ? "text" : "password";
  newPasswordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});

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

// Handling form validation, password toggles, etc.
document
  .getElementById("changePasswordForm")
  .addEventListener("submit", function (event) {
    let isValid = true;

    // Current password validation
    const currentPasswordInput = document.getElementById("current_password");
    const currentPasswordError = document.getElementById(
      "currentPasswordError"
    );

    if (currentPasswordInput.value.trim() === "") {
      currentPasswordError.textContent = "Please enter your current password";
      currentPasswordInput.style.borderColor = "red";
      isValid = false;
    } else {
      currentPasswordError.textContent = "";
      currentPasswordInput.style.borderColor = "";
    }

    // New password validation
    const newPasswordError = document.getElementById("newPasswordError");
    const passwordPattern = new RegExp(
      "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$"
    );

    // Checking if new password is the same as current password
    if (newPasswordInput.value === currentPasswordInput.value) {
      newPasswordError.textContent =
        "New password cannot be the same as your current password";
      newPasswordInput.style.borderColor = "red";
      isValid = false;
    } else if (!passwordPattern.test(newPasswordInput.value)) {
      newPasswordError.textContent = "Password must meet all the requirements";
      newPasswordInput.style.borderColor = "red";
      isValid = false;
    } else {
      newPasswordError.textContent = "";
      newPasswordInput.style.borderColor = "";
    }

    // Confirm Password validation
    if (confirmPasswordInput.value !== newPasswordInput.value) {
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
      // Showing loading spinner when the form is submitted
      document.getElementById("spinnerOverlay").style.display = "flex";
    }
  });
