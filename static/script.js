function openTab(tabName) {
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    // Deactivate all tab buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Show specific tab content
    document.getElementById(tabName).classList.add('active');

    // Activate specific button
    const activeButton = Array.from(buttons).find(btn => btn.getAttribute('onclick').includes(tabName));
    if (activeButton) {
        activeButton.classList.add('active');
    }

    if (tabName === 'summary') {
        loadSummary();
    } else if (tabName === 'inventory' || tabName === 'products') {
        loadInventory();
    } else if (tabName === 'statistics') {
        loadStatistics();
    } else if (tabName === 'agenda') {
        loadAppointments();
    } else if (tabName === 'config') {
        loadUsers();
    } else if (tabName === 'monthly-expenses') {
        loadMonthlyExpenses();
    }
}

// Sede Management
function getCurrentSede() {
    const selector = document.getElementById('sedeSelector');
    return selector ? selector.value : 'Bolivia';
}

function changeSede() {
    const sede = getCurrentSede();
    localStorage.setItem('currentSede', sede);

    // Reload current data based on active tab
    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab) {
        const tabId = activeTab.id;
        if (tabId === 'summary') {
            loadSummary();
        } else if (tabId === 'inventory' || tabId === 'products') {
            loadInventory();
        } else if (tabId === 'statistics') {
            loadStatistics();
        } else if (tabId === 'agenda') {
            loadAppointments();
        } else if (tabId === 'monthly-expenses') {
            loadMonthlyExpenses();
        }
    }
}

let currentSummaryData = [];
let currentTotals = {};
let currentInventory = [];
let payrollChart;
let salesChart;
let timelineChart;
let servicesChart;
let predictionChart;
let revenueHeatmapChart;
let serviceDemandChart;

