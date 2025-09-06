// Initiate echarts instance and load data
var hireChart = echarts.init(document.getElementById('hire'));


// Load Hire Data
function loadHireData() {
    fetch('/api/hire_status')
    .then(response => response.json())
    .then(data => {
        const months = data.map(item => item.month);
        const hires = data.map(item => item.number_of_hires);

        var option = {
            tooltip: {},
            xAxis: {
                data: months
            },
            yAxis: {},
            series: [{
                name: 'Hires',
                type: 'line',
                data: hires,
                areaStyle: {}
            }]
        };
        hireChart.setOption(option);
    });
}

loadHireData();

// Resize chart when window is resized
window.addEventListener('resize', function() {
    hireChart.resize();
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

    // Fetch and display hire data
    fetch('/api/hire_status')
    .then(response => response.json())
    .then(data => {
        const sortedData = sortDataByMonth(data);
        let table = document.getElementById('hire_table');
        let tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        sortedData.forEach(row => {
            let tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.month}</td><td>${row.number_of_hires}</td>`;
            tbody.appendChild(tr);
        });
    });
});