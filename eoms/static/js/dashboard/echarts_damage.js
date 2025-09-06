// Initiate echarts instance and load data
var damageChart = echarts.init(document.getElementById('damage'));


// Load Damage Data
function loadDamageData() {
    fetch('/api/maintenance_records')
    .then(response => response.json())
    .then(data => {
        const months = data.map(item => item.month);
        const services = data.map(item => item.number_of_services);

        var option = {
            tooltip: {},
            xAxis: {
                data: months
            },
            yAxis: {},
            series: [{
                name: 'Services',
                type: 'line',
                data: services
            }]
        };
        damageChart.setOption(option);
    });
}

loadDamageData();

// Resize chart when window is resized
window.addEventListener('resize', function() {
    damageChart.resize();
});


// ---------- JS for Table ----------
document.addEventListener('DOMContentLoaded', function() {
    // Function to sort data by month
    function sortDataByMonth(data) {
        return data.sort((a, b) => {
            const monthA = a.month.split('-');
            const monthB = b.month.split('-');
            const dateA = new Date(monthA[0], monthA[1] - 1);
            const dateB = new Date(monthB[0], monthB[1] - 1);
            return dateA - dateB;
        });
    }

    // Fetch and display maintenance data
    fetch('/api/maintenance_records')
    .then(response => response.json())
    .then(data => {
        const sortedData = sortDataByMonth(data);
        let table = document.getElementById('damage_table');
        let tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        sortedData.forEach(row => {
            let tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.month}</td><td>${row.number_of_services}</td>`;
            tbody.appendChild(tr);
        });
    });
});
