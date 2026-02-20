const DATA_URL = 'data.json';
let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    loadData();

    document.getElementById('searchInput').addEventListener('input', (e) => {
        const activeBrand = document.querySelector('.brand-chip.active')?.innerText || 'Todo';
        filterProducts(e.target.value, activeBrand);
    });

    document.getElementById('sortSelect').addEventListener('change', () => {
        renderProducts(allProducts); 
    });
});

async function loadData() {
    try {
        const response = await fetch(DATA_URL + '?v=' + new Date().getTime());
        let rawData = await response.json();
        
        allProducts = rawData.map(product => {
            const weight = product.weight_kg || 1.0;
            const price = parseFloat(product.price);
            const purity = product.protein_percent || 0;
            
            const pricePerKg = (price / weight).toFixed(2);
            
            let realCostPerKg = 'N/A';
            if (purity > 0) {
                realCostPerKg = (price / (weight * (purity / 100))).toFixed(2);
            }

            return {
                ...product,
                pricePerKg: pricePerKg,
                realCostPerKg: realCostPerKg
            };
        });

        renderProducts(allProducts);
        
    } catch (error) {
        console.error(error);
        document.getElementById('products-container').innerHTML = '<p style="text-align:center; width:100%;">Cargando datos del mercado...</p>';
    }
}

// Función maestra que aplica todos los filtros en cascada
function updateDisplay() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const activeBrandChip = document.querySelector('.brand-chip.active');
    const categoryFilter = activeBrandChip ? activeBrandChip.innerText : 'Todo';
    const sortBy = document.getElementById('sortSelect').value;

    // 1. FILTRADO
    let filtered = allProducts.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchTerm) || 
                              p.brand.toLowerCase().includes(searchTerm);
        
        const matchesCategory = (categoryFilter === 'Todo') || 
                                (p.category.toLowerCase() === categoryFilter.toLowerCase());
        
        return matchesSearch && matchesCategory;
    });

    // 2. ORDENACIÓN (Aquí es donde arreglamos lo de la pureza)
    filtered.sort((a, b) => {
        switch (sortBy) {
            case 'price-asc':
                return parseFloat(a.price) - parseFloat(b.price);
            case 'price-desc':
                return parseFloat(b.price) - parseFloat(a.price);
            case 'purity-desc':
                // Forzamos que la creatina (0 pureza) vaya al final
                return (b.protein_percent || 0) - (a.protein_percent || 0);
            case 'kg-price-asc':
                return parseFloat(a.pricePerKg) - parseFloat(b.pricePerKg);
            default:
                return 0;
        }
    });

    renderProducts(filtered);
}

// Modifica los event listeners para que todos llamen a updateDisplay
document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    loadData();

    document.getElementById('searchInput').addEventListener('input', updateDisplay);
    document.getElementById('sortSelect').addEventListener('change', updateDisplay);
});

// Modifica la función de los botones de categoría
function filterData(brand, event) {
    document.querySelectorAll('.brand-chip').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // Por si se llama programáticamente
        const chips = document.querySelectorAll('.brand-chip');
        chips.forEach(c => { if(c.innerText === brand) c.classList.add('active'); });
    }
    updateDisplay();
}

function filterProducts(search, categoryFilter) {
    let filtered = allProducts;

    if (categoryFilter && categoryFilter !== 'Todo' && categoryFilter !== 'all') {
        filtered = filtered.filter(p => p.category.toLowerCase() === categoryFilter.toLowerCase());
    }

    if (search) {
        const term = search.toLowerCase();
        filtered = filtered.filter(p => 
            // Corregido: volvemos a usar 'name' en lugar de 'fixed_name'
            p.name.toLowerCase().includes(term) || 
            p.brand.toLowerCase().includes(term)
        );
    }

    renderProducts(filtered);
}

function renderProducts(products) {
    const container = document.getElementById('products-container');
    container.innerHTML = '';

    products.forEach(product => {
        let statsHTML = '';
        
        // Configuración de estadísticas según categoría
        if (product.category === 'protein') {
            statsHTML = `
                <div class="stat-item">
                    <span class="stat-value highlight">${product.protein_percent}%</span>
                    <span class="stat-label">Pureza</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${product.realCostPerKg}€</span>
                    <span class="stat-label">Kg Puro</span>
                </div>
            `;
        } else if (product.category === 'creatina') {
            statsHTML = `
                <div class="stat-item">
                    <span class="stat-value highlight">Mono</span>
                    <span class="stat-label">Tipo</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${product.pricePerKg}€</span>
                    <span class="stat-label">Precio/Kg</span>
                </div>
            `;
        }

        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="card-header">
                <img src="${product.image}" alt="${product.name}" class="product-img" onerror="this.src='img/placeholder.jpg'">
            </div>
            
            <div class="card-body">
                <div class="card-brand">${product.brand}</div>
                <h3 class="card-title">${product.name}</h3>
                
                <div class="price-section">
                    <div class="main-price">${product.price}<span class="currency">€</span></div>
                    <div class="price-label">MEJOR PRECIO HOY</div>
                </div>

                <div class="stats-grid">
                    ${statsHTML}
                </div>
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
}