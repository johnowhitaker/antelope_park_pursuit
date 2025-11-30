let allTasks = [];
let completedTaskIds = JSON.parse(localStorage.getItem('completedTaskIds')) || [];
let incompleteOnly = false;

async function loadTasks() {
    try {
        const res = await fetch('data/tasks.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('Failed to load tasks');
        allTasks = await res.json();
    } catch (e) {
        console.error('Error loading tasks:', e);
        allTasks = [];
    }
    preloadImages(allTasks);
    renderTasks();
}

function preloadImages(tasks) {
    tasks.forEach(task => {
        if (task.photoURL) {
            const img = new Image();
            img.src = task.photoURL;
        }
    });
}

function renderTasks() {
    const taskList = document.getElementById('task-list');
    const filtered = incompleteOnly ? allTasks.filter(t => !completedTaskIds.includes(t.id)) : allTasks;
    const categories = [...new Set(filtered.map(task => task.category))].filter(Boolean);
    taskList.innerHTML = '';

    categories.forEach(category => {
        const details = document.createElement('details');
        details.innerHTML = `<summary>${category}</summary>`;
        const tasksInCategory = filtered.filter(task => task.category === category);

        tasksInCategory.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = 'card';
            taskDiv.id = `task-${task.id}`;
            if (completedTaskIds.includes(task.id)) taskDiv.classList.add('completed');
            taskDiv.innerHTML = `
                ${task.photoURL ? `<img src="${task.photoURL}" alt="${task.name}">` : ''}
                <div class="task-info">
                    <h3>${task.name}</h3>
                    ${task.description ? `<p>${task.description}</p>` : ''}
                </div>
                <div class="points-badge">${task.points || 0} pts</div>
                <span class="checkmark">✅</span>
            `;
            taskDiv.addEventListener('click', () => toggleTask(task.id));
            details.appendChild(taskDiv);
        });

        taskList.appendChild(details);
    });

    updateScore();
}

function toggleTask(taskId) {
    if (completedTaskIds.includes(taskId)) {
        completedTaskIds = completedTaskIds.filter(id => id !== taskId);
    } else {
        completedTaskIds.push(taskId);
    }
    localStorage.setItem('completedTaskIds', JSON.stringify(completedTaskIds));
    const taskDiv = document.getElementById(`task-${taskId}`);
    if (taskDiv) taskDiv.classList.toggle('completed');
    updateScore();
}

function updateScore() {
    const score = allTasks.reduce((acc, task) => {
        return acc + (completedTaskIds.includes(task.id) ? (task.points || 0) : 0);
    }, 0);
    document.getElementById('score').textContent = `Your Score: ${score}`;
}

function setupControls() {
    const cb = document.getElementById('incomplete-only');
    if (cb) {
        cb.checked = incompleteOnly;
        cb.addEventListener('change', () => {
            incompleteOnly = cb.checked;
            renderTasks();
        });
    }
    const resetBtn = document.getElementById('reset-progress');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Reset all progress?')) {
                completedTaskIds = [];
                localStorage.removeItem('completedTaskIds');
                renderTasks();
            }
        });
    }
}

setupControls();
loadTasks();
