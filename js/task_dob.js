 
function formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getDate().toString().padStart(2, '0')}.${(date.getMonth() + 1).toString().padStart(2, '0')}.${date.getFullYear()}`;
}
const currentDate = new Date();
const formattedDate = formatDate(currentDate);

document.getElementById('creationDate').innerText = formattedDate;


function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
 
const urlParams = new URLSearchParams(window.location.search);

document.addEventListener('DOMContentLoaded', async function () {
    const taskId = urlParams.get('task_id');

    if (taskId) {
        try {
            const token = getCookie('access_token');
            if (!token) {
                console.error('Токен не найден, пользователь не аутентифицирован');
                return;
            }

            const response = await fetch(`/tasks/${taskId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
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
            console.error('Ошибка при получении задачи:', error);
        }
    } else {//если новая задача
        document.getElementById('creationDate').innerText = '';
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
    const token = getCookie('access_token');
    if (!token) {
        console.error('Токен не найден, пользователь не аутентифицирован');
        return;
    }

    const taskId = parseInt(urlParams.get('task_id')); 

    const heading = document.getElementById('heading').value;
    const task_text = document.getElementById('textarea').value;
    const prize = document.getElementById('prize').value;
    const important = document.getElementById('importantCheckbox').checked;
    const completed = document.getElementById('completedCheckbox').checked;
    const data_stop = document.getElementById('completionDate').value;

    const taskData = {
        task_id: taskId, 
        heading,
        task_text,
        prize,
        important,
        completed,
        data_stop
    };

    try {
        const response = await fetch('/create_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Задача успешно сохранена:', result);
            window.location.href = `/html/storage.html`;
        } else {
            console.error('Ошибка при сохранении задачи:', response.statusText);
        }
    } catch (error) {
        console.error('Ошибка при сохранении задачи:', error);
    }
}