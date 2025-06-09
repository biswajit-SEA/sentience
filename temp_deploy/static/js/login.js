document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    let isValid = true;

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
    const passwordInput = document.getElementById("password");
    const passwordError = document.getElementById("passwordError");

    if (passwordInput.value.trim() === "") {
      passwordError.textContent = "Password cannot be empty";
      passwordInput.style.borderColor = "red";
      isValid = false;
    } else {
      passwordError.textContent = "";
      passwordInput.style.borderColor = "";
    }

    // reCAPTCHA validation
    const recaptchaResponse = grecaptcha.getResponse();
    const recaptchaError = document.getElementById("recaptchaError");

    if (recaptchaResponse.length === 0) {
      recaptchaError.style.display = "block";
      isValid = false;
    } else {
      recaptchaError.style.display = "none";
    }

    if (!isValid) {
      event.preventDefault();
    }
  });

// Toggle password visibility
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

togglePassword.addEventListener("click", function () {
  const type =
    passwordInput.getAttribute("type") === "password" ? "text" : "password";
  passwordInput.setAttribute("type", type);
  this.innerHTML =
    type === "password"
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
});
