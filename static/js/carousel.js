/* Featured products carousel on the home page.
   The products sit in a row that scrolls sideways (with a finger, trackpad
   or the arrow keys). The two buttons move it one card at a time.
   Without JavaScript the row still scrolls, the buttons are just hidden. */

document.addEventListener("DOMContentLoaded", function () {
  const track = document.getElementById("featured-track");
  const previous = document.querySelector("[data-carousel-prev]");
  const next = document.querySelector("[data-carousel-next]");
  if (!track || !previous || !next) {
    return;
  }

  // How far one click moves: one card plus the gap between cards
  function stepSize() {
    const slide = track.querySelector(".carousel-slide");
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    return slide ? slide.offsetWidth + gap : track.clientWidth;
  }

  // Turn the buttons off at the start and the end, hide them if everything fits
  function updateButtons() {
    const maxScroll = track.scrollWidth - track.clientWidth;
    const everythingFits = maxScroll <= 8;
    previous.hidden = everythingFits;
    next.hidden = everythingFits;
    previous.disabled = track.scrollLeft <= 8;
    next.disabled = track.scrollLeft >= maxScroll - 8;
  }

  previous.addEventListener("click", function () {
    track.scrollBy({ left: -stepSize() });
  });
  next.addEventListener("click", function () {
    track.scrollBy({ left: stepSize() });
  });
  track.addEventListener("scroll", updateButtons, { passive: true });
  window.addEventListener("resize", updateButtons);
  updateButtons();
});
