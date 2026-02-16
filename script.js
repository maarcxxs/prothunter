// --- DATOS MOCKEADOS (Esto es lo que tu Python debería escupir en JSON) ---
const products = [
    {
        id: 1,
        name: "Impact Whey Protein",
        brand: "MyProtein",
        type: "whey",
        price: 24.99,
        weight_kg: 1.0,
        protein_percent: 72, // 72% de pureza
        image: "https://static.thcdn.com/productimg/1600/1600/10530943-1954885871295725.jpg",
        link: "#"
    },
    {
        id: 2,
        name: "Gold Standard 100% Whey",
        brand: "Optimum Nutrition",
        type: "whey",
        price: 34.90,
        weight_kg: 0.9,
        protein_percent: 79,
        image: "https://m.media-amazon.com/images/I/61JS6lWc+AL._AC_SL1080_.jpg",
        link: "#"
    },
    {
        id: 3,
        name: "IsoPrime CFM",
        brand: "Amix",
        type: "isolate",
        price: 45.00,
        weight_kg: 1.0,
        protein_percent: 90, // Muy pura
        image: "https://www.amix.es/237-large_default/isoprime-cfm-1kg.jpg",
        link: "#"
    },
    {
        id: 4,
        name: "Vegan Protein Blend",
        brand: "MyProtein",
        type: "vegan",
        price: 18.99,
        weight_kg: 1.0,
        protein_percent: 65,
        image: "https://static.thcdn.com/productimg/1600/1600/11317537-1234676527582531.jpg",
        link: "#"
    }
];

// --- LÓGICA DE NEGOCIO (El cerebro) ---

// Función para calcular el precio real por gramo de proteína (TU KPI CLAVE)
function calculateRealPrice(price, weight, percentage) {
    const totalProteinGrams = (weight * 1000) * (percentage / 100);
    const pricePerGram = price / totalProteinGrams;
    return (pricePerGram * 100).toFixed(2); // Precio por cada 100g de proteína pura
}

// Función para renderizar las tarjetas
function renderProducts(data) {
    const grid = document.getElementById('productGrid');
    grid.innerHTML = ''; // Limpiar grid

    data.forEach(product => {
        const realPrice = calculateRealPrice(product.price, product.weight_kg, product.protein_percent);
        
        // Etiqueta dinámica: Si el precio real es bajo (<3.5€/100g pura), es CHOLLO
        let badgeHTML = '';
        if (realPrice < 3.5) {
            badgeHTML = `<div class="card-badge">CHOLLO 🔥</div>`;
        } else if (product.protein_percent > 85) {
            badgeHTML = `<div class="card-badge" style="background:#3b82f6">CALIDAD 💎</div>`;
        }

        const card = document.createElement('article');
        card.className = 'card';
        card.innerHTML = `
            ${badgeHTML}
            <img src="${product.image}" alt="${product.name}" class="card-img">
            <div class="card-body">
                <span class="card-brand">${product.brand}</span>
                <h3 class="card-title">${product.name}</h3>
                
                <div class="data-row">
                    <span>Precio lista:</span>
                    <span class="price-big">${product.price}€</span>
                </div>
                
                <div class="data-row" style="color: var(--accent)">
                    <span>Precio real (100g prote):</span>
                    <span class="real-price">${realPrice}€</span>
                </div>

                <div class="data-row">
                    <span style="font-size: 0.8rem; color: #94a3b8">Pureza: ${product.protein_percent}%</span>
                </div>
                <div class="purity-container">
                    <div class="purity-bar" style="width: ${product.protein_percent}%"></div>
                </div>

                <button class="btn-buy" onclick="window.open('${product.link}', '_blank')">
                    VER OFERTA <i data-lucide="external-link" size="16"></i>
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
    
    // Reinicializar iconos para los nuevos elementos
    if(typeof lucide !== 'undefined') lucide.createIcons();
}

// --- FILTROS Y ORDENACIÓN ---

// Escuchar el buscador
document.getElementById('searchInput').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = products.filter(p => p.name.toLowerCase().includes(term) || p.brand.toLowerCase().includes(term));
    renderProducts(filtered);
});

// Escuchar el Select de ordenación
document.getElementById('sortSelect').addEventListener('change', (e) => {
    const criteria = e.target.value;
    let sorted = [...products]; // Copia del array para no mutar el original

    if (criteria === 'price_asc') {
        sorted.sort((a, b) => a.price - b.price);
    } else if (criteria === 'purity_desc') {
        sorted.sort((a, b) => b.protein_percent - a.protein_percent);
    } else if (criteria === 'real_value') {
        sorted.sort((a, b) => {
            const realA = calculateRealPrice(a.price, a.weight_kg, a.protein_percent);
            const realB = calculateRealPrice(b.price, b.weight_kg, b.protein_percent);
            return realA - realB;
        });
    }
    renderProducts(sorted);
});

// Botones de filtro
function filterData(type) {
    // Actualizar estilo botones
    document.querySelectorAll('.filter-group .btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    if (type === 'all') {
        renderProducts(products);
    } else {
        const filtered = products.filter(p => p.type === type);
        renderProducts(filtered);
    }
}

// Cargar inicial
renderProducts(products);