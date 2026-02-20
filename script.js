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

function filterData(brand, event) {
    document.querySelectorAll('.brand-chip').forEach(btn => btn.classList.remove('active'));
    if(event && event.target) event.target.classList.add('active'); 

    const searchTerm = document.getElementById('searchInput').value;
    filterProducts(searchTerm, brand);
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
        
        if (product.category === 'protein') {
            statsHTML = `
                <div class="stat"><span>Pureza:</span> ${product.protein_percent}%</div>
                <div class="stat"><span>Precio/Kg (Puro):</span> ${product.realCostPerKg}€</div>
            `;
        } else if (product.category === 'creatina') {
            statsHTML = `
                <div class="stat"><span>Tipo:</span> Monohidrato</div>
                <div class="stat"><span>Precio/Kg:</span> ${product.pricePerKg}€</div>
            `;
        }

        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}" onerror="this.src='img/placeholder.jpg'">
            <div class="card-info">
                <h3>${product.brand}</h3>
                <p class="product-name">${product.name}</p>
                <div class="price-tag">${product.price}€</div>
                <div class="stats-container">
                    ${statsHTML}
                </div>
            </div>
            <div class="card-footer">
                <a href="${product.link}" target="_blank" class="btn-buy">VER OFERTA</a>
            </div>
        `;
        container.appendChild(card);
    });
}