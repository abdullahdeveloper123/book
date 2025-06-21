  function toggleTheme() {
            const body = document.body;
            const themeIcon = document.getElementById('theme-icon');
            const mobileThemeIcon = document.getElementById('mobile-theme-icon');

            if (body.getAttribute('data-theme') === 'light') {
                body.setAttribute('data-theme', 'dark');
                themeIcon.className = 'fas fa-moon';
                mobileThemeIcon.className = 'fas fa-moon';
                localStorage.setItem('theme', 'dark');
            } else {
                body.setAttribute('data-theme', 'light');
                themeIcon.className = 'fas fa-sun';
                mobileThemeIcon.className = 'fas fa-sun';
                localStorage.setItem('theme', 'light');
            }
        }



    function removeFromWishlist(button, productId) {
      button.innerHTML = '⏳ Removing...';
      button.disabled = true;

      fetch('http://127.0.0.1:8000/remove_wishlist/', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "id": productId })
      })
        .then(response => {
          if (response.status !== 200) {
            console.log("Something went wrong!", response.status);
            button.innerHTML = '✗ Failed';
            button.disabled = false;
            return;
          }
          return response.json();
        })
        .then(data => {
          if (data) {
            console.log(data);
            const card = button.closest('.book-card');
            card.style.transform = 'translateX(-100%)';
            card.style.opacity = '0';
            setTimeout(() => {
              card.remove();
              updateBookCount();
              checkEmptyState();
            }, 300);
          }
        })
        .catch(error => {
          console.error("Network error:", error);
          button.innerHTML = '✗ Failed';
          button.disabled = false;
        });
    }

    function updateBookCount() {
      const cards = document.querySelectorAll('.book-card');
      document.getElementById('total-books').textContent = cards.length;

      // Unique authors
      const authors = new Set();
      cards.forEach(card => {
        authors.add(card.getAttribute('data-author'));
      });
      document.getElementById('author-count').textContent = authors.size;

      // Unique genres
      const genres = new Set();
      cards.forEach(card => {
        genres.add(card.getAttribute('data-genre'));
      });
      document.getElementById('genre-count').textContent = genres.size;
    }

    function checkEmptyState() {
      const grid = document.getElementById('books-grid');
      const cards = document.querySelectorAll('.book-card');

      if (cards.length === 0) {
        grid.innerHTML = `
        <div class="empty-wishlist">
          <div class="empty-icon">📚</div>
          <h2 class="empty-title">Your Wishlist Awaits</h2>
          <p class="empty-subtitle">No sacred texts have been saved yet. Explore our collection and discover wisdom worth treasuring.</p>
          <a href="/" class="browse-btn">Browse Collection</a>
        </div>
      `;
      }
    }

    function clearWishlist() {
      if (confirm('Are you sure you want to clear your entire wishlist?')) {
        document.querySelectorAll('.book-card').forEach(card => {
          card.style.transform = 'translateX(-100%)';
          card.style.opacity = '0';
        });

        setTimeout(() => {
          document.getElementById('books-grid').innerHTML = `
          <div class="empty-wishlist">
            <div class="empty-icon">📚</div>
            <h2 class="empty-title">Your Wishlist Awaits</h2>
            <p class="empty-subtitle">No sacred texts have been saved yet. Explore our collection and discover wisdom worth treasuring.</p>
            <a href="/" class="browse-btn">Browse Collection</a>
          </div>
        `;
          updateBookCount();
        }, 300);
      }
    }
    document.addEventListener("DOMContentLoaded", () => {
      updateBookCount();
    });

    
    // Mobile Navigation Toggle
    function toggleMobileNav() {
      const hamburger = document.querySelector('.nav-hamburger');
      const sidebar = document.getElementById('mobile-sidebar');

      hamburger.classList.toggle('active');
      sidebar.classList.toggle('active');
    }

    // Close mobile nav when clicking outside
    document.addEventListener('click', function (event) {
      const sidebar = document.getElementById('mobile-sidebar');
      const hamburger = document.querySelector('.nav-hamburger');

      if (!sidebar.contains(event.target) && !hamburger.contains(event.target)) {
        sidebar.classList.remove('active');
        hamburger.classList.remove('active');
      }
    });