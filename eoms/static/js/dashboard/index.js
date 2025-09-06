document.addEventListener('DOMContentLoaded', function() {
// Select all sidebar links
var sidebarLinks = document.querySelectorAll('.sidebar-link');

// Iterate over these links and add click events to them
sidebarLinks.forEach(function(link) {
  link.addEventListener('click', function() {
    // Remove the currently active class
    sidebarLinks.forEach(function(otherLink) {
      otherLink.classList.remove('active');
    });

    // Add 'active' class for clicked links
    this.classList.add('active');
  });
});
});

