const DATA_URL = 'data.json';
let allProducts = [];

const ICONS = {
    trending: '<i data-lucide="trending-up"></i>',
    fire: '<i data-lucide="flame"></i>',
    award: '<i data-lucide="award"></i>'
};

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    loadData();

    document.getElementById('searchInput').addEventListener('input', (e) => {
        filterProducts(e.target.value, document.querySelector('.brand-chip.active').innerText);
    });

    document.getElementById('sortSelect').addEventListener('change', () => {
        renderProducts(allProducts); 
    });
});

async function loadData() {
    try {
        const response = await fetch(DATA_URL + '?v=' + new Date().getTime());
        allProducts = await response.json();
      
        allProducts = allProducts.map(product => {
            return {
                ...product,
                realPricePer100g: calculateRealPrice(product)
            };
        });

        renderProducts(allProducts);
        updateLastUpdate(allProducts);
    } catch (error) {
        console.error("Error cargando datos:", error);
        document.getElementById('productGrid').innerHTML = '<p style="text-align:center; grid-column: 1/-1;">Cargando datos del mercado...</p>';
    }
}


function calculateRealPrice(product) {
    const weightKg = product.weight_kg || 1.0;
    const totalGrams = weightKg * 1000;
    const realProteinGrams = totalGrams * (product.protein_percent / 100);
    if (realProteinGrams <= 0) return 999; 
    
    return (product.price / (realProteinGrams / 100)).toFixed(2);
}

function filterData(brand) {
    document.querySelectorAll('.brand-chip').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active'); 

    const searchTerm = document.getElementById('searchInput').value;
    filterProducts(searchTerm, brand);
}

function filterProducts(search, brandFilter) {
    let filtered = allProducts;

    // filtro de marca
    if (brandFilter && brandFilter !== 'Todo' && brandFilter !== 'all') {
        filtered = filtered.filter(p => p.brand.toLowerCase() === brandFilter.toLowerCase());
    }

    // filtro de busqudda
    if (search) {
        filtered = filtered.filter(p => 
            p.name.toLowerCase().includes(search.toLowerCase()) || 
            p.brand.toLowerCase().includes(search.toLowerCase())
        );
    }

    renderProducts(filtered);
}

function renderProducts(products) {
    const grid = document.getElementById('productGrid');
    const sortMode = document.getElementById('sortSelect').value;

    // ordenación dinamica
    products.sort((a, b) => {
        if (sortMode === 'real_value') return a.realPricePer100g - b.realPricePer100g; // Menor a mayor
        if (sortMode === 'price_asc') return a.price - b.price;
        if (sortMode === 'purity_desc') return b.protein_percent - a.protein_percent;
    });

    grid.innerHTML = '';

    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; opacity: 0.6;">No se encontraron proteínas con esos filtros.</p>';
        return;
    }

    // encontrar el mejor precio absoluto para ponerle la etiqueta "CHOLLO"
    const bestPrice = Math.min(...products.map(p => parseFloat(p.realPricePer100g)));

    products.forEach(product => {
        // Etiquetas dinámicas
        let badge = '';
        if (parseFloat(product.realPricePer100g) === bestPrice) {
            badge = `<div class="card-badge" style="background:var(--accent); color:#000;">${ICONS.fire} CHOLLO</div>`;
        } else if (product.protein_percent >= 90) {
            badge = `<div class="card-badge" style="background:#3b82f6;">${ICONS.award} PREMIUM</div>`;
        }

        const imageSrc = product.image || 'img/placeholder.png'; 
        
        const card = document.createElement('article');
        card.className = 'card';
        card.innerHTML = `
            ${badge}
            <div class="img-container">
                <img src="${imageSrc}" alt="${product.name}" class="card-img" onerror="this.src='https://placehold.co/400x400/1e293b/FFF?text=Protein'">
            </div>
            <div class="card-body">
                <span class="card-brand">${product.brand}</span>
                <h3 class="card-title">${product.name}</h3>
                
                <div class="specs">
                    <span><i data-lucide="dumbbell"></i> ${product.protein_percent}% Pureza</span>
                    <span><i data-lucide="weight"></i> ${product.weight_kg}kg</span>
                </div>

                <div class="price-box">
                    <div class="row">
                        <span class="unit-price">Real: <strong>${product.realPricePer100g}€</strong> /100g prot.</span>
                    </div>
                    <div class="row" style="margin-top:0.5rem; align-items:end;">
                        <span class="big-price">${product.price}€</span>
                        <a href="${product.link}" target="_blank" class="btn-buy">VER OFERTA</a>
                    </div>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });

    lucide.createIcons(); 
    
   
    const countLabel = document.querySelector('.result-count');
    if(countLabel) countLabel.innerText = `Mostrando ${products.length} productos en tiempo real`;
}

function updateLastUpdate(data) {
    if(data.length > 0 && data[0].last_update) {
        console.log("Última actualización de precios:", data[0].last_update);
    }
}