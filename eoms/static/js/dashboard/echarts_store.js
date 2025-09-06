// Scatter plot

var storeDistributionChart = echarts.init(document.getElementById('store'));

function loadStoreDistributionData() {
    fetch('/api/store_distribution')
    .then(response => response.json())
    .then(data => {
        var transformedData = data.map((item, index) => {
            return {
                name: item.city,
                value: [index, item.store_count, item.store_count] // x position (index), y position (store count), size (store count)
            };
        });

        var option = {
            backgroundColor: {
                type: 'radial',
                x: 0.3,
                y: 0.3,
                r: 0.8,
                colorStops: [{
                    offset: 0,
                    color: '#f7f8fa'
                }, {
                    offset: 1,
                    color: '#cdd0d5'
                }]
            },
            tooltip: {
                trigger: 'item',
                formatter: function (params) {
                    return params.name + ': ' + params.value[1] + ' stores';
                }
            },
            xAxis: {
                type: 'value',
                splitLine: {
                    show: false
                }
            },
            yAxis: {
                type: 'value',
                splitLine: {
                    show: false
                },
                scale: true
            },
            series: [{
                name: 'Store Count',
                type: 'scatter',
                data: transformedData,
                symbolSize: function (data) {
                    return Math.sqrt(data[2]) * 20; // Dynamically size symbols based on store count
                },
                label: {
                    show: true,
                    formatter: function (param) {
                        return param.name;
                    },
                    position: 'top'
                },
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(120, 36, 50, 0.5)',
                    shadowOffsetY: 5,
                    color: {
                        type: 'radial',
                        x: 0.4,
                        y: 0.3,
                        r: 1,
                        colorStops: [{
                            offset: 0,
                            color: 'rgb(251, 118, 123)'
                        }, {
                            offset: 1,
                            color: 'rgb(204, 46, 72)'
                        }]
                    }
                }
            }]
        };

        storeDistributionChart.setOption(option);
    }).catch(error => console.error('Error loading store distribution data:', error));
}

loadStoreDistributionData();

// Resize chart on window resize
window.addEventListener('resize', function() {
    storeDistributionChart.resize();
});


// Populate the store distribution table
document.addEventListener('DOMContentLoaded', function() {
    // Fetch and populate the store distribution table
    fetch('/api/store_distribution')
    .then(response => response.json())
    .then(data => {
        const table = document.getElementById('store_table');
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = ''; // Clear existing rows
        data.forEach(item => {
            const row = `<tr><td>${item.city}</td><td>${item.store_count}</td></tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    });
});