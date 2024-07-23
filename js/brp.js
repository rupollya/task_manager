function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

async function deleteTask(task_id) {
    const token = getCookie('access_token');

    if (!token) {
        console.error('Token not found, user is not authenticated');
        return;
    }

    try {
        console.log(`Sending request to delete task with ID ${task_id}`);
        const response = await fetch(`/tasks/${task_id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
        });

        console.log(`Server response status: ${response.status}`);
        if (response.ok) {
            console.log(`Task with ID ${task_id} successfully deleted from server.`);
            const deletedTaskElement = document.querySelector(`.task[data-task-id="${task_id}"]`);
            if (deletedTaskElement) {
                deletedTaskElement.remove();
                console.log(`Task element with ID ${task_id} successfully removed from DOM`);
            } else {
                console.error(`Task element with ID ${task_id} not found in DOM`);
            }
        } else {
            console.error('Error deleting task:', response.statusText);
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}
 
async function loadTaskById(taskId) {
    const token = getCookie('access_token');

    if (!token) {
        console.error('Токен не найден, пользователь не аутентифицирован');
        return;
    }

    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
        });

        if (response.ok) {
            const task = await response.json(); 

            var section3 = document.querySelector('.section3');
            var taskDetails = document.createElement('div');
            taskDetails.innerHTML = `
                <h3 class="heading_3">${task.heading}</h3>
                <p class="date_3">Дата создания: ${formatDate(task.created_at)}</p>
                <p class="date_3">Завершить до: ${formatDate(task.data_stop)}</p>
                <textarea class="textarea_3" readonly>${task.task_text}</textarea>
                <p class="prize_text">Награда за выполнение</p>
                <textarea class="textarea_3_1" readonly>${task.prize}</textarea>
            `;
            section3.innerHTML = ''; // чистим секцию 3
            section3.appendChild(taskDetails);
        } else {
            const error = await response.json();
            console.error('Ошибка при получении задачи:', error.error);
        }
    } catch (error) {
        console.error('Ошибка при получении задачи:', error);
    }
}

 