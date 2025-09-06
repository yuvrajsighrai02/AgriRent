// Helper function to sort data by months
function sortDataByMonth(data) {
    return data.sort((a, b) => new Date(a.month) - new Date(b.month));
}

// Financial Chart
function loadFinancialData() {
    fetch('/api/financial_report')
    .then(response => response.json())
    .then(data => {
        data = sortDataByMonth(data);
        const months = data.map(item => item.month);
        const revenues = data.map(item => item.total_revenue);

        var option = {
            title: {
                text: 'Financial Report'
            },
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

// Hire Chart
function loadHireData() {
    fetch('/api/hire_status')
    .then(response => response.json())
    .then(data => {
        data = sortDataByMonth(data);
        const months = data.map(item => item.month);
        const hires = data.map(item => item.number_of_hires);

        var option = {
            title: {
                text: 'Machine Hire Status'
            },
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

// Damage Chart
function loadDamageData() {
    fetch('/api/maintenance_records')
    .then(response => response.json())
    .then(data => {
        data = sortDataByMonth(data);
        const months = data.map(item => item.month);
        const services = data.map(item => item.number_of_services);

        var option = {
            title: {
                text: 'Maintenance Records'
            },
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
