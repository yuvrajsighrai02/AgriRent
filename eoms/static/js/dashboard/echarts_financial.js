// Initiate echarts instance and load data
var financialChart = echarts.init(document.getElementById('financial'));


// Load Financial Data
function loadFinancialData() {
    fetch('/api/financial_report')
    .then(response => response.json())
    .then(data => {
        const months = data.map(item => item.month);
        const revenues = data.map(item => item.total_revenue);

        var option = {
            tooltip: {},
            xAxis: {
                data: months
            },
            yAxis: {},
            series: [{
                name: 'Revenue',
                type: 'bar',
                data: revenues
            }]
        };
        financialChart.setOption(option);
    });
}

loadFinancialData();

// Resize chart when window is resized
window.addEventListener('resize', function() {
    financialChart.resize();
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

    // Fetch Financial Data and Populate Table
    fetch('/api/financial_report')
    .then(response => response.json())
    .then(data => {
        let table = document.getElementById('financial_table');
        let tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(row => {
            let tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.month}</td><td>${row.total_revenue}</td>`;
            tbody.appendChild(tr);
        });
    });
});