/* =========================
   CONFIG
========================= */

// 🔴 YAHAN APNA RENDER BACKEND URL DAAL
const API_URL = "https://event-booking-system.onrender.com";

/* =========================
   UI FUNCTIONS (as it is)
========================= */

function scrollToBooking() {
  document.getElementById("booking").scrollIntoView({ behavior: "smooth" });
}

/* ✅ Mobile Navbar toggle */
function toggleMenu() {
  document.getElementById("navLinks").classList.toggle("show");
}

/* ✅ Reveal animation on scroll */
function revealOnScroll() {
  const reveals = document.querySelectorAll(".reveal");
  reveals.forEach(el => {
    const windowHeight = window.innerHeight;
    const elementTop = el.getBoundingClientRect().top;

    if (elementTop < windowHeight - 100) {
      el.classList.add("active");
    }
  });
}

window.addEventListener("scroll", revealOnScroll);
window.addEventListener("load", revealOnScroll);

/* =========================
   SLIDER
========================= */

let images = window.GALLERY_IMAGES || [];
let index = 0;

function showSlide() {
  if (images.length === 0) return;
  document.getElementById("slide").src = images[index];
}

function nextSlide() {
  if (images.length === 0) return;
  index = (index + 1) % images.length;
  showSlide();
}

function prevSlide() {
  if (images.length === 0) return;
  index = (index - 1 + images.length) % images.length;
  showSlide();
}

/* ✅ Auto slide */
setInterval(() => {
  if (images.length > 1) nextSlide();
}, 3000);

window.onload = () => {
  images = window.GALLERY_IMAGES || [];
  showSlide();
};

/* =========================
   MOBILE NAV CLOSE
========================= */

document.querySelectorAll("#navLinks a").forEach(link => {
  link.addEventListener("click", () => {
    document.getElementById("navLinks").classList.remove("show");
  });
});

document.addEventListener("click", (e) => {
  const navLinks = document.getElementById("navLinks");
  const menuBtn = document.querySelector(".menu-btn");

  if (!navLinks.contains(e.target) && !menuBtn.contains(e.target)) {
    navLinks.classList.remove("show");
  }
});

/* =========================
   🔥 BOOKING FORM → API
========================= */

const bookingForm = document.getElementById("bookingForm");

if (bookingForm) {
  bookingForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const btn = bookingForm.querySelector("button");
    btn.disabled = true;
    btn.innerText = "Submitting...";

    const data = {
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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (result.success) {
        // ✅ SUCCESS → redirect
        window.location.href = "success.html";
      } else {
        alert("❌ Something went wrong. Try again.");
      }

    } catch (err) {
      console.error(err);
      alert("❌ Server error. Please try later.");
    }

    btn.disabled = false;
    btn.innerText = "Submit Booking";
  });
}

if (result.success) {
  alert("✅ Booking submitted successfully!");
  bookingForm.reset();
}
