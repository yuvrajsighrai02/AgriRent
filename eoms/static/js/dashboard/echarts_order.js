// Radar chart with two separate radar indicators

var customerOrdersChart = echarts.init(document.getElementById('order'));

function loadCustomerOrdersData() {
    fetch('/api/customer_orders')
    .then(response => response.json())
    .then(data => {
        // Extract data and define maximum scales
        var maxOrderCount = Math.max(...data.map(item => item.order_count));
        var maxTotalSpent = Math.max(...data.map(item => item.total_spent));

        // Set up two separate sets of indicators for each type of data
        var orderIndicators = data.map(item => ({
            name: item.customer_name,
            max: maxOrderCount * 1.1 // 10% padding for visual comfort
        }));

        var spentIndicators = data.map(item => ({
            name: item.customer_name,
            max: maxTotalSpent * 1.1 // 10% padding for visual comfort
        }));

        var option = {
            color: ['#FFE434', '#65FFA4'],
            // title: {
            //     text: 'Customer Orders and Spending by Radar',
            //     left: 'center',
            //     textStyle: {
            //         color: '#333'
            //     }
            // },
            tooltip: {
                trigger: 'item'
            },
            legend: {
                data: ['Order Count', 'Total Spent'],
                left: 'right'
            },
            radar: [{
                indicator: orderIndicators,
                center: ['25%', '50%'],
                radius: 120,
                shape: 'circle', // Set the shape of the radar to circle
                splitNumber: 5,
                axisName: {
                    color: '#fff',
                    backgroundColor: '#666',
                    borderRadius: 3,
                    padding: [3, 5]
                },
                splitArea: {
                    areaStyle: {
                        color: ['rgba(255, 195, 0, 0.1)', 'rgba(255, 152, 0, 0.2)', 'rgba(255, 87, 34, 0.4)', 'rgba(244, 67, 54, 0.6)', 'rgba(233, 30, 99, 0.8)'], // Background colors for a colorful display
                        shadowColor: 'rgba(0, 0, 0, 0.3)',
                        shadowBlur: 10
                    }
                },
                axisLine: {
                    lineStyle: {
                        color: 'rgba(255, 255, 255, 0.5)'
                    }
                }
            }, {
                indicator: spentIndicators,
                center: ['75%', '50%'],
                radius: 120,
                shape: 'circle',
                splitNumber: 5,
                axisName: {
                    color: '#fff',
                    backgroundColor: '#666',
                    borderRadius: 3,
                    padding: [3, 5]
                },
                splitArea: {
                    areaStyle: {
                        color: ['#77EADF', '#26C3BE', '#64AFE9', '#428BD4'], // Blue shades
                        shadowColor: 'rgba(0, 0, 0, 0.2)',
                        shadowBlur: 10
                    }
                },
                axisLine: {
                    lineStyle: {
                        color: 'rgba(211, 253, 250, 0.8)'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: 'rgba(211, 253, 250, 0.8)'
                    }
                }
            }],
            series: [{
                name: 'Orders',
                type: 'radar',
                radarIndex: 0,
                data: [{
                    value: data.map(item => item.order_count),
                    name: 'Order Count',
                    symbol: 'rectangle',
                    symbolSize: 10,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: function(params) {
                            return params.value;
                        }
                    },
                    areaStyle: {
                        color: 'rgba(255, 228, 52, 0.6)'
                    }
                }]
            }, {
                name: 'Spending',
                type: 'radar',
                radarIndex: 1,
                data: [{
                    value: data.map(item => item.total_spent),
                    name: 'Total Spent',
                    symbol: 'circle',
                    symbolSize: 10,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: function(params) {
                            return params.value;
                        }
                    },
                    areaStyle: {
                        color: 'rgba(101, 255, 164, 0.6)'
                    }
                }]
            }]
        };

        customerOrdersChart.setOption(option);
    }).catch(error => console.error('Error loading customer orders data:', error));
}

loadCustomerOrdersData();

// Resize the chart when the window resizes
window.addEventListener('resize', function() {
    customerOrdersChart.resize();
});


// Populate the order table
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate the order table
    fetch('/api/customer_orders')
    .then(response => response.json())
    .then(data => {
        console.log("Order Data Received:", data); // Debug statement
        const table = document.getElementById('order_table');
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(item => {
            const totalSpent = item.total_spent ? parseFloat(item.total_spent) : 0; // Ensure it is a number and handle null/undefined
            const row = `<tr><td>${item.customer_name}</td><td>${item.order_count}</td><td>${totalSpent.toFixed(2)}</td></tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    }).catch(error => {
        console.error("Error fetching order data:", error);
    });
});
