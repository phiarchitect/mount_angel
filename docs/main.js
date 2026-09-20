let allData = [];
let currentDataView = [];
let currentIndex = -1;

// Editor State
let isEditMode = false;
let currentTool = 'box'; // 'box' or 'point'
let componentsData = {}; // Will hold the annotations keyed by drawing ID
let isDrawing = false;
let startX, startY;
let currentBox = null;

document.addEventListener('DOMContentLoaded', () => {
    // Load main data
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            allData = data;
            populateFilters(data);
            renderGrid(data);
            setupEventListeners();
            
            // Try to load components.json if it exists
            return fetch('components.json');
        })
        .then(response => {
            if (response.ok) return response.json();
            throw new Error('No components.json found');
        })
        .then(compData => {
            componentsData = compData;
        })
        .catch(err => console.log('Notice:', err.message));
});

function populateFilters(data) {
    const types = new Set();
    data.forEach(item => {
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

    // Modal navigation
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

    document.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('show')) return;
        // Don't trigger navigation if user is typing in a prompt/input
        if (e.target.tagName === 'INPUT') return;
        
        if (e.key === 'Escape') closeModal();
        if (e.key === 'ArrowLeft') showPrev();
        if (e.key === 'ArrowRight') showNext();
    });

    prevBtn.addEventListener('click', showPrev);
    nextBtn.addEventListener('click', showNext);

    // Editor events
    document.getElementById('editModeToggle').addEventListener('change', toggleEditMode);
    document.getElementById('toolBox').addEventListener('click', () => setTool('box'));
    document.getElementById('toolPoint').addEventListener('click', () => setTool('point'));
    document.getElementById('exportBtn').addEventListener('click', exportComponentsData);

    // Canvas drawing events
    const overlay = document.getElementById('drawingOverlay');
    overlay.addEventListener('mousedown', startDrawing);
    overlay.addEventListener('mousemove', draw);
    overlay.addEventListener('mouseup', endDrawing);
    overlay.addEventListener('mouseleave', () => { if(isDrawing) endDrawing(); });
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('show');
    // Exit edit mode on close
    if (isEditMode) {
        document.getElementById('editModeToggle').click();
    }
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
    setTimeout(() => modal.classList.add('show'), 10);
}

function updateModalContent(item) {
    const modalImg = document.getElementById('modalImage');
    const caption = document.getElementById('modalCaption');
    
    modalImg.src = `drawings/${item.filename}`;
    caption.innerHTML = `<h3>${item.title_block}</h3><p>${item.contents}</p>`;

    // Wait for image to load to render annotations correctly based on dimensions
    modalImg.onload = () => {
        renderAnnotations(item.id);
    };
}

// --- Editor Functions ---

function toggleEditMode(e) {
    isEditMode = e.target.checked;
    
    const toolbar = document.getElementById('editorToolbar');
    const overlay = document.getElementById('drawingOverlay');
    
    if (isEditMode) {
        toolbar.style.display = 'flex';
        overlay.style.display = 'block';
    } else {
        toolbar.style.display = 'none';
        overlay.style.display = 'none';
    }
}

function setTool(toolName) {
    currentTool = toolName;
    document.getElementById('toolBox').classList.toggle('active', toolName === 'box');
    document.getElementById('toolPoint').classList.toggle('active', toolName === 'point');
}

function startDrawing(e) {
    if (!isEditMode) return;
    
    const rect = e.target.getBoundingClientRect();
    // Calculate percentages
    startX = ((e.clientX - rect.left) / rect.width) * 100;
    startY = ((e.clientY - rect.top) / rect.height) * 100;

    if (currentTool === 'box') {
        isDrawing = true;
        currentBox = document.createElement('div');
        currentBox.className = 'bounding-box';
        currentBox.style.left = startX + '%';
        currentBox.style.top = startY + '%';
        document.getElementById('annotationsLayer').appendChild(currentBox);
    } else if (currentTool === 'point') {
        // Place point immediately
        saveReferencePoint(startX, startY);
    }
}

