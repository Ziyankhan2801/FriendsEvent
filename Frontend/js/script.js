/* =========================
   CONFIG (AUTO)
========================= */

// 🔥 Auto detect backend (Local vs Production)
const API_URL =
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://friendsevent.onrender.com";

/* =========================
   UI FUNCTIONS
========================= */

function scrollToBooking() {
  document.getElementById("booking")?.scrollIntoView({ behavior: "smooth" });
}

function toggleMenu() {
  document.getElementById("navLinks")?.classList.toggle("show");
}

/* Reveal on scroll */
function revealOnScroll() {
  document.querySelectorAll(".reveal").forEach(el => {
    if (el.getBoundingClientRect().top < window.innerHeight - 100) {
      el.classList.add("active");
    }
  });
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);

/* =========================
   🖼️ GALLERY API + SLIDER
========================= */

let images = [];
let index = 0;
const slideImg = document.getElementById("slide");

async function loadGallery() {
  if (!slideImg) return;

  try {
    const res = await fetch(`${API_URL}/api/gallery/`);
    if (!res.ok) throw new Error("Gallery API failed");

    images = await res.json();

    slideImg.src = images.length
      ? images[0].image
      : "./images/default.jpg";

  } catch (err) {
    console.error("Gallery error:", err);
    slideImg.src = "./images/default.jpg";
  }
}

function showSlide() {
  if (!slideImg || images.length === 0) return;
  slideImg.src = images[index].image;
}

function nextSlide() {
  if (!images.length) return;
  index = (index + 1) % images.length;
  showSlide();
}

function prevSlide() {
  if (!images.length) return;
  index = (index - 1 + images.length) % images.length;
  showSlide();
}

/* Auto slide */
setInterval(() => {
  if (images.length > 1) nextSlide();
}, 3000);

window.addEventListener("load", loadGallery);

/* =========================
   MOBILE NAV CLOSE
========================= */

document.querySelectorAll("#navLinks a").forEach(link => {
  link.addEventListener("click", () => {
    document.getElementById("navLinks")?.classList.remove("show");
  });
});

document.addEventListener("click", (e) => {
  const navLinks = document.getElementById("navLinks");
  const menuBtn = document.querySelector(".menu-btn");

  if (navLinks && menuBtn) {
    if (!navLinks.contains(e.target) && !menuBtn.contains(e.target)) {
      navLinks.classList.remove("show");
    }
  }
});

/* =========================
   🔥 BOOKING FORM → API (FINAL)
========================= */

const bookingForm = document.getElementById("bookingForm");

if (bookingForm) {
  bookingForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const btn = bookingForm.querySelector("button");
    btn.disabled = true;
    btn.innerText = "Submitting...";

    const payload = {
      name: bookingForm.name.value.trim(),
      phone: bookingForm.phone.value.trim(),
      email: bookingForm.email.value.trim(),
      event_type: bookingForm.eventType.value.trim(),
      date: bookingForm.date.value,
      location: bookingForm.location.value.trim(),
      amount: bookingForm.amount.value.trim(),
    };

    try {
      const res = await fetch(`${API_URL}/api/booking/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Booking API failed");

      const result = await res.json();
      console.log("BOOKING RESPONSE:", result);

      if (result.success && result.booking_id) {
        // ✅ HARD REDIRECT (NO FAIL)
        window.location.href =
          "success.html?booking_id=" + result.booking_id;
        return;
      }

      alert("❌ Booking failed. Try again.");

    } catch (err) {
      console.error("Booking error:", err);
      alert("❌ Server issue. Please try later.");
    }

    btn.disabled = false;
    btn.innerText = "Submit Booking";
  });
}
