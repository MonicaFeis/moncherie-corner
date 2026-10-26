/* Cart page: when the quantity changes, show the new totals straight away.
   This is only a preview. The real price is always worked out again
   on the server when the customer clicks "Update" or pays. */

function formatEuro(amount) {
  return "€" + amount.toFixed(2);
}

function updateCartPreview() {
  const rows = document.querySelectorAll(".cart-row");
  let total = 0;
  let changed = false;

  rows.forEach(function (row) {
    const price = parseFloat(row.dataset.price);
    const input = row.querySelector(".qty-input");
    let quantity = 1;

    if (input) {
      const max = parseInt(input.max, 10);
      quantity = parseInt(input.value, 10);
      if (isNaN(quantity) || quantity < 1) {
        quantity = 1;
      }
      if (quantity > max) {
        quantity = max;
        input.value = max;
      }
      if (quantity !== parseInt(input.defaultValue, 10)) {
        changed = true;
      }
    }

    const lineTotal = price * quantity;
    row.querySelector(".line-total").textContent = formatEuro(lineTotal);
    total += lineTotal;
  });

  document.getElementById("cart-total").textContent = formatEuro(total);
  document.getElementById("cart-note").textContent = changed
    ? "Click Update to save the new quantity. 撳 Update 儲存。"
    : "";
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".qty-input").forEach(function (input) {
    input.addEventListener("input", updateCartPreview);
  });
});
