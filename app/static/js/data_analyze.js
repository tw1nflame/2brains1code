document.getElementById('file-input').addEventListener('change', async function(event){
    event.preventDefault();
    const fileInputLabel = document.querySelector('label[for="file-input"]');
    const fileInput = document.getElementById('file-input');
    fileInputLabel.textContent = fileInput.files[0].name;
});

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('upload-form').addEventListener('submit', async function(event) {
        event.preventDefault();  // Останавливаем стандартное поведение формы

        const fileInput = document.getElementById('file-input');
        if (!fileInput.files.length) {
            alert("Выберите файл перед загрузкой!");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const loadingIndicator = document.getElementById('loading-indicator');
        loadingIndicator.classList.remove('hidden'); // Показываем индикатор загрузки

        try {
            const response = await fetch("/upload/", {
                method: "POST",
                body: formData
            });

            loadingIndicator.classList.add('hidden'); // Скрываем индикатор

            if (!response.ok) {
                alert("Ошибка при загрузке файла");
                return;
            }

            const result = await response.json();

            // Отображаем таблицу с результатами
            const tableBody = document.getElementById('results-body');
            tableBody.innerHTML = "";
            result.data.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="border border-gray-300 px-4 py-2">${row.text}</td>
                    <td class="border border-gray-300 px-4 py-2">${row.label}</td>
                    <td class="border border-gray-300 px-4 py-2">${(row.confidence * 100).toFixed(2)}%</td>
                `;
                tableBody.appendChild(tr);
            });

            document.getElementById('results-container').classList.remove('hidden');

            // Активируем кнопку скачивания
            const downloadBtn = document.getElementById('download-btn');
            downloadBtn.href = result.download_url;
            downloadBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
            downloadBtn.classList.add('bg-blue-500', 'hover:bg-blue-600');
            downloadBtn.removeAttribute('disabled');
        } catch (error) {
            console.error("Ошибка запроса:", error);
            alert("Произошла ошибка при загрузке файла");
            loadingIndicator.classList.add('hidden'); // Скрываем индикатор при ошибке
        }
    });
});
