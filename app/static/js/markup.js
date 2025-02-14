function waitForButtonClick(buttonId) {
    return new Promise((resolve) => {
      const button = document.getElementById(buttonId);
      button.addEventListener('click', () => {
        resolve(); // Промис разрешится при нажатии на кнопку
      });
    });
}

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    

    const fileInput = document.getElementById('file-input');
    if (!fileInput.files.length) {
        alert("Выберите файл перед загрузкой!");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/upload/", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Ошибка при загрузке файла");
        return;
    }

    const result = await response.json();

    const textBlock = document.createElement('div');

    // Добавляем текст
    textBlock.textContent = 'Это динамически созданный блок с текстом.';
    
    // Добавляем стили с помощью JavaScript
    textBlock.style.border = '1px solid #ccc';
    textBlock.style.padding = '20px';
    textBlock.style.margin = '10px';
    textBlock.style.backgroundColor = '#f9f9f9';
    textBlock.style.borderRadius = '5px';
    
    // Добавляем блок на страницу
    document.body.appendChild(textBlock);

    // Отображаем таблицу с результатами
    const tableBody = document.getElementById('results-body');
    tableBody.innerHTML = "";
    for (const row of result.data) {
        // const tr = document.createElement("tr");
        // tr.innerHTML = `
        //     <td class="border border-gray-300 px-4 py-2">${row.MessageText}</td>
        //     <td class="border border-gray-300 px-4 py-2">${row.label}</td>
        //     <td class="border border-gray-300 px-4 py-2">${(row.confidence * 100).toFixed(2)}%</td>
        // `;
        // tableBody.appendChild(tr);
        // console.log('huy')
        // Ждем нажатия кнопки перед переходом к следующей строке
        textBlock.textContent = row.MessageText;
        await waitForButtonClick('wait-button');
        
    }

    document.getElementById('results-container').classList.remove('hidden');

    // Активируем кнопку скачивания
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.href = result.download_url;
    downloadBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
    downloadBtn.classList.add('bg-blue-500', 'hover:bg-blue-600');
    downloadBtn.removeAttribute('disabled');
});