async function loadSummary() {
    try {
        // Get the selected date or use today's date
        const dateInput = document.getElementById('filterDate');
        if (!dateInput.value) {
            // Set to today if not set
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        }

        const selectedDate = dateInput.value;
        const sede = getCurrentSede();
        const response = await fetch(`/api/summary?date=${selectedDate}&sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            currentSummaryData = result.data;
            currentTotals = result.totals;
            applyFilters();
        } else {
            showNotification(result.message || 'Error al cargar resumen', true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión: ' + error.message, true);
    }
}

function applyFilters() {
    const stylistFilter = document.getElementById('filterStylist').value;
    const serviceFilter = document.getElementById('filterService').value;

    let filteredData = currentSummaryData;

    if (stylistFilter) {
        filteredData = filteredData.filter(item => item.estilista === stylistFilter);
    }

    if (serviceFilter) {
        filteredData = filteredData.filter(item => item.descripcion === serviceFilter);
    }

    // Calculate totals from filtered data
    let totalValor = 0;
    let totalComision = 0;
    const paymentTotals = {
        'Efectivo': 0,
        'Tarjeta': 0,
        'NEQUI': 0,
        'Daviplata': 0
    };

    filteredData.forEach(item => {
        totalValor += item.valor;
        totalComision += item.comision;

        // Sum by payment method
        if (paymentTotals.hasOwnProperty(item.metodo_pago)) {
            paymentTotals[item.metodo_pago] += item.valor;
        }
    });

    // Get total expenses from currentTotals (not filtered)
    const totalGastos = currentTotals.gastos || 0;

    // Calculate profit
    const utilidad = totalValor - totalGastos - totalComision;

    // Populate the table
    const tbody = document.getElementById('summaryBody');
    tbody.innerHTML = '';

    filteredData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.estilista}</td>
            <td>${item.descripcion} <span class="badge">${item.tipo}</span></td>
            <td>$${item.valor.toLocaleString()}</td>
            <td>$${item.comision.toLocaleString()}</td>
            <td><span class="payment-badge">${item.metodo_pago}</span></td>
            <td>
                <button class="edit-btn" onclick="enableEdit(this, '${item.sheet}', ${item.id}, ${item.valor}, ${item.comision})" style="background:none; border:none; cursor:pointer;" title="Editar">✏️</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    // Update totals
    document.getElementById('totalValue').textContent = `$${totalValor.toLocaleString()}`;
    document.getElementById('totalCommission').textContent = `$${totalComision.toLocaleString()}`;
    document.getElementById('totalExpenses').textContent = `$${totalGastos.toLocaleString()}`;
    document.getElementById('totalProfit').textContent = `$${utilidad.toLocaleString()}`;

    // Display payment method subtotals
    const paymentSubtotalsDiv = document.getElementById('paymentSubtotals');
    paymentSubtotalsDiv.innerHTML = '';

    for (const [method, total] of Object.entries(paymentTotals)) {
        if (total > 0) {
            const card = document.createElement('div');
            card.className = 'subtotal-card';
            card.innerHTML = `
                <span class="payment-method">${method}</span>
                <span class="payment-total">$${total.toLocaleString()}</span>
            `;
            paymentSubtotalsDiv.appendChild(card);
        }
    }

    // Check cash sufficiency for commissions
    const cashTotal = paymentTotals['Efectivo'] || 0;
    const sufficiencyDiv = document.getElementById('cashSufficiencyIndicator');

    if (sufficiencyDiv) {
        sufficiencyDiv.style.display = 'block';
        if (cashTotal >= totalComision) {
            sufficiencyDiv.textContent = `Efectivo Suficiente para Comisiones (Sobran $${(cashTotal - totalComision).toLocaleString()})`;
            sufficiencyDiv.style.background = 'rgba(16, 185, 129, 0.2)';
            sufficiencyDiv.style.border = '1px solid rgba(16, 185, 129, 0.4)';
            sufficiencyDiv.style.color = '#34d399';
        } else {
            const deficit = totalComision - cashTotal;
            sufficiencyDiv.textContent = `Efectivo INSUFICIENTE para Comisiones (Faltan $${deficit.toLocaleString()})`;
            sufficiencyDiv.style.background = 'rgba(239, 68, 68, 0.2)';
            sufficiencyDiv.style.border = '1px solid rgba(239, 68, 68, 0.4)';
            sufficiencyDiv.style.color = '#f87171';
        }
    }
}

function downloadPDF() {
    const dateInput = document.getElementById('filterDate');
    let selectedDate = dateInput.value;
    const sede = getCurrentSede();

    if (!selectedDate) {
        selectedDate = new Date().toISOString().split('T')[0];
    }

    window.location.href = `/export_pdf?date=${selectedDate}&sede=${sede}`;
}

function showNotification(message, isError = false) {
    const notif = document.getElementById('notification');
    const msg = document.getElementById('notif-message');

    notif.classList.remove('hidden');
    // Trigger reflow
    void notif.offsetWidth;
    notif.classList.add('show');

    msg.textContent = message;

    if (isError) {
        notif.style.background = 'rgba(239, 68, 68, 0.2)';
        notif.style.borderColor = 'rgba(239, 68, 68, 0.4)';
        notif.style.color = '#f87171';
    } else {
        notif.style.background = 'rgba(16, 185, 129, 0.2)';
        notif.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        notif.style.color = '#34d399';
    }

    setTimeout(() => {
        notif.classList.remove('show');
        setTimeout(() => {
            notif.classList.add('hidden');
        }, 300);
    }, 3000);
}

async function handleFormSubmit(event, url) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Add current sede to data
    data.sede = getCurrentSede();

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        // Handle non-ok responses that might still be JSON
        if (response.status === 401) {
            showNotification('Sesión expirada. Recargando...', true);
            setTimeout(() => window.location.reload(), 2000);
            return;
        }

        let result;
        const text = await response.text();
        try {
            result = JSON.parse(text);
        } catch (e) {
            console.error('SERVER RESPONSE NOT JSON:', text);
            throw new Error(`Respuesta del servidor inválida (${response.status})`);
        }

        if (result.status === 'success') {
            let msg = result.message;
            if (result.comision) {
                msg += ` (Comisión: $${result.comision.toLocaleString()})`;
            }
            showNotification(msg);
            form.reset();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error: ' + error.message, true);
    }
}

document.getElementById('serviceForm').addEventListener('submit', (e) => handleFormSubmit(e, '/api/service'));
document.getElementById('productForm').addEventListener('submit', (e) => handleFormSubmit(e, '/api/product'));
document.getElementById('expenseForm').addEventListener('submit', (e) => handleFormSubmit(e, '/api/expense'));

async function handleStylistSubmit(event, url) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            form.reset();
            setTimeout(() => location.reload(), 1000); // Reload to update lists
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

document.getElementById('addStylistForm').addEventListener('submit', (e) => handleStylistSubmit(e, '/api/stylist'));
document.getElementById('addServiceForm').addEventListener('submit', (e) => handleStylistSubmit(e, '/api/service-item'));

async function deleteStylist(name) {
    if (!confirm(`¿Estás seguro de eliminar a ${name}?`)) return;

    try {
        const response = await fetch('/api/stylist', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

async function deleteService(name) {
    if (!confirm(`¿Estás seguro de eliminar el servicio ${name}?`)) return;

    try {
        const response = await fetch('/api/service-item', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

async function loadInventory() {
    try {
        const sede = getCurrentSede();
        const response = await fetch(`/api/inventory?sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            currentInventory = result.data;
            const tbody = document.getElementById('inventoryBody');
            tbody.innerHTML = '';

            // Populate datalist with existing products
            const datalist = document.getElementById('productList');
            datalist.innerHTML = '';

            result.data.forEach(item => {
                // Add to table
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.Producto}</td>
                    <td>${item.Marca || ''}</td>
                    <td>${item.Descripcion || ''}</td>
                    <td>${item.Cantidad}</td>
                    <td>${item.Unidad}</td>
                    <td>$${item.Valor.toLocaleString()}</td>
                    <td>${item.Estado || 'Nuevo'}</td>
                    <td>
                        <button class="delete-btn" onclick="deleteInventoryItem('${item.Producto}', '${item.Marca || ''}', '${item.Descripcion || ''}')">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(row);

                // Add to datalist
                const option = document.createElement('option');
                option.value = item.Producto;
                datalist.appendChild(option);
            });
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar inventario', true);
    }
}

