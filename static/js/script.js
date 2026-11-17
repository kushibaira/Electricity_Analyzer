
const chartElement = document.getElementById("consumptionChart");

if (chartElement) {
    new Chart(chartElement, {
        type: "line",

        data: {
            labels: [
                "Jan 1", "Jan 2", "Jan 3",
                "Jan 4", "Jan 5", "Jan 6",
                "Jan 7", "Jan 8", "Jan 9",
                "Jan 10", "Jan 11", "Jan 12",
                "Jan 13", "Jan 14", "Jan 15"
            ],

            datasets: [{
                label: "Electricity Consumption (kWh)",

                data: [
                    12.5, 14.2, 16.8, 10.5, 12.1,
                    17.3, 13.8, 19.5, 15.6, 11.2,
                    12.8, 14.5, 20.1, 17.9, 12.4
                ],

                borderWidth: 3,
                tension: 0.3,
                fill: false
            }]
        },

        options: {
            responsive: true,

            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: "Consumption (kWh)"
                    }
                }
            }
        }
    });
}
