let allData = [];
let currentDataView = [];
let currentIndex = -1;

document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            allData = data;
            populateFilters(data);
            renderGrid(data);
            setupEventListeners();
        })
        .catch(err => console.error('Error loading data:', err));
});

function populateFilters(data) {
    const types = new Set();
    data.forEach(item => {
        // Some types are combined like "Plan / Details", let's just use the raw string for simplicity,
        // or we could split them. We'll use the raw type string.
        if (item.type && item.type !== "Unknown") {
            types.add(item.type);
        }
    });

    const filterSelect = document.getElementById('typeFilter');
    Array.from(types).sort().forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        filterSelect.appendChild(option);
    });
}

function renderGrid(data) {
    currentDataView = data;
    const grid = document.getElementById('galleryGrid');
    grid.innerHTML = '';
    
    if (data.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No drawings found.</div>';
        return;
    }

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        // we assume the images are one level up in references/drawings/
        const imgSrc = `drawings/${item.filename}`;
        
        card.innerHTML = `
            <div class="card-img-wrap">
                <img src="${imgSrc}" alt="${item.title_block}" loading="lazy">
            </div>
            <div class="card-content">
                <div class="card-type">${item.type}</div>
                <div class="card-title">${item.title_block}</div>
                <div class="card-desc">${item.contents}</div>
                <div class="card-footer">
                    <span>ID: ${item.id}</span>
                    <span>${item.filename}</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => openModal(item));
        grid.appendChild(card);
    });
}

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const sortSelect = document.getElementById('sortSelect');
    
    const applyFilters = () => {
        const query = searchInput.value.toLowerCase();
        const type = typeFilter.value;
        const sort = sortSelect.value;
        
        let filtered = allData.filter(item => {
            const matchesSearch = item.title_block.toLowerCase().includes(query) || 
                                  item.contents.toLowerCase().includes(query) ||
                                  item.filename.toLowerCase().includes(query);
            const matchesType = type === 'all' || item.type === type;
            return matchesSearch && matchesType;
        });
        
        filtered.sort((a, b) => {
            if (sort === 'id_asc') return a.id - b.id;
            if (sort === 'id_desc') return b.id - a.id;
            if (sort === 'type_asc') return a.type.localeCompare(b.type);
            return 0;
        });
        
        renderGrid(filtered);
    };

    searchInput.addEventListener('input', applyFilters);
    typeFilter.addEventListener('change', applyFilters);
    sortSelect.addEventListener('change', applyFilters);

    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.close-modal');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    closeBtn.onclick = () => closeModal();
    
    window.onclick = (e) => {
        if (e.target === modal) {
            closeModal();
        }
    };

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('show')) return;
        if (e.key === 'Escape') closeModal();
        if (e.key === 'ArrowLeft') showPrev();
        if (e.key === 'ArrowRight') showNext();
    });

    prevBtn.addEventListener('click', showPrev);
    nextBtn.addEventListener('click', showNext);
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('show');
    setTimeout(() => modal.style.display = 'none', 300);
}

function showPrev() {
    if (currentDataView.length === 0) return;
    currentIndex = (currentIndex > 0) ? currentIndex - 1 : currentDataView.length - 1;
    updateModalContent(currentDataView[currentIndex]);
}

function showNext() {
    if (currentDataView.length === 0) return;
    currentIndex = (currentIndex < currentDataView.length - 1) ? currentIndex + 1 : 0;
    updateModalContent(currentDataView[currentIndex]);
}

function openModal(item) {
    const modal = document.getElementById('imageModal');
    currentIndex = currentDataView.findIndex(d => d.id === item.id);
    updateModalContent(item);
    
    modal.style.display = 'block';
    // tiny delay to allow display:block to apply before opacity transition
    setTimeout(() => modal.classList.add('show'), 10);
}

function updateModalContent(item) {
    const modalImg = document.getElementById('modalImage');
    const caption = document.getElementById('modalCaption');
    
    modalImg.src = `drawings/${item.filename}`;
    caption.innerHTML = `<h3>${item.title_block}</h3><p>${item.contents}</p>`;
}
