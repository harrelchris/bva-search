document.addEventListener('DOMContentLoaded', (event) => {
  const htmlElement = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');

  let currentTheme = localStorage.getItem('bsTheme') || 'dark';
  htmlElement.setAttribute('data-bs-theme', currentTheme);

  themeToggle.addEventListener('click', function () {
    if (currentTheme === 'light') {
      currentTheme = 'dark';
      themeIcon.classList.remove("bi-moon");
      themeIcon.classList.add("bi-sun");
      htmlElement.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('bsTheme', 'dark');
    } else {
      currentTheme = 'light';
      themeIcon.classList.remove("bi-sun");
      themeIcon.classList.add("bi-moon");
      htmlElement.setAttribute('data-bs-theme', 'light');
      localStorage.setItem('bsTheme', 'light');
    }
  });
});
