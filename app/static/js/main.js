/* ========================================
   LibrarySphere - Main JavaScript
======================================== */

// ---- Auto hide flash messages ----
setTimeout(() => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    alert.style.transition = 'all 0.5s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-10px)';
    setTimeout(() => alert.remove(), 500);
  });
}, 4000);

// ---- Sidebar Toggle (Mobile) ----
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (sidebarToggle) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
  });
}

if (overlay) {
  overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
  });
}

// ---- Active Nav Link ----
const currentPath = window.location.pathname;
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
  if (link.getAttribute('href') === currentPath) {
    link.classList.add('active');
  }
});

// ---- Confirm Delete ----
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this?');
}

// ---- Loading Button ----
function setLoading(btn, loading) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.original = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Please wait...';
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.original;
  }
}

// ---- Format Currency ----
function formatCurrency(amount) {
  return '₹' + parseFloat(amount).toFixed(2);
}

// ---- Tooltip Init ----
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap tooltips
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(el => new bootstrap.Tooltip(el));

  // Add fade-in animation to cards
  const cards = document.querySelectorAll('.card, .kpi-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.05}s`;
    card.classList.add('animated');
  });
});

// ---- Search Filter ----
function liveSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('keyup', () => {
    const filter = input.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(filter) ? '' : 'none';
    });
  });
}

// ---- Print Page ----
function printPage() {
  window.print();
}