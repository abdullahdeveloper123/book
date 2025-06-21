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

    let booksData = [];
    let filteredBooks = [];
    let currentView = 'grid';

    const bookStoreURL = "https://mystore.com/book";

    document.addEventListener('DOMContentLoaded', async function () {
      await fetchBooks();
      filteredBooks = [...booksData];
      updateStats();
      createGenreFilter();
      renderBooks();
      setupEventListeners();
    });

    async function fetchBooks() {
      try {
        const response = await fetch('http://127.0.0.1:8000/get_orders/');
        const data = await response.json();
        booksData = data;
        console.log('Fetched books:', booksData);
      } catch (error) {
        console.error('Failed to fetch books:', error);
      }
    }

    function updateStats() {
      document.getElementById('total-books').textContent = booksData.length;
      document.getElementById('total-authors').textContent = new Set(booksData.map(b => b.author)).size;
      document.getElementById('total-genres').textContent = new Set(booksData.map(b => b.genre)).size;
    }

    function setupEventListeners() {
      document.addEventListener('click', handleBookActions);
      document.querySelectorAll('.toggle-btn').forEach(btn =>
        btn.addEventListener('click', handleViewToggle)
      );
      const searchInput = document.getElementById('searchInput');
      if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
      }
    }

    function handleViewToggle(event) {
      const viewType = event.target.dataset.view;
      currentView = viewType;
      document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('books-grid').style.display = viewType === 'grid' ? 'grid' : 'none';
      document.getElementById('books-list').style.display = viewType === 'list' ? 'flex' : 'none';
      renderBooks();
    }

    function handleBookActions(event) {
      if (event.target.classList.contains('copy-btn')) {
        const bookId = event.target.closest('[data-book-id]').dataset.bookId;
        copyBookURL(bookId);
      }
    }

    function copyBookURL(bookId) {
      const book = booksData.find(b => b.id == bookId);
      if (!book) return;
      const urlToCopy = `${bookStoreURL}/${book.product_id}`;
      navigator.clipboard.writeText(urlToCopy).then(() => {
        alert(`Copied: ${urlToCopy}`);
      });
    }

    function renderBooks() {
      const gridContainer = document.getElementById('books-grid');
      const listContainer = document.getElementById('books-list');
      const noResults = document.getElementById('no-results');
      gridContainer.innerHTML = "";
      listContainer.innerHTML = "";

      if (filteredBooks.length === 0) {
        noResults.style.display = 'block';
        return;
      } else {
        noResults.style.display = 'none';
      }

      if (currentView === 'grid') {
        gridContainer.innerHTML = filteredBooks.map(book => createBookCard(book)).join('');
      }
    }

    function createBookCard(book) {
      return `
      <div class="book-card" data-book-id="${book.id}">
        <div class="book-header">
          <span class="book-genre">${book.genre}</span>
        </div>
        <div class="book-content">
          <h3 class="book-title">${book.title}</h3>
          <p class="book-author">By ${book.author}</p>
          <div class="book-meta">
            <span>📅 ${book.year}</span>
            <span>📄 ${book.pages} pages</span>
          </div>
          <p class="book-description">${book.description}</p>
          <div class="book-actions">
            <a href="../details/${book.product_id}" class="action-btn view-btn">🛒 View in Store</a>
            <button class="action-btn copy-btn">📋 Copy</button>
          </div>
        </div>
      </div>`;
    }

    function createBookListItem(book) {
      return `
      <div class="book-list-item" data-book-id="${book.id}" style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid #ddd;border-radius:8px;margin-bottom:8px;background:#fafafa;box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        <div style="flex:1;">
          <h3 style="margin:0 0 4px;font-size:18px;">${book.title}</h3>
          <p style="margin:0;color:#666;font-size:14px;">By <strong>${book.author}</strong> | <em>${book.genre}</em> | 📅 ${book.year} | 📄 ${book.pages} pages</p>
        </div>
        <div style="display:flex;gap:8px;">
          <a href="../details/${book.product_id}" class="action-btn view-btn" style="padding:6px 10px;border:none;background:#4caf50;color:#fff;border-radius:4px;cursor:pointer;">🛒 View</a>
          <button class="action-btn copy-btn" style="padding:6px 10px;border:none;background:#2196f3;color:#fff;border-radius:4px;cursor:pointer;">📋 Copy</button>
        </div>
      </div>`;
    }

    function createGenreFilter() {
      const parent = document.getElementById('view-controls');
      if (!parent) return;

      const select = document.createElement('select');
      select.setAttribute('class', 'genre-filter');
      select.setAttribute('id', 'genreFilter');
      select.innerHTML = `<option value="">All Genres</option>`;

      const genres = [...new Set(booksData.map(book => book.genre))];
      genres.forEach(genre => {
        const option = document.createElement('option');
        option.value = genre;
        option.textContent = genre;
        select.appendChild(option);
      });

      parent.appendChild(select);
      select.addEventListener('change', () => {
        handleSearch();
      });
    }

    function handleSearch() {
      const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
      const selectedGenre = document.getElementById('genreFilter')?.value;

      filteredBooks = booksData.filter(book => {
        const matchesSearch = book.title.toLowerCase().includes(searchTerm) ||
          book.author.toLowerCase().includes(searchTerm);
        const matchesGenre = !selectedGenre || book.genre === selectedGenre;
        return matchesSearch && matchesGenre;
      });

      renderBooks();
    }

    
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