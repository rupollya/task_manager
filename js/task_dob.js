document.addEventListener('DOMContentLoaded', function () {
    function formatDate(dateString) {
        const date = new Date(dateString);
        const options = {
            weekday: 'long',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        };
        const formatter = new Intl.DateTimeFormat('ru-RU', options);
        return formatter.format(date);
    }

    function getCurrentDate() {
        const date = new Date();
        const options = {
            weekday: 'short',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
        };
        const formatter = new Intl.DateTimeFormat('ru-RU', options);
        return formatter.format(date);
    }

    document.querySelectorAll('.date-text').forEach(element => {
        const originalText = element.textContent;
        const dateMatch = originalText.match(/Дата создания: (.+)/) || originalText.match(/Срок: (.+)/);

        if (dateMatch) {
            const formattedDate = formatDate(dateMatch[1]);
            element.textContent = originalText.replace(dateMatch[1], formattedDate);
        } else {
            // Если нет даты, вставляем текущее время
            const currentDate = getCurrentDate();
            element.textContent = `Дата создания: ${currentDate}`;
        }
    });
});
const urlParams = new URLSearchParams(window.location.search);
document.addEventListener('DOMContentLoaded', async function () {
    const taskId = urlParams.get('task_id');

    if (taskId) {
        // Редактирование задачи
        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'GET'
            });

            if (response.ok) {
                const task = await response.json();
                document.getElementById('creationDate').innerText = formatDate(task.created_at);
                document.getElementById('completionDate').value = task.data_stop ? task.data_stop.split('T')[0] : '';
                document.getElementById('importantCheckbox').checked = task.important || false;
                document.getElementById('completedCheckbox').checked = task.completed || false;
                document.getElementById('prize').value = task.prize || '';
                document.getElementById('task_id').value = task.task_id || '';
                document.getElementById('heading').value = task.heading || '';
                document.getElementById('textarea').value = task.task_text || '';
            } else {
                console.error('Ошибка при получении задачи:', response.statusText);
            }
        } catch (error) {
             
        }
    } 
    else {
        // Создание новой задачи
        document.getElementById('creationDate').innerText = formatDate(new Date());
        document.getElementById('completionDate').value = '';
        document.getElementById('importantCheckbox').checked = false;
        document.getElementById('completedCheckbox').checked = false;
        document.getElementById('prize').value = '';
        document.getElementById('task_id').value = '';
        document.getElementById('heading').value = '';
        document.getElementById('textarea').value = '';
    }
});
 
 
async function saveTask() {
    const taskId = parseInt(urlParams.get('task_id')); 
    const heading = document.getElementById('heading').value;
    const task_text = document.getElementById('textarea').value;
    const prize = document.getElementById('prize').value;
    const important = document.getElementById('importantCheckbox').checked;
    const completed = document.getElementById('completedCheckbox').checked;
    const data_stop = document.getElementById('completionDate').value;

    console.log({ taskId, heading, task_text, prize, important, completed, data_stop });

    const taskData = {
        task_id: taskId ? parseInt(taskId) : null,
        heading,
        task_text,
        prize,
        important,
        completed,
        data_stop
    };

    try {
        const method = 'POST';
        const url = `/task_dob.html`;

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            console.log('Задача успешно сохранена');
            window.location.href = '/storage.html';
        } else {
            console.error('Ошибка при сохранении задачи:', response.statusText);
        }
    } catch (error) {
        console.error('Ошибка при сохранении задачи:', error);
    }
}
 