async function deleteInventoryItem(producto, marca, descripcion) {
    if (!confirm(`¿Estás seguro de eliminar ${producto} del inventario?`)) return;

    try {
        const sede = getCurrentSede();
        const response = await fetch('/api/inventory', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto: producto,
                marca: marca || '',
                descripcion: descripcion || '',
                sede: sede
            }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            loadInventory();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

document.getElementById('inventoryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.sede = getCurrentSede();

    try {
        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            form.reset();
            loadInventory();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
});



async function loadStatistics() {
    // Register the plugin if available
    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
    }
    const monthInput = document.getElementById('statsMonth');
    let selectedMonth = monthInput.value;

    if (!selectedMonth) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        selectedMonth = `${year}-${month}`;
        monthInput.value = selectedMonth;
    }

    const sede = getCurrentSede();

    try {
        const response = await fetch(`/api/statistics?month=${selectedMonth}&sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            const data = result.data;

            // Update Cards
            document.getElementById('statsVentas').textContent = `$${data.totales.ventas.toLocaleString()}`;
            document.getElementById('statsGastos').textContent = `$${data.totales.gastos.toLocaleString()}`;
            document.getElementById('statsNomina').textContent = `$${data.totales.nomina.toLocaleString()}`;
            document.getElementById('statsNomina').textContent = `$${data.totales.nomina.toLocaleString()}`;
            document.getElementById('statsUtilidad').textContent = `$${data.totales.utilidad_operativa.toLocaleString()}`;

            // New stats
            if (document.getElementById('statsGastosFijos')) {
                document.getElementById('statsGastosFijos').textContent = `$${(data.totales.gastos_fijos || 0).toLocaleString()}`;
            }
            if (document.getElementById('statsUtilidadReal')) {
                document.getElementById('statsUtilidadReal').textContent = `$${(data.totales.utilidad_real || 0).toLocaleString()}`;
            }

            // --- CHARTS ---

            // 1. Payroll Pie Chart
            const payrollCtx = document.getElementById('payrollChart').getContext('2d');
            if (payrollChart) payrollChart.destroy();

            payrollChart = new Chart(payrollCtx, {
                type: 'pie',
                data: {
                    labels: Object.keys(data.nomina_por_estilista),
                    datasets: [{
                        data: Object.values(data.nomina_por_estilista),
                        backgroundColor: [
                            '#63ecf1', // Cyan (Primary)
                            '#325ff3', // Blue (Secondary)
                            '#ec4899', // Pink (Accent)
                            '#d4af37', // Gold (Accent)
                            '#8b5cf6', // Purple (Accent)
                            '#10b981'  // Green (Success)
                        ],
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#0f172a' } },
                        datalabels: {
                            color: '#0f172a',
                            display: function (context) {
                                return context.dataset.data[context.dataIndex] > 0;
                            },
                            font: {
                                weight: 'bold'
                            },
                            formatter: (value) => {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            });

            // 2. Sales Bar Chart - Sorted Descending
            const salesCtx = document.getElementById('salesChart').getContext('2d');
            if (salesChart) salesChart.destroy();

            // Sort entries
            const salesEntries = Object.entries(data.ventas_por_estilista).sort((a, b) => b[1] - a[1]);
            const salesLabels = salesEntries.map(e => e[0]);
            const salesData = salesEntries.map(e => e[1]);

            salesChart = new Chart(salesCtx, {
                type: 'bar',
                data: {
                    labels: salesLabels,
                    datasets: [
                        {
                            label: 'Ventas por Estilista',
                            data: salesData,
                            backgroundColor: 'rgba(99, 236, 241, 0.8)',
                            borderColor: '#00b8c4',
                            borderWidth: 1,
                            borderRadius: 6,
                            borderSkipped: false,
                        },
                        {
                            label: 'Sombra',
                            data: salesData.map(v => v * 0.15),
                            backgroundColor: 'rgba(0, 0, 0, 0.2)',
                            borderColor: 'transparent',
                            borderWidth: 0,
                            borderRadius: 6,
                            borderSkipped: false,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    layout: {
                        padding: {
                            top: 25
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#0f172a' }, grid: { color: 'rgba(0, 0, 0, 0.1)' } },
                        x: { ticks: { color: '#0f172a' }, grid: { display: false } }
                    },
                    plugins: {
                        legend: { display: false },
                        datalabels: {
                            color: '#0f172a',
                            anchor: 'end',
                            align: 'top',
                            formatter: (value) => '$' + value.toLocaleString(),
                            display: function(context) {
                                return context.datasetIndex === 0;
                            }
                        }
                    }
                }
            });

            // 3. Timeline Line Chart - Last 3 Years
            const timelineCtx = document.getElementById('timelineChart').getContext('2d');
            if (timelineChart) timelineChart.destroy();

            const years = Object.keys(data.timeline).sort();
            const colors = ['#325ff3', '#10b981', '#ec4899']; // Blue, Green, Pink
            const datasets = years.map((year, index) => ({
                label: year,
                data: data.timeline[year],
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length].replace(')', ', 0.2)').replace('rgb', 'rgba'),
                fill: false,
                tension: 0.4
            }));

            timelineChart = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    layout: {
                        padding: {
                            top: 20
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#0f172a' }, grid: { color: 'rgba(0, 0, 0, 0.1)' } },
                        x: { ticks: { color: '#0f172a' }, grid: { color: 'rgba(0, 0, 0, 0.05)' } }
                    },
                    plugins: {
                        legend: { labels: { color: '#0f172a' } },
                        datalabels: {
                            color: '#0f172a',
                            align: 'top',
                            formatter: (value) => '$' + value.toLocaleString()
                        }
                    }
                }
            });

            // 4. Top Services Horizontal Bar Chart - Sorted Descending
            const servicesCanvas = document.getElementById('servicesChart');
            if (servicesCanvas) {
                const servicesCtx = servicesCanvas.getContext('2d');
                if (servicesChart) servicesChart.destroy();

                // Sort entries
                const servicesEntries = Object.entries(data.top_servicios || {}).sort((a, b) => b[1] - a[1]);
                const servicesLabels = servicesEntries.map(e => e[0]);
                const servicesData = servicesEntries.map(e => e[1]);

                servicesChart = new Chart(servicesCtx, {
                    type: 'bar',
                    indexAxis: 'y',
                    data: {
                        labels: servicesLabels,
                        datasets: [
                            {
                                label: 'Cantidad de Servicios',
                                data: servicesData,
                                backgroundColor: 'rgba(236, 72, 153, 0.8)',
                                borderColor: '#be185d',
                                borderWidth: 1,
                                borderRadius: 6,
                                borderSkipped: false,
                            },
                            {
                                label: 'Sombra',
                                data: servicesData.map(v => v * 0.15),
                                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                                borderColor: 'transparent',
                                borderWidth: 0,
                                borderRadius: 6,
                                borderSkipped: false,
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        layout: {
                            padding: {
                                right: 30
                            }
                        },
                        scales: {
                            x: { beginAtZero: true, ticks: { color: '#0f172a' }, grid: { color: 'rgba(0, 0, 0, 0.1)' } },
                            y: { ticks: { color: '#0f172a' }, grid: { display: false } }
                        },
                        plugins: {
                            legend: { display: false },
                            datalabels: {
                                color: '#0f172a',
                                anchor: 'end',
                                align: 'right'
                            }
                        }
                    }
                });
            }



            // Update Payroll Table
            const payrollBody = document.getElementById('statsNominaBody');
            payrollBody.innerHTML = '';
            for (const [stylist, amount] of Object.entries(data.nomina_por_estilista)) {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${stylist}</td><td>$${amount.toLocaleString()}</td>`;
                payrollBody.appendChild(row);
            }

            // Update Sales Table
            const salesBody = document.getElementById('statsVentasBody');
            salesBody.innerHTML = '';
            for (const [stylist, amount] of Object.entries(data.ventas_por_estilista)) {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${stylist}</td><td>$${amount.toLocaleString()}</td>`;
                salesBody.appendChild(row);
            }

            // Update Inventory Table
            const inventoryBody = document.getElementById('statsInventoryBody');
            inventoryBody.innerHTML = '';
            data.inventario.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.producto}</td>
                    <td>${item.cantidad}</td>
                    <td>${item.unidad}</td>
                    <td>$${item.valor_total.toLocaleString()}</td>
                `;
                inventoryBody.appendChild(row);
            });

        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar estadísticas', true);
    }

    // Load prediction chart independently
    await loadPredictionChart();
    await loadRevenueHeatmap();
    await loadServiceDemand();
}

