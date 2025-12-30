const API_URL = "http://localhost:8004/api";

async function loadBoard() {
    const res = await fetch(`${API_URL}/board`);
    const data = await res.json();
    
    const globalCols = data.cols;
    const tasks = data.tasks;

    const boardDiv = document.getElementById('board');
    boardDiv.innerHTML = '';

    globalCols.forEach(col => {

        const colDiv = document.createElement('div');
        colDiv.className = 'column';
        colDiv.dataset.colId = col.id;
        colDiv.innerHTML = `
            <h2>${col.name}</h2>
            <div class="task-list" id="col-${col.id}"></div>
            <div class="add-form">
                <input type="text" placeholder="..." id="input-${col.id}">
                <button onclick="addTask(${col.id})">+</button>
            </div>
        `;

        // EVENTY DLA KOLUMN (DROP ZONE)
        colDiv.addEventListener('dragover', handleDragOver);
        colDiv.addEventListener('dragleave', handleDragLeave);
        colDiv.addEventListener('drop', (e) => handleDrop(e, col.id));

        boardDiv.appendChild(colDiv);
    });

    tasks.forEach(task => {
        const colList = document.getElementById(`col-${task.col_id}`);
        if (colList) {
            const taskDiv = document.createElement('div');
            taskDiv.className = 'task-card';
            taskDiv.draggable = true;
            taskDiv.innerText = task.title;
            taskDiv.dataset.taskId = task.id; 

            taskDiv.addEventListener('dragstart', handleDragStart);
            taskDiv.addEventListener('dragend', handleDragEnd);

            colList.appendChild(taskDiv);
        }
    });
}

// LOGIKA DRAG & DROP

let draggedTaskId = null; // Zmienna globalna przechowująca ID przenoszonego zadania

function handleDragStart(e) {
    draggedTaskId = this.dataset.taskId;
    this.classList.add('dragging');

    setTimeout(() => (this.style.display = "none"), 0);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    this.style.display = "block";
    draggedTaskId = null;
    
    document.querySelectorAll('.column').forEach(col => col.classList.remove('drag-over'));
}

function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('drag-over'); 
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

async function handleDrop(e, targetColId) {
    e.preventDefault();
    
    const colElement = e.currentTarget;
    colElement.classList.remove('drag-over'); 

    if (!draggedTaskId) return;

    // Wywołanie API, żeby przenieść zadanie
    // Ustawienie ord na 9999, żeby wpadło na koniec listy
    try {
        await fetch(`${API_URL}/tasks/${draggedTaskId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ col_id: targetColId, ord: 9999 })
        });
        
        loadBoard(); 
    } catch (err) {
        console.error("Błąd podczas przenoszenia:", err);
    }
}

async function addTask(colId) {
    const input = document.getElementById(`input-${colId}`);
    if (!input.value) return;

    await fetch(`${API_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: input.value, col_id: colId })
    });
    
    loadBoard();
}

loadBoard();