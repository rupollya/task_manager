document.addEventListener('DOMContentLoaded', function () {
    var tasksContainer = document.getElementById('tasksContainer');

    tasksContainer.querySelectorAll('.delete-task-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
            var taskId = this.dataset.taskId;
            console.log(`Кнопка удаления задачи с ID ${taskId} была жмякнута`);
            deleteTask(taskId);
        });
    });

    tasksContainer.querySelectorAll('.redak-task-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
            var taskId = this.getAttribute('redak-task-id');
            console.log(`Кнопка редактирования задачи с ID ${taskId} была жмякнута`);
            window.location.href = `/task_dob.html?task_id=${taskId}`;
        });
    });

    function deleteTask(taskId) {
        fetch(`/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${document.cookie.split('=')[1]}`,
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error(`Ошибка при удалении задачи с ID ${taskId}`);
            }
        }).catch(error => {
            console.error(`Ошибка при удалении задачи с ID ${taskId}:`, error);
        });
    }
});

async function deleteTask(task_id) {
    const token = getCookie('access_token');
    try {
        console.log(`Sending request to delete task with ID ${task_id}`);
        const response = await fetch(`/tasks/${task_id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
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



document.addEventListener('DOMContentLoaded', function () {
    const taskButtons = document.querySelectorAll('.selected-task-btn');
    const taskDetails = document.querySelectorAll('.task-detail');

    taskButtons.forEach(button => {
        button.addEventListener('click', function () {
            const selectedTaskId = this.closest('.task').dataset.taskId;

            //скрываем детали задачи
            taskDetails.forEach(detail => {
                detail.classList.remove('active');
            });

             //и показываем только нужную
            const selectedTaskDetail = Array.from(taskDetails).find(detail => detail.dataset.taskId === selectedTaskId);
            if (selectedTaskDetail) {
                selectedTaskDetail.classList.add('active');
            }
        });
    });
});
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

    document.querySelectorAll('.date-text').forEach(element => {
        const originalText = element.textContent;
        const dateMatch = originalText.match(/Дата создания: (.+)/) || originalText.match(/Срок: (.+)/);

        if (dateMatch) {
            const formattedDate = formatDate(dateMatch[1]);
            element.textContent = originalText.replace(dateMatch[1], formattedDate);
        }
    });
});
//ПОИСК
document.addEventListener('DOMContentLoaded', function () {
    var searchForm = document.getElementById('searchForm');
    var searchInput = document.getElementById('searchInput');

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        var task = searchInput.value.trim().toLowerCase();  

        filterTasks(task);
    });

    function filterTasks(task) {
        var tasks = document.querySelectorAll('.task'); 
        tasks.forEach(function (taskElement) {
            var heading = taskElement.querySelector('.task_section2').textContent.toLowerCase();  
            if (heading.includes(task)) {
                taskElement.style.display = 'block';
            } else {
                taskElement.style.display = 'none';
            }
        });
    }
});





