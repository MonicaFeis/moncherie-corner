/* Checkout page: show a "please wait" state on the Pay button (US-10).
 *
 * When the form is sent, the button is disabled so it cannot be clicked twice,
 * and a spinner with "Taking you to payment" is shown while we go to Stripe.
 * If the customer comes back with the browser's Back button, the button is
 * reset so they can try again.
 */
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("checkout-form");
  const button = document.getElementById("pay-button");
  const status = document.getElementById("pay-status");
  if (!form || !button) {
    return;
  }
  const ready = button.querySelector(".pay-ready");
  const waiting = button.querySelector(".pay-waiting");

  function showWaiting(isWaiting) {
    button.disabled = isWaiting;
    button.setAttribute("aria-busy", isWaiting ? "true" : "false");
    ready.classList.toggle("d-none", isWaiting);
    waiting.classList.toggle("d-none", !isWaiting);
    if (status) {
      status.textContent = isWaiting ? "Taking you to payment, please wait." : "";
    }
  }

  form.addEventListener("submit", function () {
    showWaiting(true);
  });

  // Coming back with the Back button can show the old, disabled page.
  window.addEventListener("pageshow", function () {
    showWaiting(false);
  });
});