async function loadPredictionChart() {
    const sede = getCurrentSede();
    try {
        const response = await fetch(`/api/prediction?sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            const ctx = document.getElementById('predictionChart').getContext('2d');
            if (predictionChart) predictionChart.destroy();

            const histLabels = result.historical.map(d => d.fecha);
            const histData = result.historical.map(d => d.valor);

            const predLabels = result.prediction ? result.prediction.map(d => d.fecha) : [];
            const predData = result.prediction ? result.prediction.map(d => d.valor) : [];

            // Combine labels for X-axis
            const allLabels = [...histLabels, ...predLabels];

            // Prepare historical data with nulls for prediction range
            const histDataset = [...histData];
            for (let i = 0; i < predData.length; i++) histDataset.push(null);

            // Prepare prediction data with nulls for historical range
            // We want the prediction line to start from the last historical point
            const predictionDataset = new Array(Math.max(0, histData.length - 1)).fill(null);
            if (histData.length > 0) {
                predictionDataset.push(histData[histData.length - 1]); // Connect last hist to first pred
            }
            predData.forEach(v => predictionDataset.push(v));

            predictionChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: allLabels,
                    datasets: [
                        {
                            label: 'Ingresos Históricos',
                            data: histDataset,
                            borderColor: '#325ff3',
                            backgroundColor: 'rgba(50, 95, 243, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.3,
                            pointRadius: 2,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'Predicción 7 Días',
                            data: predictionDataset,
                            borderColor: '#d4af37',
                            backgroundColor: 'rgba(212, 175, 55, 0.1)',
                            borderWidth: 3,
                            borderDash: [5, 5],
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                            pointBackgroundColor: '#d4af37',
                            pointHoverRadius: 7
                        }
                    ]
                },
                options: {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#0f172a',
                                callback: (value) => '$' + value.toLocaleString()
                            },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        },
                        x: {
                            ticks: {
                                color: '#0f172a',
                                maxRotation: 45,
                                minRotation: 45,
                                autoSkip: true,
                                maxTicksLimit: 15
                            },
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#0f172a', usePointStyle: true }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    let label = context.dataset.label || '';
                                    if (label) label += ': ';
                                    if (context.parsed.y !== null) {
                                        label += '$' + context.parsed.y.toLocaleString();
                                    }
                                    return label;
                                }
                            }
                        },
                        datalabels: {
                            display: false // Too many points for datalabels
                        }
                    }
                }
            });

            // Update Summary
            const summaryDiv = document.getElementById('predictionSummary');
            if (summaryDiv) {
                summaryDiv.style.display = 'block';

                const peak = Math.max(...histData);
                const dip = Math.min(...histData);
                const avg = histData.reduce((a, b) => a + b, 0) / histData.length;

                const peakIndex = histData.indexOf(peak);
                const dipIndex = histData.indexOf(dip);

                const peakDate = peakIndex !== -1 ? result.historical[peakIndex].fecha : 'N/A';
                const dipDate = dipIndex !== -1 ? result.historical[dipIndex].fecha : 'N/A';

                let trendIcon = '➡️';
                let trendText = 'estable';
                let trendColor = '#94a3b8';

                if (result.trend === 'up') {
                    trendIcon = '📈';
                    trendText = 'ALCISTA';
                    trendColor = '#34d399';
                } else if (result.trend === 'down') {
                    trendIcon = '📉';
                    trendText = 'BAJISTA';
                    trendColor = '#f87171';
                }

                summaryDiv.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div>
                            <p style="color: #94a3b8; margin-bottom: 0.2rem;">Tendencia:</p>
                            <p style="color: ${trendColor}; font-weight: bold;">${trendIcon} ${trendText}</p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin-bottom: 0.2rem;">Pico (Máximo):</p>
                            <p style="color: #63ecf1;">$${peak.toLocaleString()} <span style="font-size: 0.75rem; color: #64748b;">(${peakDate})</span></p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin-bottom: 0.2rem;">Caída (Mínimo):</p>
                            <p style="color: #f87171;">$${dip.toLocaleString()} <span style="font-size: 0.75rem; color: #64748b;">(${dipDate})</span></p>
                        </div>
                        <div>
                            <p style="color: #94a3b8; margin-bottom: 0.2rem;">Promedio Diario:</p>
                            <p style="color: #cbd5e1;">$${Math.round(avg).toLocaleString()}</p>
                        </div>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading prediction:', error);
    }
}


async function loadRevenueHeatmap() {
    const sede = getCurrentSede();
    try {
        const response = await fetch(`/api/revenue-patterns?sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            // Update Inference Text
            const inferenceDiv = document.getElementById('revenueInference');
            if (inferenceDiv) {
                inferenceDiv.textContent = result.inference;
            }

            // Prepare Chart Data
            const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            const dataValues = days.map(day => result.patterns[day] || 0);

            // Calculate colors based on value (Heatmap effect)
            const maxVal = Math.max(...dataValues, 1);
            const colors = dataValues.map(val => {
                // Opacity from 0.2 to 1.0 based on relative value
                const alpha = 0.2 + (val / maxVal) * 0.8;
                return `rgba(16, 185, 129, ${alpha})`; // Emerald green
            });

            const ctx = document.getElementById('revenueHeatmapChart').getContext('2d');
            if (revenueHeatmapChart) revenueHeatmapChart.destroy();

            revenueHeatmapChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: days,
                    datasets: [
                        {
                            label: 'Ingreso Promedio Semanal',
                            data: dataValues,
                            backgroundColor: colors,
                            borderColor: '#059669',
                            borderWidth: 1,
                            borderRadius: 6,
                            borderSkipped: false,
                            barPercentage: 0.9,
                            categoryPercentage: 0.9
                        },
                        {
                            label: 'Sombra',
                            data: dataValues.map(v => v * 0.15),
                            backgroundColor: 'rgba(0, 0, 0, 0.2)',
                            borderColor: 'transparent',
                            borderWidth: 0,
                            borderRadius: 6,
                            borderSkipped: false,
                            barPercentage: 0.9,
                            categoryPercentage: 0.9
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#0f172a',
                                callback: (value) => '$' + value.toLocaleString()
                            },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        },
                        x: {
                            ticks: { color: '#0f172a' },
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => `Promedio: $${context.parsed.y.toLocaleString()}`
                            }
                        },
                        datalabels: {
                            color: '#0f172a',
                            anchor: 'end',
                            align: 'top',
                            formatter: (val) => {
                                if (val === 0) return '';
                                // Shorten large numbers
                                if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
                                if (val >= 1000) return '$' + (val / 1000).toFixed(0) + 'k';
                                return '$' + val;
                            },
                            font: { weight: 'bold', size: 10 }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading revenue heatmap:', error);
    }
}




async function loadServiceDemand() {
    const sede = getCurrentSede();
    try {
        const response = await fetch(`/api/service-demand?sede=${sede}`);

        // Handle no 200 OK
        if (!response.ok) {
            console.error('Service demand API error:', response.status);
            const div = document.getElementById('growthInference');
            if (div) {
                div.style.display = 'block';
                div.innerHTML = 'Error en la API de demanda de servicios. Código: ' + response.status;
            }
            return;
        }

        const result = await response.json();

        if (result.status === 'success') {
            const ctx = document.getElementById('serviceDemandChart').getContext('2d');
            if (serviceDemandChart) serviceDemandChart.destroy();

            const historical = result.historical || [];
            const prediction = result.prediction || [];

            if (historical.length === 0) {
                const div = document.getElementById('growthInference');
                if (div) {
                    div.style.display = 'block';
                    div.innerHTML = 'No hay datos suficientes para mostrar la demanda de servicios. Verifica que haya servicios registrados en los últimos 60 días para la sede seleccionada.';
                }
                return;
            }

            // Prepare labels
            const labels = [...historical.map(d => d.fecha), ...prediction.map(d => d.fecha)];

            // Service Types
            const types = ['Corte', 'Tintura', 'Uñas', 'Depilación'];
            const colors = {
                'Corte': '#3b82f6',     // Blue
                'Tintura': '#ec4899',   // Pink
                'Uñas': '#8b5cf6',      // Purple
                'Depilación': '#f97316' // Orange
            };

            const datasets = types.map(type => {
                // Historical Data
                const histData = historical.map(d => d[type] || 0);
                // Prediction Data
                const predData = prediction.map(d => d[type] || 0);

                // Complete Data array with nulls to spacing if needed, but here we just concat
                // Actually for stacked bar, we should concat values.
                const allData = [...histData, ...predData];

                // Background Colors: Solid for historical, Transparent/Border for prediction
                const bgColors = allData.map((_, i) => {
                    return i < histData.length ? colors[type] : `${colors[type]}80`; // 50% opacity for prediction
                });

                const borderColors = allData.map((_, i) => {
                    return i < histData.length ? colors[type] : '#fff'; // White border for prediction to distinguish
                });

                const borderWidths = allData.map((_, i) => {
                    return i < histData.length ? 0 : 2; // Border for prediction
                });

                return {
                    label: type,
                    data: allData,
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: borderWidths,
                    stack: 'Stack 0'
                };
            });

            serviceDemandChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            stacked: true,
                            ticks: { color: '#0f172a', maxTicksLimit: 15 },
                            grid: { display: false }
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true,
                            ticks: { color: '#0f172a', stepSize: 1 },
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#0f172a' } },
                        tooltip: {
                            callbacks: {
                                title: (context) => {
                                    const index = context[0].dataIndex;
                                    const label = context[0].label;
                                    return index >= historical.length ? `${label} (Predicción)` : label;
                                }
                            }
                        },
                        datalabels: { display: false } // Too crowded
                    }
                }
            });

            // Update Inference Box
            const growthDiv = document.getElementById('growthInference');
            if (growthDiv) {
                if (result.growthService) {
                    growthDiv.style.display = 'block';
                    growthDiv.innerHTML = `
                        <p style="color: #cbd5e1; margin-bottom: 0.5rem; font-weight: bold;">💡 Análisis de Tendencia</p>
                        <p style="color: #93c5fd;">
                            Se proyecta que el servicio de <span style="font-weight: bold; color: #fff; font-size: 1.1em;">${result.growthService}</span> tendrá el mayor crecimiento en la demanda durante la próxima semana.
                        </p>
                    `;
                } else {
                    growthDiv.style.display = 'none';
                }
            }

        }
    } catch (error) {
        console.error('Error loading service demand:', error);
        const div = document.getElementById('growthInference');
        if (div) {
            div.style.display = 'block';
            div.innerHTML = 'Error al cargar la demanda de servicios. Revisa la consola para más detalles.';
        }
    }
}

