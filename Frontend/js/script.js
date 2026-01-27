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

// ✅ Slider with admin images
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

/* ✅ Start first image */
window.onload = () => {
  images = window.GALLERY_IMAGES || [];
  showSlide();
};


// ✅ Close menu when any link is clicked (mobile)
document.querySelectorAll("#navLinks a").forEach(link => {
  link.addEventListener("click", () => {
    document.getElementById("navLinks").classList.remove("show");
  });
});
// ✅ Close menu when click outside navbar (optional)
document.addEventListener("click", (e) => {
  const navLinks = document.getElementById("navLinks");
  const menuBtn = document.querySelector(".menu-btn");

  if (!navLinks.contains(e.target) && !menuBtn.contains(e.target)) {
    navLinks.classList.remove("show");
  }
});
