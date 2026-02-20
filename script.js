const DATA_URL = 'data.json';
let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    loadData();

    // Listeners centralizados
    document.getElementById('searchInput').addEventListener('input', updateDisplay);
    document.getElementById('sortSelect').addEventListener('change', updateDisplay);
});

async function loadData() {
    try {
        const response = await fetch(DATA_URL + '?v=' + new Date().getTime());
        let rawData = await response.json();
        
        allProducts = rawData.map(p => {
            const weight = p.weight_kg || 1.0;
            const price = parseFloat(p.price);
            const purity = p.protein_percent || 0;
            return {
                ...p,
                pricePerKg: (price / weight).toFixed(2),
                realCostPerKg: purity > 0 ? (price / (weight * (purity / 100))).toFixed(2) : 'N/A'
            };
        });

        updateDisplay();
    } catch (error) {
        console.error("Error de carga:", error);
    }
}

function updateDisplay() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const activeChip = document.querySelector('.brand-chip.active');
    const category = activeChip ? activeChip.getAttribute('data-category') : 'all';
    const sortBy = document.getElementById('sortSelect').value;

    // A. Gestión dinámica del Selector (Solo pureza para proteínas)
    const sortSelect = document.getElementById('sortSelect');
    const purityOption = sortSelect.querySelector('option[value="purity_desc"]');
    const realPriceOption = sortSelect.querySelector('option[value="real_value"]');

    if (category === 'protein') {
        purityOption.style.display = 'block';
        realPriceOption.style.display = 'block';
    } else {
        purityOption.style.display = 'none';
        realPriceOption.style.display = 'none';
        // Si estaba seleccionado algo de prote, resetear a precio barato
        if (sortBy === 'purity_desc' || sortBy === 'real_value') sortSelect.value = 'price_asc';
    }

    // B. Filtrado
    let filtered = allProducts.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchTerm) || p.brand.toLowerCase().includes(searchTerm);
        const matchesCat = (category === 'all') || (p.category.toLowerCase() === category.toLowerCase());
        return matchesSearch && matchesCat;
    });

    // C. Ordenación
    filtered.sort((a, b) => {
        const val = document.getElementById('sortSelect').value;
        if (val === 'price_asc') return parseFloat(a.price) - parseFloat(b.price);
        if (val === 'purity_desc') return (b.protein_percent || 0) - (a.protein_percent || 0);
        if (val === 'real_value') return (parseFloat(a.realCostPerKg) || 999) - (parseFloat(b.realCostPerKg) || 999);
        return 0;
    });

    renderProducts(filtered);
}

function filterData(category, event) {
    // 1. Gestionar color verde (clase active)
    document.querySelectorAll('.brand-chip').forEach(btn => btn.classList.remove('active'));
    
    // Si el evento existe (click), activamos. Si no, buscamos por atributo.
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }

    // 2. Ejecutar actualización de señal
    updateDisplay();
}

function renderProducts(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align:center; padding: 3rem; color: var(--text-dim);">No se han encontrado suplementos con esos filtros.</p>';
        return;
    }

    products.forEach(product => {
        let statsHTML = product.category === 'protein' ? `
            <div class="stat-item"><span class="stat-value highlight">${product.protein_percent}%</span><span class="stat-label">Pureza</span></div>
            <div class="stat-item"><span class="stat-value">${product.realCostPerKg}€</span><span class="stat-label">Kg Puro</span></div>
        ` : `
            <div class="stat-item"><span class="stat-value highlight">Mono</span><span class="stat-label">Tipo</span></div>
            <div class="stat-item"><span class="stat-value">${product.pricePerKg}€</span><span class="stat-label">Precio/Kg</span></div>
        `;

        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="card-header"><img src="${product.image}" class="product-img" onerror="this.src='img/placeholder.jpg'"></div>
            <div class="card-body">
                <div class="card-brand">${product.brand}</div>
                <h3 class="card-title">${product.name}</h3>
                <div class="price-section">
                    <div class="main-price">${product.price}<span class="currency">€</span></div>
                    <div class="price-label">MEJOR PRECIO HOY</div>
                </div>
                <div class="stats-grid">${statsHTML}</div>
            </div>
            <div class="card-footer">
                <a href="${product.link}" target="_blank" class="btn-buy">IR A LA OFERTA</a>
            </div>
        `;
        container.appendChild(card);
    });
}