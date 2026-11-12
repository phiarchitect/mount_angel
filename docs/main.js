let allData = [];
let currentDataView = [];
let currentIndex = -1;

// Vector Overlay State
let vectorManifest = { layers: [], sheets: {} };
let svgCache = {};
let calibratedOnly = false;
let vectorMasterEnabled = true;
let darkBlueprintEnabled = true;
let scanOpacity = 78;
let activeLayers = new Set();

// Editor State
let isEditMode = false;
let currentTool = 'box'; // 'box' or 'point'
let componentsData = {}; // Will hold the annotations keyed by drawing ID
let isDrawing = false;
let startX, startY;
let currentBox = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [dataRes, manifestRes] = await Promise.all([
            fetch('data.json'),
            fetch('overlays/manifest.json').catch(() => null),
        ]);
        allData = await dataRes.json();

        if (manifestRes && manifestRes.ok) {
            vectorManifest = await manifestRes.json();
            (vectorManifest.layers || []).forEach(l => activeLayers.add(l.id));
            buildLayerPills();
        }

        populateFilters(allData);
        renderGrid(allData);
        setupEventListeners();

        const compRes = await fetch('components.json').catch(() => null);
        if (compRes && compRes.ok) {
            componentsData = await compRes.json();
        }
    } catch (err) {
        console.log('Initialization notice:', err.message);
    }
});

function buildLayerPills() {
    const wrap = document.getElementById('vecLayerPills');
    if (!wrap) return;
    wrap.innerHTML = '';
    (vectorManifest.layers || []).forEach(layer => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'vec-pill active';
        btn.dataset.layer = layer.id;
        btn.innerHTML = `<span class="dot" style="background:${layer.color}"></span><span>${layer.label}</span>`;
        btn.addEventListener('click', () => {
            if (activeLayers.has(layer.id)) {
                activeLayers.delete(layer.id);
                btn.classList.remove('active');
            } else {
                activeLayers.add(layer.id);
                btn.classList.add('active');
            }
            syncVectorLayerVisibility();
        });
        wrap.appendChild(btn);
    });
}

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

