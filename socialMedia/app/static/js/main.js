    // Theme Toggle Functionality
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

    // Load saved theme
    document.addEventListener('DOMContentLoaded', function () {
      const savedTheme = localStorage.getItem('theme') || 'light';
      const body = document.body;
      const themeIcon = document.getElementById('theme-icon');
      const mobileThemeIcon = document.getElementById('mobile-theme-icon');

      body.setAttribute('data-theme', savedTheme);
      if (savedTheme === 'dark') {
        themeIcon.className = 'fas fa-moon';
        mobileThemeIcon.className = 'fas fa-moon';
      }
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

    // Carousel Functionality
    let currentSlideIndex = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot');
    const track = document.getElementById('carousel-track');

    function showSlide(index) {
      currentSlideIndex = index;
      track.style.transform = `translateX(-${index * 100}%)`;

      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
    }

    function nextSlide() {
      currentSlideIndex = (currentSlideIndex + 1) % slides.length;
      showSlide(currentSlideIndex);
    }

    function previousSlide() {
      currentSlideIndex = (currentSlideIndex - 1 + slides.length) % slides.length;
      showSlide(currentSlideIndex);
    }

    function currentSlide(index) {
      showSlide(index - 1);
    }

    // Auto-play carousel
    setInterval(nextSlide, 5000);

// trending books 
    document.addEventListener("DOMContentLoaded", function () {
      fetch('/trending_books/')
        .then(response => response.json())
        .then(data => {
          const booksGrid = document.querySelector('.books-grid');
          booksGrid.innerHTML = ''; 

          data.forEach(book => {
            const card = document.createElement('div');
            card.classList.add('book-card');

            card.innerHTML = `
           
          <div class="book-info">
            <h3 class="book-title trending-book-quotes">${book.title}</h3>
            <p class="book-title">${book.name}</p>
            <p class="book-author">By <strong>${book.author}</strong></p>
            <p class="book-price">$${book.price}</p>
          </div>
        `;

            booksGrid.appendChild(card);
          });
        })
        .catch(error => {
          console.error('Error fetching top trending books:', error);
        });
    });


    // Search Functionality
    function search() {
      fetch('http://127.0.0.1:8000/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'query': document.getElementById('search_input').value })
      })
        .then(response => response.json())
        .then(data => {
          let quotes_collection = document.getElementById('quotes-collection')
          quotes_collection.innerHTML = ''

          for (let i = 0; i < data.length; i++) {
            let a = document.createElement('a')
            a.classList.add('quote-card')
            a.setAttribute('href', `http://127.0.0.1:8000/details/${data[i].id}`)

            let quoteContent = document.createElement('div')
            quoteContent.classList.add('quote-content')
            quoteContent.textContent = data[i].name

            let authorName = document.createElement('div')
            authorName.classList.add('author_name')
            authorName.textContent = "— " + data[i].author

            a.appendChild(quoteContent)
            a.appendChild(authorName)
            quotes_collection.appendChild(a)
          }
        })
        .catch(error => console.error("Error:", error))
    }

    // Add enter key support for search
    document.getElementById('search_input').addEventListener('keypress', function (event) {
      if (event.key === 'Enter') {
        search();
      }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Add loading animation for search
    function search() {
      const searchButton = document.querySelector('.search-button');
      const originalText = searchButton.innerHTML;

      searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
      searchButton.disabled = true;

      fetch('http://127.0.0.1:8000/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'query': document.getElementById('search_input').value })
      })
        .then(response => response.json())
        .then(data => {
          let quotes_collection = document.getElementById('quotes-collection')
          quotes_collection.innerHTML = ''

          for (let i = 0; i < data.length; i++) {
            let a = document.createElement('a')
            a.classList.add('quote-card')
            a.setAttribute('href', `http://127.0.0.1:8000/details/${data[i].id}`)

            let quoteContent = document.createElement('div')
            quoteContent.classList.add('quote-content')
            quoteContent.textContent = data[i].name

            let authorName = document.createElement('div')
            authorName.classList.add('author_name')
            authorName.textContent = "— " + data[i].author

            a.appendChild(quoteContent)
            a.appendChild(authorName)
            quotes_collection.appendChild(a)
          }
        })
        .catch(error => console.error("Error:", error))
        .finally(() => {
          searchButton.innerHTML = originalText;
          searchButton.disabled = false;
        });
    }

    //  Fetch Recommended Books  
document.addEventListener("DOMContentLoaded", function () {
  fetch('/recommended-books/')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      const booksGrid = document.querySelector('.recomendation-grid');
      if (!booksGrid) return;

      booksGrid.innerHTML = '';

      data.recommendations.forEach(book => {
        const card = document.createElement('div');
        card.classList.add('book-card');

        card.innerHTML = `
          <div class="book-info">
            <h3 class="book-title trending-book-quotes">${book.quote}</h3>
            <p class="book-title">${book.name}</p>
            <p class="book-author">By <strong>${book.author}</strong></p>
            <p class="book-price">$${book.price}</p>
          </div>
        `;

        booksGrid.appendChild(card);
      });
    })
    .catch(error => {
      console.error('Error fetching recommended books:', error);
    });
});


// Wish List
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