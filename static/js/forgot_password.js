document
  .getElementById("forgotPasswordForm")
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
    } else {
      // Showing loading spinner when the form is submitted and validation passes
      document.getElementById("spinnerOverlay").style.display = "flex";
    }
  });
