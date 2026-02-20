const DATA_URL = 'data.json';
let allProducts = [];
let currentCategory = 'all'; // El "cerebro" que recuerda dónde estamos

document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    loadData();

    // Listeners del buscador y del desplegable
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
                // Asignamos un valor muy alto (9999) si no tiene pureza para que no rompa el orden
                realCostPerKg: purity > 0 ? (price / (weight * (purity / 100))).toFixed(2) : '9999'
            };
        });

        updateDisplay();
    } catch (error) {
        console.error("Error cargando los datos:", error);
    }
}

// Esta es la función que se llama desde tu HTML al hacer clic en las marcas/categorías
window.filterData = function(category) {
    currentCategory = category.toLowerCase(); // Guardamos el estado en la memoria global

    // 1. Limpiamos todos los botones
    document.querySelectorAll('.brand-chip').forEach(btn => {
        btn.classList.remove('active');
        // 2. Buscamos el botón que acabas de pulsar leyendo su atributo onclick
        if (btn.getAttribute('onclick').includes(`'${category}'`) || btn.getAttribute('onclick').includes(`"${category}"`)) {
            btn.classList.add('active'); // Lo ponemos en verde
        }
    });

    // 3. Reseteamos el select al filtro por defecto para evitar comportamientos raros
    document.getElementById('sortSelect').value = 'price_asc';
    
    // 4. Procesamos la señal
    updateDisplay();
};

function updateDisplay() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const sortSelect = document.getElementById('sortSelect');

    // --- MAGIA VISUAL: Ocultar o mostrar el filtro ---
    // Si estamos en proteínas, mostramos el desplegable. Si no, lo fulminamos.
    if (currentCategory === 'protein' || currentCategory === 'proteína') {
        sortSelect.style.display = 'inline-block';
    } else {
        sortSelect.style.display = 'none';
    }

    // --- 1. FILTRADO MULTICANAL ---
    let filtered = allProducts.filter(p => {
        // Búsqueda por texto
        const matchesSearch = p.name.toLowerCase().includes(searchTerm) || p.brand.toLowerCase().includes(searchTerm);
        
        // Búsqueda por categoría
        const pCat = p.category ? p.category.toLowerCase() : '';
        const matchesCat = (currentCategory === 'all' || currentCategory === 'todo') || (pCat === currentCategory);
        
        return matchesSearch && matchesCat;
    });

    // --- 2. ORDENACIÓN ---
    // Si el select está oculto, forzamos ordenar por precio barato por defecto
    const sortBy = sortSelect.style.display === 'none' ? 'price_asc' : sortSelect.value;

    filtered.sort((a, b) => {
        if (sortBy === 'price_asc') {
            return parseFloat(a.price) - parseFloat(b.price);
        }
        if (sortBy === 'purity_desc') {
            return parseFloat(b.protein_percent || 0) - parseFloat(a.protein_percent || 0);
        }
        if (sortBy === 'real_value') {
            return parseFloat(a.realCostPerKg) - parseFloat(b.realCostPerKg);
        }
        return 0;
    });

    renderProducts(filtered);
}

function renderProducts(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align:center; padding: 3rem; color: var(--text-dim);">No se han encontrado suplementos en esta categoría.</p>';
        return;
    }

    products.forEach(product => {
        let statsHTML = '';
        let gridStyle = '';
        
        if (product.category === 'protein') {
            statsHTML = `
                <div class="stat-item"><span class="stat-value highlight">${product.protein_percent}%</span><span class="stat-label">Pureza</span></div>
                <div class="stat-item"><span class="stat-value">${product.pricePerKg}€</span><span class="stat-label">Precio/Kg</span></div>
                <div class="stat-item"><span class="stat-value">${product.realCostPerKg}€</span><span class="stat-label">Kg Puro</span></div>
            `;
            gridStyle = 'grid-template-columns: repeat(3, 1fr);';
        } else if (product.category === 'creatina') {
            statsHTML = `
                <div class="stat-item"><span class="stat-value highlight">Mono</span><span class="stat-label">Tipo</span></div>
                <div class="stat-item"><span class="stat-value">${product.pricePerKg}€</span><span class="stat-label">Precio/Kg</span></div>
            `;
            gridStyle = 'grid-template-columns: repeat(2, 1fr);';
        } else {
            statsHTML = `
                <div class="stat-item"><span class="stat-value highlight">${product.pricePerKg}€</span><span class="stat-label">Precio/Kg</span></div>
            `;
            gridStyle = 'grid-template-columns: 1fr;';
        }

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
                <div class="stats-grid" style="${gridStyle}">${statsHTML}</div>
            </div>
            <div class="card-footer">
                <a href="${product.link}" target="_blank" class="btn-buy">IR A LA OFERTA</a>
                <div class="update-info">
                    <i class="lucide-refresh-cw" style="width:10px; display:inline-block;"></i> 
                    Verificado: ${product.last_update ? product.last_update.split(' ')[0] : 'Hoy'}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    if (typeof lucide !== 'undefined') lucide.createIcons();
}