function draw(e) {
    if (!isDrawing || currentTool !== 'box' || !currentBox) return;

    const rect = e.target.getBoundingClientRect();
    const currentX = ((e.clientX - rect.left) / rect.width) * 100;
    const currentY = ((e.clientY - rect.top) / rect.height) * 100;

    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    const left = Math.min(currentX, startX);
    const top = Math.min(currentY, startY);

    currentBox.style.width = width + '%';
    currentBox.style.height = height + '%';
    currentBox.style.left = left + '%';
    currentBox.style.top = top + '%';
}

function endDrawing(e) {
    if (!isDrawing) return;
    isDrawing = false;

    if (currentTool === 'box' && currentBox) {
        const width = parseFloat(currentBox.style.width);
        const height = parseFloat(currentBox.style.height);
        
        // Ignore tiny accidental clicks
        if (width < 1 || height < 1) {
            currentBox.remove();
            currentBox = null;
            return;
        }

        const name = prompt("Enter a name for this component:", "New Component");
        if (name) {
            saveBoundingBox(
                name, 
                parseFloat(currentBox.style.left), 
                parseFloat(currentBox.style.top), 
                width, 
                height
            );
        } else {
            currentBox.remove();
        }
        currentBox = null;
        
        // Re-render to show proper label
        const currentItem = currentDataView[currentIndex];
        renderAnnotations(currentItem.id);
    }
}

function initializeComponentData(id) {
    if (!componentsData[id]) {
        componentsData[id] = {
            reference_point: null,
            components: []
        };
    }
}

function saveReferencePoint(x, y) {
    const currentItem = currentDataView[currentIndex];
    initializeComponentData(currentItem.id);
    
    componentsData[currentItem.id].reference_point = { x, y };
    renderAnnotations(currentItem.id);
}

function saveBoundingBox(name, x, y, w, h) {
    const currentItem = currentDataView[currentIndex];
    initializeComponentData(currentItem.id);
    
    const newComponent = {
        id: 'comp_' + Date.now(),
        name: name,
        box: { x, y, w, h }
    };
    
    componentsData[currentItem.id].components.push(newComponent);
}

function renderAnnotations(id) {
    const layer = document.getElementById('annotationsLayer');
    layer.innerHTML = ''; // Clear existing
    
    const data = componentsData[id];
    if (!data) return;

    // Render Box Components
    if (data.components) {
        data.components.forEach(comp => {
            const box = document.createElement('div');
            box.className = 'bounding-box';
            box.style.left = comp.box.x + '%';
            box.style.top = comp.box.y + '%';
            box.style.width = comp.box.w + '%';
            box.style.height = comp.box.h + '%';
            
            const label = document.createElement('div');
            label.className = 'box-label';
            label.textContent = comp.name;
            
            // Allow deletion of box by clicking the label while in edit mode
            label.onclick = (e) => {
                if (isEditMode && confirm(`Delete component "${comp.name}"?`)) {
                    componentsData[id].components = componentsData[id].components.filter(c => c.id !== comp.id);
                    renderAnnotations(id);
                }
            };

            box.appendChild(label);
            layer.appendChild(box);
        });
    }

    // Render Reference Point
    if (data.reference_point) {
        const pt = document.createElement('div');
        pt.className = 'ref-point';
        pt.style.left = data.reference_point.x + '%';
        pt.style.top = data.reference_point.y + '%';
        pt.title = "Reference Point (Origin)";
        
        // Allow deletion of point by clicking it in edit mode
        pt.onclick = (e) => {
            if (isEditMode && confirm("Delete reference point?")) {
                componentsData[id].reference_point = null;
                renderAnnotations(id);
            }
        };

        layer.appendChild(pt);
    }
}

function exportComponentsData() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(componentsData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "components.json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}
