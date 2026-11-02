/* Product page: when the customer chooses a version (for example
   "Digital file" or "Printed A4"), show its price straight away.
   This is only a preview. The real price is always worked out
   again on the server in the bag and at checkout. */

document.addEventListener("DOMContentLoaded", function () {
  const priceText = document.getElementById("product-price");
  const choices = document.querySelectorAll(".option-radio");

  choices.forEach(function (choice) {
    choice.addEventListener("change", function () {
      const price = parseFloat(choice.dataset.price);
      if (priceText && !isNaN(price)) {
        priceText.textContent = "€" + price.toFixed(2);
      }
    });
  });
});
