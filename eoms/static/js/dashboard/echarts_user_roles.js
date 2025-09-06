// Initialize the echarts instance
var userRolesChart = echarts.init(document.getElementById('userRoles'));


// Pie chart for user roles distribution
function loadUserRolesData() {
    fetch('/api/user_roles_distribution')
    .then(response => response.json())
    .then(data => {
        var option = {
            tooltip: {
                trigger: 'item'
            },
            legend: {
                orient: 'vertical',
                left: 'left'
            },
            series: [
                {
                    name: 'User Role',
                    type: 'pie',
                    radius: '50%',
                    data: data.map(item => ({
                        value: item.count,
                        name: item.role
                    })),
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };
        userRolesChart.setOption(option);
    });
}

loadUserRolesData();

// Resize the chart when the window resizes
window.addEventListener('resize', function() {
    userRolesChart.resize();
});


// Table version of the user roles distribution
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate the User Roles table
    fetch('/api/user_roles_distribution')
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('userRoles_table');
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(item => {
            const row = `<tr><td>${item.role}</td><td>${item.count}</td></tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    });
});