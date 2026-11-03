/* Product page: when the customer chooses a version (for example
   "Digital file" or "Printed A4") or the number of people, show the new
   price straight away. This is only a preview. The real price is always
   worked out again on the server in the bag and at checkout. */

document.addEventListener("DOMContentLoaded", function () {
  const priceText = document.getElementById("product-price");
  const choices = document.querySelectorAll(".option-radio");
  const people = document.querySelector(".people-select");
  if (!priceText) {
    return;
  }

  function showPrice() {
    let price = parseFloat(priceText.dataset.base);
    const chosen = document.querySelector(".option-radio:checked");
    if (chosen) {
      price = parseFloat(chosen.dataset.price);
    }
    if (people) {
      price += (parseInt(people.value, 10) - 1) * parseFloat(people.dataset.extra || "0");
    }
    if (!isNaN(price)) {
      priceText.textContent = "€" + price.toFixed(2);
    }
  }

  choices.forEach(function (choice) {
    choice.addEventListener("change", showPrice);
  });
  if (people) {
    people.addEventListener("change", showPrice);
  }
});

/* Examples: click a small picture to show it in the big one.
   Without JavaScript, the link simply opens the picture. */
document.addEventListener("DOMContentLoaded", function () {
  const mainImage = document.getElementById("main-image");
  const thumbs = document.querySelectorAll(".example-thumb");
  if (!mainImage) {
    return;
  }
  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function (event) {
      event.preventDefault();
      mainImage.src = thumb.getAttribute("href");
      mainImage.alt = thumb.dataset.alt;
      thumbs.forEach(function (other) {
        other.classList.remove("is-active");
      });
      thumb.classList.add("is-active");
    });
  });
});
