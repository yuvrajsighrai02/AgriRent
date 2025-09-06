// Initialize the echarts instance
var inventoryChart = echarts.init(document.getElementById('stock'));

// Load the inventory data
function loadInventoryData() {
    fetch('/api/product_inventory')
    .then(response => response.json())
    .then(data => {
        const categories = data.map(item => item.category_name + ' - ' + item.product_name);
        const productCounts = data.map(item => item.product_count);
        const totalMachines = data.map(item => item.total_machines);

        var option = {
            tooltip: {},
            legend: {
                data: ['Product Count', 'Total Machines']
            },
            xAxis: {
                data: categories
            },
            yAxis: {},
            series: [
                {
                    name: 'Product Count',
                    type: 'bar',
                    data: productCounts
                },
                {
                    name: 'Total Machines',
                    type: 'bar',
                    data: totalMachines
                }
            ]
        };
        inventoryChart.setOption(option);
    });
}

loadInventoryData();

// Resize the chart when the window resizes
window.addEventListener('resize', function() {
    inventoryChart.resize();
});


// Populate the inventory table
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate the inventory table
    fetch('/api/product_inventory')
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('stock_table');
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(item => {
            const row = `<tr><td>${item.category_name} - ${item.product_name}</td><td>${item.product_count}</td><td>${item.total_machines}</td></tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    });
});
