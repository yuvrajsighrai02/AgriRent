// Load user activity distribution data and render gauge chart

var userActivityChart = echarts.init(document.getElementById('userActivity'));

function loadUserActivityData() {
    fetch('/api/user_activity_distribution')
    .then(response => response.json())
    .then(data => {
        // Ensure data is found for both active and inactive users
        const activeUser = data.find(d => d.is_active === 1) || { count: 0 };
        const inactiveUser = data.find(d => d.is_active === 0) || { count: 0 };
        const totalUsers = activeUser.count + inactiveUser.count;
        const activePercentage = totalUsers > 0 ? (activeUser.count / totalUsers * 100).toFixed(2) : 0;

        var option = {
            tooltip: {
                formatter: '{a} <br/>{b} : {c}%'
            },
            series: [
                {
                    name: 'User Activity',
                    type: 'gauge',
                    progress: {
                        show: true
                    },
                    detail: {
                        valueAnimation: true,
                        formatter: '{value}%'
                    },
                    data: [
                        {
                            value: activePercentage,
                            name: 'Active Users'
                        }
                    ]
                }
            ]
        };
        userActivityChart.setOption(option);
    }).catch(error => console.error('Error loading user activity data:', error));
}

loadUserActivityData();

// Resize the chart when the window resizes
window.addEventListener('resize', function() {
    userActivityChart.resize();
});


// Table version of the user activity distribution
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate the User Activity table
    fetch('/api/user_activity_distribution')
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('userActivity_table');
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(item => {
            const activityStatus = item.is_active ? 'Active' : 'Inactive';
            const row = `<tr><td>${activityStatus}</td><td>${item.count}</td></tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    });
});