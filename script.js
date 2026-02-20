const DATA_URL = 'data.json';
let allProducts = [];

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Si usas iconos en la barra de búsqueda, iniciamos Lucide, 
    // pero en las tarjetas nuevas ya no los usamos para que quede más limpio.
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    loadData();

    // Eventos de búsqueda y filtros
    document.getElementById('searchInput').addEventListener('input', (e) => {
        // Asumimos que el filtro de marca "Todo" es el activo por defecto
        const activeBrand = document.querySelector('.brand-chip.active')?.innerText || 'Todo';
        filterProducts(e.target.value, activeBrand);
    });

    document.getElementById('sortSelect').addEventListener('change', () => {
        // Volver a renderizar con el orden nuevo
        renderProducts(allProducts); 
    });
});

async function loadData() {
    try {
        // Truco del '?v=' para evitar que el navegador guarde el JSON viejo en caché
        const response = await fetch(DATA_URL + '?v=' + new Date().getTime());
        allProducts = await response.json();
        
        // Pre-calculamos valores útiles para ordenar
        allProducts = allProducts.map(product => {
            const weight = product.weight_kg || 1.0;
            const price = parseFloat(product.price);
            const purity = product.protein_percent || 0;
            
            // Cálculo: Precio por Kilo de producto
            const pricePerKg = price / weight;
            
            // Cálculo: Coste Real por Kilo de Proteína Pura
            // Si vale 20€ el kilo y tiene 50% pureza, el kilo real cuesta 40€.
            let realCostPerKg = 999;
            if (purity > 0) {
                realCostPerKg = pricePerKg / (purity / 100);
            }

            return {
                ...product,
                pricePerKg: pricePerKg,
                realCostPerKg: realCostPerKg
            };
        });

        renderProducts(allProducts);
        
    } catch (error) {
        console.error("Error cargando datos:", error);
        document.getElementById('products-container').innerHTML = '<p style="text-align:center; width:100%;">Cargando datos del mercado...</p>';
    }
}

// Función para manejar los botones de marcas (HTML onclick)
function filterData(brand) {
    // Gestionar clases activas visuales
    document.querySelectorAll('.brand-chip').forEach(btn => btn.classList.remove('active'));
    // Si el evento viene de un click, activamos ese botón
    if(event && event.target) event.target.classList.add('active'); 

    const searchTerm = document.getElementById('searchInput').value;
    filterProducts(searchTerm, brand);
}

function filterProducts(search, categoryFilter) {
    let filtered = allProducts;

    // 1. FILTRO POR CATEGORÍA (Los botones)
    // Si el filtro no es 'all' ni 'Todo', filtramos por la etiqueta 'category' del JSON
    if (categoryFilter && categoryFilter !== 'Todo' && categoryFilter !== 'all') {
        filtered = filtered.filter(p => p.category.toLowerCase() === categoryFilter.toLowerCase());
    }

    // 2. FILTRO DE BÚSQUEDA (Barra de texto)
    // Aquí seguimos buscando por Nombre o Marca para que el usuario pueda escribir "MyProtein"
    if (search) {
        const term = search.toLowerCase();
        filtered = filtered.filter(p => 
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
            const purePrice = (product.price / (product.weight_kg * (product.protein_percent / 100))).toFixed(2);
            statsHTML = `
                <div class="stat"><span>Pureza:</span> ${product.protein_percent}%</div>
                <div class="stat"><span>Precio/Kg (Puro):</span> ${purePrice}€</div>
            `;
        } else if (product.category === 'creatina') {
            const pricePerKg = (product.price / product.weight_kg).toFixed(2);
            statsHTML = `
                <div class="stat"><span>Tipo:</span> Monohidrato</div>
                <div class="stat"><span>Precio/Kg:</span> ${pricePerKg}€</div>
            `;
        }

        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
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