// Auto-fill product details on sale
document.addEventListener('DOMContentLoaded', () => {
    const saleProductoInput = document.getElementById('saleProducto');
    if (saleProductoInput) {
        saleProductoInput.addEventListener('input', function () {
            const val = this.value;
            if (currentInventory.length > 0) {
                const item = currentInventory.find(i => i.Producto === val);
                if (item) {
                    const marcaInput = document.getElementById('saleMarca');
                    const descInput = document.getElementById('saleDescripcion');
                    if (marcaInput) marcaInput.value = item.Marca || '';
                    if (descInput) descInput.value = item.Descripcion || '';

                    // Also try to fill price if empty
                    const priceInput = document.querySelector('#productForm input[name="valor"]');
                    if (priceInput && !priceInput.value && item.Valor) {
                        priceInput.value = item.Valor;
                    }
                }
            }
        });
    }

    // Check alerts on load
    checkAlerts();
    loadAppointments();

    // Auto-fill price on service selection
    const serviceSelect = document.querySelector('select[name="servicio"]');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function () {
            const selectedOption = this.options[this.selectedIndex];
            const price = selectedOption.getAttribute('data-price');
            const priceInput = document.querySelector('input[name="valor"]');

            if (price && priceInput) {
                priceInput.value = price;
            }
        });
    }

    // Restore last selected sede from localStorage
    const savedSede = localStorage.getItem('currentSede');
    const sedeSelector = document.getElementById('sedeSelector');
    if (savedSede && sedeSelector) {
        sedeSelector.value = savedSede;
    }
});

