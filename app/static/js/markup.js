class DataLabeler {
    constructor(buttonIds, resultsContainerId) {
      this.labeledData = [];
      this.currentIndex = 0;
      this.currentResolve = null;
      
      // Элементы интерфейса
      this.resultsContainer = document.getElementById(resultsContainerId);
      this.resultsBody = document.getElementById('results-body');
      this.messageContainer = document.getElementById('currentMessage');
      
      // Инициализация кнопок
      buttonIds.forEach(id => {
        const btn = document.getElementById(id);
        btn.addEventListener('click', () => this.handleLabelSelect(id));
      });
    }
  
    handleLabelSelect(buttonId) {
      if (this.currentResolve) {
        const label = buttonId.replace('btn', '');
        this.currentResolve(label);
        this.currentResolve = null;
      }
    }
  
    async processData(data) {
        // Показываем контейнер с результатами
        this.originalData = data;
        this.resultsContainer.classList.remove('hidden');

        // Получаем или создаем контейнер для сообщения
        let messageContainer = document.getElementById('currentMessage');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'currentMessage';
            messageContainer.className = 'mb-4 p-4 bg-gray-100 rounded-lg border border-blue-200';
            messageContainer.style.minHeight = '100px';
            this.resultsContainer.parentNode.insertBefore(messageContainer, this.resultsContainer);
        }

        // Очищаем предыдущие данные
        this.labeledData = [];
        this.resultsBody.innerHTML = '';

        for (const item of data) {
            // Показываем текущее сообщение
            messageContainer.textContent = item.MessageText;

            // Ждем выбора лейбла
            const label = await new Promise(resolve => {
                this.currentResolve = resolve;
            });

            // Добавляем данные
            this.labeledData.push({
                text: item.MessageText,
                label: label,
            });

            // Обновляем таблицу
            this.addTableRow(item.MessageText, label);
        }

        // Показываем финальный результат
        this.showFinalResult();
    }

    addTableRow(text, label) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="border border-gray-300 px-4 py-2 break-all whitespace-normal">${text}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${label}</td>
        `;
        this.resultsBody.appendChild(row);
    }
    
    showFinalResult() {
        // Проверяем, существует ли уже кнопка
        // let downloadBtn = this.resultsContainer.querySelector('.download-btn');
        const downloadBtn = document.getElementById('btnDownload');
        // Если кнопка не существует, создаем ее
        // downloadBtn
        // if (!downloadBtn) {
            // downloadBtn = document.createElement('button');
            // downloadBtn.className = 'download-btn mb-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600';
            // downloadBtn.textContent = 'Скачать XLSX';
            downloadBtn.classList.remove('disabled');
            downloadBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
            downloadBtn.classList.add('bg-blue-500', 'hover:bg-blue-600');
            
            downloadBtn.onclick = () => {
                const data = this.prepareOutputData();
                this.exportToExcel(data);
            };

            // Вставляем кнопку перед таблицей
            // const tableContainer = this.resultsContainer.querySelector('.max-w-full');
            // this.resultsContainer.insertBefore(downloadBtn, tableContainer);
        // }
    }

    exportToExcel(data) {
        // Создаем рабочую книгу
        const workbook = XLSX.utils.book_new();
        
        // Преобразуем данные в лист Excel
        const worksheet = XLSX.utils.json_to_sheet(data, {
            header: this.getExcelHeaders(data),
            skipHeader: false
        });
        
        // Добавляем лист в книгу
        XLSX.utils.book_append_sheet(workbook, worksheet, "Разметка");
        
        // Генерируем файл
        XLSX.writeFile(workbook, 'labeled-data.xlsx', {
            bookType: 'xlsx',
            type: 'buffer'
        });
    }

    getExcelHeaders(data) {
        if (data.length === 0) return [];
        const firstItem = data[0];
        return Object.keys(firstItem);
    }

    prepareOutputData() {
        return this.originalData.map((item, index) => ({
            ...item,
            label: this.labeledData[index].label
        }));
    }

    // convertToCSV() {
    //     const escapeField = (field) => {
    //         if (typeof field !== 'string') return field;
    //         return `"${field.replace(/"/g, '""')}"`;
    //     };

    //     const header = ['Текст', 'Лейбл', 'Уверенность'].join(',');
    //     const rows = this.labeledData.map(item => {
    //         return [
    //             escapeField(item.text),
    //             escapeField(item.label),
    //             item.confidence ? `${(item.confidence * 100).toFixed(2)}%` : ''
    //         ].join(',');
    //     });

    //     return [header, ...rows].join('\n');
    // }
  }
  

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const messageContainer = document.getElementById('currentMessage');
    if (messageContainer) messageContainer.textContent = '';

    const fileInput = document.getElementById('file-input');
    if (!fileInput.files.length) {
        alert("Выберите файл перед загрузкой!");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/kek/", {
        method: "POST",
        body: formData
    });
    console.log(response)
    if (!response.ok) {
        alert("Ошибка при загрузке файла");
        return;
    }

    const result = await response.json();

    // const textBlock = document.createElement('div');
    // // Добавляем текст
    // textBlock.textContent = 'Это динамически созданный блок с текстом.';
    
    // // Добавляем стили с помощью JavaScript
    // textBlock.style.border = '1px solid #ccc';
    // textBlock.style.padding = '20px';
    // textBlock.style.margin = '10px';
    // textBlock.style.backgroundColor = '#f9f9f9';
    // textBlock.style.borderRadius = '5px';
    
    // // Добавляем блок на страницу
    // document.getElementsByClassName("bg-white shadow-md rounded-lg p-6")[0].appendChild(textBlock);

    // Отображаем таблицу с результатами
    const tableBody = document.getElementById('results-body');
    tableBody.innerHTML = "";
    const labeler = new DataLabeler(
        ['btnA', 'btnB', 'btnC'],
        'jsonOutput'
      );
    // processRows(result)
    // for (const row of result.data) {
    // //     // const tr = document.createElement("tr");
    // //     // tr.innerHTML = `
    // //     //     <td class="border border-gray-300 px-4 py-2">${row.MessageText}</td>
    // //     //     <td class="border border-gray-300 px-4 py-2">${row.label}</td>
    // //     //     <td class="border border-gray-300 px-4 py-2">${(row.confidence * 100).toFixed(2)}%</td>
    // //     // `;
    // //     // tableBody.appendChild(tr);
    // //     // console.log('huy')
    // //     // Ждем нажатия кнопки перед переходом к следующей строке
    // //     textBlock.textContent = row.MessageText;
    // //     await waitForButtonClick('wait-button');
    //     textBlock.textContent = row.MessageText;

    //     // Ждем нажатия любой из кнопок
    //     const clickedButtonId = await waitForAnyButtonClick();
    //     console.log('Нажата кнопка:', clickedButtonId);
        
    // }
    labeler.processData(result.data);
    // document.getElementById('results-container').classList.remove('hidden');

    // Активируем кнопку скачивания
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.href = result.download_url;
    downloadBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
    downloadBtn.classList.add('bg-blue-500', 'hover:bg-blue-600');
    downloadBtn.removeAttribute('disabled');
});