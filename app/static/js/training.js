const form = document.getElementById("train-form");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const etaText = document.getElementById("eta-text");
const trainingStatus = document.getElementById("training-status");
const metricsChartContainer = document.getElementById("metrics-chart-container");
let taskId = null;
let activeCharts = {};
let selectedMetrics = [];

document.getElementById('file-input').addEventListener('change', async function(event){
    event.preventDefault();
    const fileInputLabel = document.querySelector('label[for="file-input"]');
    const fileInput = document.getElementById('file-input');
    fileInputLabel.textContent = fileInput.files[0].name;
});


const metricMapping = {
    accuracy: 'eval_accuracy',
    f1: 'eval_f1',
    recall: 'eval_recall'
};

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const batchSize = document.getElementById("batch_size").value;
    const epochs = document.getElementById("n_epochs").value;
    const testSize = document.getElementById("test_size").value;
    selectedMetrics = Array.from(document.getElementById("metrics").selectedOptions).map(opt => opt.value);
    const fileInput = document.getElementById("file-input");
    
    if (!fileInput.files.length) {
        alert("Выберите файл для загрузки.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("batch_size", batchSize);
    formData.append("n_epochs", epochs);
    formData.append("test_size", testSize);

    // Преобразуем метрики для бэкенда
    selectedMetrics.forEach(metric => {
        formData.append("metrics", metric);
    });

    try {
        const response = await axios.post("/start-training", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        taskId = response.data.task_id;
        trainingStatus.classList.remove("hidden");
        initializeCharts();
        monitorTraining(taskId);
    } catch (error) {
        if (error.response && error.response.status === 400) {
            alert("Модель уже обучается.");
        }
        else{
            console.error("Ошибка при отправке данных:", error);
        }
    }
});

async function monitorTraining(taskId) {
    const interval = setInterval(async () => {
        try {
            const response = await axios.get(`/training-status/${taskId}`);
            const { status, progress, eta, metrics } = response.data;
            console.log(response.data)

            progressBar.value = progress * 100;
            progressText.textContent = `Прогресс: ${Math.round(progress * 100)}%`;
            etaText.textContent = `Оставшееся время: ${eta ? Math.round(eta) + " сек" : "--"}`;

            if (metrics) {
                const step = metrics.step || 0;

                selectedMetrics.forEach(frontendMetric => {
                    const backendMetric = metricMapping[frontendMetric];
                    if (metrics[backendMetric] !== undefined && activeCharts[backendMetric]) {
                        updateChartData(activeCharts[backendMetric], step, metrics[backendMetric]);
                    }
                });

                if (metrics.loss !== undefined && activeCharts.loss) {
                    updateChartData(activeCharts.loss, step, metrics.loss);
                }
                if (metrics.eval_loss !== undefined && activeCharts.eval_loss) {
                    updateChartData(activeCharts.eval_loss, step, metrics.eval_loss);
                }
            }

            if (status === "completed" || status === "failed") {
                clearInterval(interval);
            }
        } catch (error) {
            console.error("Ошибка при отправке данных:", error);
        }
    }, 5000);
}

function initializeCharts() {
    metricsChartContainer.innerHTML = "";
    activeCharts = {};
    metricsChartContainer.className = "grid grid-cols-2 gap-4 mt-4";

    selectedMetrics.forEach(frontendMetric => {
        const backendMetric = metricMapping[frontendMetric];
        createChart(backendMetric);
    });

    createChart('loss');
    createChart('eval_loss');

    metricsChartContainer.classList.remove("hidden");
}

function createChart(metric) {
    const chartContainer = document.createElement("div");
    chartContainer.className = "h-48 bg-white p-2 rounded-lg shadow-sm";
    metricsChartContainer.appendChild(chartContainer);

    const canvas = document.createElement("canvas");
    chartContainer.appendChild(canvas);

    const ctx = canvas.getContext("2d");
    const chartConfig = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: metric.replace('eval_', '').replace(/\b\w/g, l => l.toUpperCase()),
                data: [],
                borderColor: getColorByMetric(metric),
                backgroundColor: getColorByMetric(metric),
                borderWidth: 2,
                pointRadius: 4,
                pointStyle: 'circle',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        font: { size: 10 }
                    }
                }
            },
            scales: {
                x: {
                    title: { 
                        display: true, 
                        text: 'Step',
                        font: { size: 10 }
                    },
                    ticks: { font: { size: 8 } }
                },
                y: {
                    title: { 
                        display: true,
                        text: metric === 'loss' ? 'Training Loss' : 
                              metric === 'eval_loss' ? 'Validation Loss' : metric.replace('eval_', ''),
                        font: { size: 10 }
                    },
                    ticks: { font: { size: 8 } },
                    min: metric.includes('loss') ? undefined : 0,
                    max: metric.includes('loss') ? undefined : 1
                }
            }
        }
    };

    activeCharts[metric] = new Chart(ctx, chartConfig);
}

function getColorByMetric(metric) {
    switch (metric) {
        case 'loss': return 'rgba(255, 159, 64, 1)';
        case 'eval_loss': return 'rgba(153, 102, 255, 1)';
        case 'eval_accuracy': return 'rgba(54, 162, 235, 1)';
        case 'eval_f1': return 'rgba(75, 192, 192, 1)';
        case 'eval_recall': return 'rgba(255, 99, 132, 1)';
        default: return 'rgba(100, 100, 100, 1)';
    }
}

// Остальные функции без изменений
function updateChartData(chart, step, value) {
    const labels = chart.data.labels;
    const data = chart.data.datasets[0].data;

    const index = labels.indexOf(step);
    if (index !== -1) {
        data[index] = value;
    } else {
        labels.push(step);
        data.push(value);
    }

    chart.update();
}