async function loadAppointments() {
    const dateInput = document.getElementById('agendaDate');
    if (!dateInput.value) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    const selectedDate = dateInput.value;
    const sede = getCurrentSede();

    try {
        const response = await fetch(`/api/appointments?date=${selectedDate}&sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            const tbody = document.getElementById('appointmentsBody');
            tbody.innerHTML = '';

            if (result.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No hay citas para este día</td></tr>';
                return;
            }

            result.data.forEach(item => {
                const row = document.createElement('tr');
                // Store item data in dataset for easy access
                row.dataset.id = item.ID;
                row.dataset.fecha = item.Fecha;
                row.dataset.hora = item.Hora;
                row.dataset.cliente = item.Cliente;
                row.dataset.telefono = item.Telefono;
                row.dataset.servicio = item.Servicio;
                row.dataset.notas = item.Notas || '';

                row.innerHTML = `
                    <td>${item.Hora}</td>
                    <td>${item.Cliente}</td>
                    <td>${item.Telefono}</td>
                    <td>${item.Servicio}</td>
                    <td>${item.Notas || ''}</td>
                    <td>
                        <button class="submit-btn" style="padding: 4px 8px; font-size: 0.8rem; margin-right: 5px;" onclick="editAppointment(this)">Editar</button>
                        <button class="delete-btn" style="padding: 4px 8px; font-size: 0.8rem;" onclick="deleteAppointment('${item.ID}')">Eliminar</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al cargar citas', true);
    }
}

let isEditing = false;
let currentEditId = null;

function editAppointment(btn) {
    const row = btn.closest('tr');
    const data = row.dataset;

    const form = document.getElementById('appointmentForm');
    form.querySelector('[name="fecha"]').value = data.fecha;
    form.querySelector('[name="hora"]').value = data.hora;
    form.querySelector('[name="cliente"]').value = data.cliente;
    form.querySelector('[name="telefono"]').value = data.telefono;
    form.querySelector('[name="servicio"]').value = data.servicio;
    form.querySelector('[name="notas"]').value = data.notas;

    // Change UI to Edit Mode
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Actualizar Cita';
    submitBtn.style.background = 'linear-gradient(to right, #f59e0b, #d97706)';

    // Add Cancel button if not exists
    if (!document.getElementById('cancelEditBtn')) {
        const cancelBtn = document.createElement('button');
        cancelBtn.id = 'cancelEditBtn';
        cancelBtn.type = 'button';
        cancelBtn.textContent = 'Cancelar';
        cancelBtn.className = 'delete-btn';
        cancelBtn.style.marginTop = '10px';
        cancelBtn.style.width = '100%';
        cancelBtn.onclick = resetAppointmentForm;
        form.appendChild(cancelBtn);
    }

    isEditing = true;
    currentEditId = data.id;
}

function resetAppointmentForm() {
    const form = document.getElementById('appointmentForm');
    form.reset();

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.textContent = 'Agendar Cita';
    submitBtn.style.background = ''; // Reset to default

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) cancelBtn.remove();

    isEditing = false;
    currentEditId = null;
}

