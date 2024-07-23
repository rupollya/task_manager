function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = new Date(dateString).toLocaleDateString('ru-RU', options);
    return formattedDate;
}



function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

document.addEventListener('DOMContentLoaded', function () {
    var urlParams = new URLSearchParams(window.location.search);
    var category = urlParams.get('category');
    const token = getCookie('access_token');

    if (!token) {
        console.error('Токен не найден, пользователь не аутентифицирован');
        return;
    }

    if (category === 'all_tasks') {
        loadAllTasks();
    } else if (category === 'today_tasks') {
        loadTodayTasks();
    } else if (category === 'important_tasks') {
        loadImportantTasks();
    } else if (category === 'completed_tasks') {
        loadCompletedTasks();
    } else {
        loadAllTasks();
    }

    function loadAllTasks() {
        fetchTasks('/tasks', 'Все задачи');
    }

    function loadTodayTasks() {
        fetchTasks('/tasks_today', 'Сегодня');
    }

    function loadImportantTasks() {
        fetchTasks('/tasks_important', 'Важное');
    }

    function loadCompletedTasks() {
        fetchTasks('/tasks_completed', 'Завершенное');
    }

    async function fetchTasks(url, categoryName) {
        try {
            var response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            var tasks = await response.json();

            var tasksContainer = document.getElementById('tasksContainer');
            tasksContainer.innerHTML = '';
            tasks.forEach(function (task) {
                var taskElement = createTaskElement(task);
                tasksContainer.appendChild(taskElement);
            });

            var select = document.getElementById('select');
            select.textContent = categoryName;
            var section2 = document.querySelector('.section2');
            section2.style.display = 'block';

        } catch (error) {
            console.error(`Ошибка при получении задач (${categoryName}):`, error);
        }
    }

    function createTaskElement(task) {
        var taskElement = document.createElement('div');
        taskElement.classList.add('task');
        taskElement.dataset.taskId = task.task_id;

        var formattedDate = formatDate(task.created_at);
        taskElement.innerHTML = `
            <div class="d-flex justify-content-between" id="box"> 
                <div class="d-flex">
                    <img src="/images/love.png" width="45" height="45">
                    <h3 class="task_section2 selected-task-btn" style="cursor:pointer;">${task.heading}</h3>
                </div>
                <div class="d-flex">
                    <img src="/images/redak.png" width="35" height="35" redak-task-id="${task.task_id}" class="redak-task-btn" style="margin-right:8px;cursor: pointer;">
                    <img src="/images/bin.png" width="35" height="35" data-task-id="${task.task_id}" class="delete-task-btn" style="cursor:pointer;">
                </div>
            </div>
        `;

        var selectedButton = taskElement.querySelector('.selected-task-btn');
        selectedButton.addEventListener('click', function (event) {
            event.stopPropagation();
            var taskId = task.task_id;
            console.log(`Кнопка показа задачи с ID ${taskId} была жмякнута`);
            loadTaskById(taskId);
        });

        var deleteButton = taskElement.querySelector('.delete-task-btn');
        deleteButton.addEventListener('click', function (event) {
            event.stopPropagation();
            var taskId = task.task_id;
            console.log(`Кнопка удаления задачи с ID ${taskId} была жмякнута`);
            deleteTask(taskId);
        });

        var redakButton = taskElement.querySelector('.redak-task-btn');
        redakButton.addEventListener('click', function (event) {
            event.stopPropagation();
            var taskId = task.task_id;
            console.log(`Кнопка редактирования задачи с ID ${taskId} была жмякнута`);
            window.location.href = `/html/task_dob.html?task_id=${taskId}`;
        });


        return taskElement;
    }
});











//ПОИСК
document.addEventListener('DOMContentLoaded', function() {
    var searchForm = document.getElementById('searchForm');
    var searchInput = document.getElementById('searchInput');

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var task = searchInput.value.trim().toLowerCase(); // исправлено на trim()

        filterTasks(task);
    });

    function filterTasks(task) {
        var tasks = document.querySelectorAll('.task'); // исправлено на querySelectorAll
        tasks.forEach(function(taskElement) {
            var heading = taskElement.querySelector('.task_section2').textContent.toLowerCase(); // исправлено на querySelector
            if (heading.includes(task)) {
                taskElement.style.display = 'block';
            } else {
                taskElement.style.display = 'none';
            }
        });
    }
});