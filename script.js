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
    // OJO: En el CSS nuevo el contenedor se llama 'products-container'
    // Asegúrate de que en tu index.html el div tenga id="products-container"
    const grid = document.getElementById('products-container'); 
    const sortMode = document.getElementById('sortSelect').value;

    // Lógica de Ordenación
    products.sort((a, b) => {
        if (sortMode === 'real_value') return a.realCostPerKg - b.realCostPerKg; // El más barato real primero
        if (sortMode === 'price_asc') return a.price - b.price;
        if (sortMode === 'purity_desc') return b.protein_percent - a.protein_percent;
        return 0;
    });

    grid.innerHTML = '';

    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align:center; grid-column: 1/-1; color: #64748b;">No hay productos que coincidan.</p>';
        return;
    }

    // Generar el HTML NUEVO (Estilo Tarjeta Limpia)
    products.forEach(product => {
        // Formatear números para que queden bonitos (2 decimales)
        const displayRealPrice = product.realCostPerKg.toFixed(2);
        const displayPricePerKg = product.pricePerKg.toFixed(2);

        // Usamos las imágenes locales si existen, o un placeholder
        const imageSrc = product.local_image || product.image || 'img/placeholder.png';

        const html = `
            <article class="product-card">
                <div class="card-header">
                    <img src="${imageSrc}" alt="${product.name}" class="product-img" onerror="this.src='img/placeholder.png'">
                    <div class="product-brand">${product.brand}</div>
                    <h2 class="product-title">${product.name}</h2>
                </div>

                <div class="card-body">
                    <div class="price-section">
                        <div class="main-price">
                            ${product.price}<span class="currency">€</span>
                        </div>
                        <div class="price-label">Precio Final</div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-value highlight">${displayRealPrice}€</span>
                            <span class="stat-label">Coste Real / Kg Pureza</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${displayPricePerKg}€</span>
                            <span class="stat-label">Precio / Kg Peso</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${product.protein_percent}%</span>
                            <span class="stat-label">Pureza</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${product.weight_kg}kg</span>
                            <span class="stat-label">Formato</span>
                        </div>
                    </div>
                </div>

                <div class="card-footer">
                    <a href="${product.link}" target="_blank" class="btn-buy">VER OFERTA</a>
                    <div class="update-info">Actualizado: ${product.last_update}</div>
                </div>
            </article>
        `;
        grid.innerHTML += html;
    });
}