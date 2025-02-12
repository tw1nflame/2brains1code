async function analyzeSentiment() {
    const textInput = document.getElementById('textInput').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = "<p class='text-gray-500'>Анализируем...</p>";

    try {
        const response = await fetch('/api/sentiment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textInput }),
        });

        if (response.ok) {
            const data = await response.json();
            const sentiment = data.sentiment;
            const confidence = (data.confidence * 100).toFixed(2);

            let color;
            if (sentiment === 'Позитивный') color = 'text-green-600';
            else if (sentiment === 'Нейтральный') color = 'text-gray-600';
            else color = 'text-red-600';

            resultDiv.innerHTML = `
                <p class="text-xl font-semibold ${color}">${sentiment}</p>
                <p class="text-gray-600">Уверенность: ${confidence}%</p>
            `;
        } else {
            resultDiv.innerHTML = "<p class='text-red-600'>Ошибка при анализе</p>";
        }
    } catch (error) {
        resultDiv.innerHTML = "<p class='text-red-600'>Ошибка сети</p>";
    }
}