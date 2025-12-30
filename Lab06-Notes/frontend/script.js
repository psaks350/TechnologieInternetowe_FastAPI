const API_URL = "http://localhost:8005/api";

// POBIERANIE (Z FILTROWANIEM)
async function loadNotes(query = "") {
    let url = `${API_URL}/notes`;
    if (query) {
        url += `?q=${encodeURIComponent(query)}`;
    }

    const res = await fetch(url);
    const notes = await res.json();
    
    const list = document.getElementById('notesList');
    list.innerHTML = '';

    if (notes.length === 0) {
        list.innerHTML = '<p style="text-align:center; color:#888">Brak wyników.</p>';
        return;
    }

    notes.forEach(note => {
        const tagsHtml = note.tags.map(t => `<span class="tag">#${t.name}</span>`).join('');
        
        const date = new Date(note.created_at).toLocaleDateString();

        list.innerHTML += `
            <div class="note-card">
                <div class="note-header">
                    <h2>${note.title}</h2>
                    <span class="note-date">${date}</span>
                </div>
                <div class="note-body">${note.body}</div>
                <div class="tags">${tagsHtml}</div>
            </div>
        `;
    });
}

// WYSZUKIWANIE
function searchNotes() {
    const query = document.getElementById('searchInput').value;
    loadNotes(query);
}

// DODAWANIE NOTATKI + TAGI
async function addNote() {
    const title = document.getElementById('newTitle').value;
    const body = document.getElementById('newBody').value;
    const tagsInput = document.getElementById('newTags').value;

    if (!title) return alert("Podaj tytuł!");

    const resNote = await fetch(`${API_URL}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, body })
    });
    
    if (resNote.ok) {
        const createdNote = await resNote.json();

        if (tagsInput.trim()) {
            const tagsArray = tagsInput.split(',').map(t => t.trim()).filter(t => t);
            
            await fetch(`${API_URL}/notes/${createdNote.id}/tags`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tags: tagsArray })
            });
        }

        document.getElementById('newTitle').value = '';
        document.getElementById('newBody').value = '';
        document.getElementById('newTags').value = '';
        searchNotes();
    }
}

loadNotes();