function isSheetCalibrated(id) {
    return Boolean(vectorManifest.sheets && vectorManifest.sheets[String(id)]);
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
        const calibrated = isSheetCalibrated(item.id);
        const card = document.createElement('div');
        card.className = calibrated ? 'card is-calibrated' : 'card';
        const imgSrc = calibrated
            ? `overlays/proofs/proof_sheet_${String(item.id).padStart(2, '0')}.png`
            : `drawings/${item.filename}`;

        card.innerHTML = `
            <div class="card-img-wrap">
                ${calibrated ? '<span class="calibrated-badge">&#10022; Vector Calibrated</span>' : ''}
                <img src="${imgSrc}" alt="${item.title_block}" loading="lazy" onerror="this.onerror=null;this.src='drawings/${item.filename}';">
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
    const calibratedBtn = document.getElementById('calibratedOnlyBtn');

    const applyFilters = () => {
        const query = searchInput.value.toLowerCase();
        const type = typeFilter.value;
        const sort = sortSelect.value;

        let filtered = allData.filter(item => {
            const matchesSearch = item.title_block.toLowerCase().includes(query) ||
                                  item.contents.toLowerCase().includes(query) ||
                                  item.filename.toLowerCase().includes(query);
            const matchesType = type === 'all' || item.type === type;
            const matchesCalibrated = !calibratedOnly || isSheetCalibrated(item.id);
            return matchesSearch && matchesType && matchesCalibrated;
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

    if (calibratedBtn) {
        calibratedBtn.addEventListener('click', () => {
            calibratedOnly = !calibratedOnly;
            calibratedBtn.classList.toggle('active', calibratedOnly);
            applyFilters();
        });
    }

    // Vector control bar events
    const masterCheck = document.getElementById('vecMasterCheck');
    const darkCheck = document.getElementById('vecDarkBlueprintCheck');
    const opacitySlider = document.getElementById('scanOpacitySlider');
    const opacityVal = document.getElementById('scanOpacityVal');

    if (masterCheck) {
        masterCheck.addEventListener('change', (e) => {
            vectorMasterEnabled = e.target.checked;
            syncVectorLayerVisibility();
        });
    }
    if (darkCheck) {
        darkCheck.addEventListener('change', (e) => {
            darkBlueprintEnabled = e.target.checked;
            applyScanVisualState(currentDataView[currentIndex]?.id);
        });
    }
    if (opacitySlider) {
        opacitySlider.addEventListener('input', (e) => {
            scanOpacity = parseInt(e.target.value, 10);
            if (opacityVal) opacityVal.textContent = `${scanOpacity}%`;
            applyScanVisualState(currentDataView[currentIndex]?.id);
        });
    }

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
    overlay.addEventListener('mouseleave', () => { if (isDrawing) endDrawing(); });
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('show');
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

async function renderVectorOverlay(id) {
    const bar = document.getElementById('vectorOverlayBar');
    const svgLayer = document.getElementById('vectorSvgLayer');
    if (!bar || !svgLayer) return;

    const sheetMeta = vectorManifest.sheets ? vectorManifest.sheets[String(id)] : null;
    if (!sheetMeta) {
        bar.style.display = 'none';
        svgLayer.innerHTML = '';
        applyScanVisualState(id);
        return;
    }

    bar.style.display = 'flex';
    applyScanVisualState(id);

    if (!svgCache[id]) {
        const res = await fetch(sheetMeta.svg);
        svgCache[id] = res.ok ? await res.text() : '';
    }
    svgLayer.innerHTML = svgCache[id];
    syncVectorLayerVisibility();
}

function syncVectorLayerVisibility() {
    const svgLayer = document.getElementById('vectorSvgLayer');
    if (!svgLayer) return;
    svgLayer.style.display = vectorMasterEnabled ? 'block' : 'none';
    svgLayer.querySelectorAll('.vec-layer').forEach(g => {
        const layerName = g.getAttribute('data-layer');
        g.style.display = activeLayers.has(layerName) ? 'inline' : 'none';
    });
}

function applyScanVisualState(id) {
    const modalImg = document.getElementById('modalImage');
    if (!modalImg) return;
    if (!isSheetCalibrated(id)) {
        modalImg.classList.remove('dark-blueprint');
        modalImg.style.opacity = '1';
        return;
    }
    modalImg.classList.toggle('dark-blueprint', darkBlueprintEnabled);
    modalImg.style.opacity = String(scanOpacity / 100);
}

function updateModalContent(item) {
    const modalImg = document.getElementById('modalImage');
    const caption = document.getElementById('modalCaption');

    modalImg.src = `drawings/${item.filename}`;
    const calMeta = vectorManifest.sheets ? vectorManifest.sheets[String(item.id)] : null;
    const calNote = calMeta
        ? `<p style="margin-top:0.35rem;font-size:0.8rem;color:#38bdf8;">&#10022; Sub-pixel calibrated to canonical WP #4 origin (${calMeta.scale_px_per_ft.toFixed(3)} px/ft, rot ${calMeta.rot_deg.toFixed(2)}&deg;)</p>`
        : '';
    caption.innerHTML = `<h3>${item.title_block}</h3><p>${item.contents}</p>${calNote}`;

    modalImg.onload = () => {
        renderAnnotations(item.id);
        renderVectorOverlay(item.id);
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

function endDrawing() {
    if (!isDrawing) return;
    isDrawing = false;

    if (currentTool === 'box' && currentBox) {
        const width = parseFloat(currentBox.style.width);
        const height = parseFloat(currentBox.style.height);

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
    layer.innerHTML = '';

    const data = componentsData[id];
    if (!data) return;

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

            label.onclick = () => {
                if (isEditMode && confirm(`Delete component "${comp.name}"?`)) {
                    componentsData[id].components = componentsData[id].components.filter(c => c.id !== comp.id);
                    renderAnnotations(id);
                }
            };

            box.appendChild(label);
            layer.appendChild(box);
        });
    }

    if (data.reference_point) {
        const pt = document.createElement('div');
        pt.className = 'ref-point';
        pt.style.left = data.reference_point.x + '%';
        pt.style.top = data.reference_point.y + '%';
        pt.title = "Reference Point (Origin)";

        pt.onclick = () => {
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
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}