async function deleteAppointment(id) {
    if (!confirm('¿Está seguro de eliminar esta cita?')) return;

    try {
        const response = await fetch(`/api/appointment/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            loadAppointments();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al eliminar cita', true);
    }
}

async function checkAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const result = await response.json();

        if (result.status === 'success' && result.alerts.length > 0) {
            result.alerts.forEach(alert => {
                showNotification(alert.message);
            });
        }
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

// Sede Management Handlers
async function addSedeHandler(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/sede', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            form.reset();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

async function deleteSede(name) {
    if (!confirm(`¿Estás seguro de eliminar la sede ${name}?`)) return;

    try {
        const response = await fetch('/api/sede', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    // Fix: Include current sede in the data
    data.sede = getCurrentSede();

    try {
        let url = '/api/appointment';
        let method = 'POST';

        if (isEditing && currentEditId) {
            url = `/api/appointment/${currentEditId}`;
            method = 'PUT';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            resetAppointmentForm();
            loadAppointments();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
});

// User Management
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const result = await response.json();

        if (result.status === 'success') {
            const list = document.getElementById('usersList');
            list.innerHTML = '';
            result.data.forEach(username => {
                const li = document.createElement('li');
                li.className = 'stylist-item';
                li.innerHTML = `
                    <span>${username}</span>
                    <button class="delete-btn" onclick="deleteUser('${username}')">Eliminar</button>
                `;
                list.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function addUserHandler(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            form.reset();
            loadUsers();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

async function deleteUser(username) {
    if (!confirm(`¿Estás seguro de eliminar el usuario ${username}?`)) return;

    try {
        const response = await fetch('/api/users', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            loadUsers();
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

async function loadMonthlyExpenses() {
    try {
        const monthInput = document.getElementById('monthlyExpensesMonth');
        if (!monthInput.value) {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            monthInput.value = `${year}-${month}`;
        }

        const mes = monthInput.value;
        const sede = getCurrentSede();

        const response = await fetch(`/api/monthly-expenses?mes=${mes}&sede=${sede}`);
        const result = await response.json();

        if (result.status === 'success') {
            const form = document.getElementById('monthlyExpensesForm');
            form.reset();

            // Map known types to input names
            const typeToName = {
                'Arriendo Local': 'arriendo',
                'Servicio de Agua': 'agua',
                'Servicio de Electricidad (Codensa)': 'electricidad',
                'Servicio de Internet y TV (Claro)': 'internet',
                'Cuota Banco (Davivienda)': 'banco',
                'Contrato Monica': 'monica'
            };

            result.data.forEach(item => {
                const name = typeToName[item.Tipo];
                if (name) {
                    const input = form.querySelector(`[name="${name}"]`);
                    if (input) input.value = item.Valor;
                }
            });
        }
    } catch (error) {
        console.error('Error loading monthly expenses:', error);
        showNotification('Error al cargar gastos mensuales', true);
    }
}

async function saveMonthlyExpenses(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const monthInput = document.getElementById('monthlyExpensesMonth');

    const nameToType = {
        'arriendo': 'Arriendo Local',
        'agua': 'Servicio de Agua',
        'electricidad': 'Servicio de Electricidad (Codensa)',
        'internet': 'Servicio de Internet y TV (Claro)',
        'banco': 'Cuota Banco (Davivienda)',
        'monica': 'Contrato Monica'
    };

    const expenses = [];
    for (const [name, val] of formData.entries()) {
        if (val) {
            expenses.push({
                tipo: nameToType[name],
                valor: val
            });
        }
    }

    if (expenses.length === 0) {
        showNotification('Ingrese al menos un valor', true);
        return;
    }

    const data = {
        sede: getCurrentSede(),
        mes: monthInput.value,
        expenses: expenses
    };

    try {
        const response = await fetch('/api/monthly-expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}

// Inline Editing Functions
function enableEdit(btn, sheet, id, valor, comision) {
    const row = btn.closest('tr');
    const valorCell = row.cells[2];
    const comisionCell = row.cells[3];
    const actionCell = row.cells[5];

    // Store original values
    valorCell.dataset.original = valor;
    comisionCell.dataset.original = comision;
    actionCell.dataset.originalHTML = actionCell.innerHTML;

    valorCell.innerHTML = `<input type="number" class="edit-input" value="${valor}" step="0.01" style="width: 80px; padding: 4px; border-radius: 4px; border: 1px solid #ccc; color: #000;">`;
    comisionCell.innerHTML = `<input type="number" class="edit-input" value="${comision}" step="0.01" style="width: 80px; padding: 4px; border-radius: 4px; border: 1px solid #ccc; color: #000;">`;

    actionCell.innerHTML = `
        <button class="save-btn" onclick="saveEdit(this, '${sheet}', ${id})" style="background:none; border:none; cursor:pointer; margin-right: 5px;" title="Guardar">💾</button>
        <button class="cancel-btn" onclick="cancelEdit(this)" style="background:none; border:none; cursor:pointer;" title="Cancelar">❌</button>
    `;
}

function cancelEdit(btn) {
    const row = btn.closest('tr');
    const valorCell = row.cells[2];
    const comisionCell = row.cells[3];
    const actionCell = row.cells[5];

    valorCell.innerHTML = `$${parseFloat(valorCell.dataset.original).toLocaleString()}`;
    comisionCell.innerHTML = `$${parseFloat(comisionCell.dataset.original).toLocaleString()}`;
    actionCell.innerHTML = actionCell.dataset.originalHTML;
}

async function saveEdit(btn, sheet, id) {
    const row = btn.closest('tr');
    const valorInput = row.cells[2].querySelector('input');
    const comisionInput = row.cells[3].querySelector('input');

    const newValor = valorInput.value;
    const newComision = comisionInput.value;

    try {
        const response = await fetch('/api/summary/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sheet: sheet,
                id: id,
                valor: newValor,
                comision: newComision
            }),
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message);
            loadSummary(); // Reload to update totals
        } else {
            showNotification(result.message, true);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexión', true);
    }
}
