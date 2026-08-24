const toggle = document.querySelector('.nav-toggle');
const links = document.querySelector('.nav-links');
if (toggle && links) toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!open));
  links.classList.toggle('is-open', !open);
});

const revealTargets = document.querySelectorAll('.section-heading, .movie-card, .detail-grid, .filter-bar, .review-layout, .about-grid, .profile-grid, .auth-card');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

revealTargets.forEach((element, index) => {
  element.classList.add('cinematic-reveal');
  if (element.classList.contains('movie-card')) {
    element.style.setProperty('--reveal-delay', `${Math.min(index % 4, 3) * 70}ms`);
  }
});

if (reducedMotion || !('IntersectionObserver' in window)) {
  revealTargets.forEach((element) => element.classList.add('is-visible'));
} else {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -30px 0px' });

  revealTargets.forEach((element) => observer.observe(element));
}
