const API_URL = "http://localhost:8002/api";


async function loadPublicView() {
    const container = document.getElementById('posts-container');
    const res = await fetch(`${API_URL}/posts`);
    const posts = await res.json();

    container.innerHTML = '';
    
    for (const post of posts) {
        const commRes = await fetch(`${API_URL}/posts/${post.id}/comments`);
        const comments = await commRes.json();

        let commentsHtml = comments.map(c => `
            <div class="comment">
                <div class="comment-author">${c.author}:</div>
                <div>${c.body}</div>
            </div>
        `).join('');

        if (comments.length === 0) commentsHtml = '<small>Brak komentarzy.</small>';

        container.innerHTML += `
            <div class="post">
                <div class="post-title">${post.title}</div>
                <div class="post-body">${post.body}</div>
                
                <div class="comments-section">
                    <h3>Komentarze:</h3>
                    <div id="comments-list-${post.id}">
                        ${commentsHtml}
                    </div>
                    
                    <div style="margin-top:10px; border-top:1px solid #eee; padding-top:10px;">
                        <strong>Dodaj komentarz:</strong>
                        <input id="author-${post.id}" placeholder="Twój nick">
                        <textarea id="body-${post.id}" placeholder="Treść..." rows="2"></textarea>
                        <button onclick="addComment(${post.id})">Wyślij</button>
                    </div>
                </div>
            </div>
        `;
    }
}

async function addComment(postId) {
    const authorInput = document.getElementById(`author-${postId}`);
    const bodyInput = document.getElementById(`body-${postId}`);

    const author = authorInput.value;
    const body = bodyInput.value;

    if(!author || !body) return alert("Wypełnij oba pola!");

    try {
        const res = await fetch(`${API_URL}/posts/${postId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author, body })
        });

        // Obsługa błędów (Anty-spam)
        if (!res.ok) {
            const errorData = await res.json();
            alert("Błąd: " + (errorData.detail || "Nie udało się dodać komentarza."));
            return;
        }

        // Sukces
        alert("Komentarz wysłany do moderacji! Pojawi się po zatwierdzeniu.");
        authorInput.value = '';
        bodyInput.value = '';

    } catch (err) {
        console.error(err);
        alert("Błąd połączenia z serwerem.");
    }
}

// LOGIKA ADMINA

async function loadAdminView() {
    const container = document.getElementById('pending-container');
    const res = await fetch(`${API_URL}/comments/pending`);
    const comments = await res.json();

    container.innerHTML = '';

    if (comments.length === 0) {
        container.innerHTML = '<p>Brak komentarzy do moderacji.</p>';
        return;
    }

    comments.forEach(c => {
        container.innerHTML += `
            <div class="pending-row">
                <div>
                    <strong>Post ID: ${c.post_id} | Autor: ${c.author}</strong><br>
                    ${c.body}
                </div>
                <div class="actions">
                    <button class="btn-approve" onclick="approveComment(${c.id})">Zatwierdź</button>
                    <button class="btn-reject" onclick="rejectComment(${c.id})">Odrzuć</button>
                </div>
            </div>
        `;
    });
}

async function approveComment(commentId) {
    await fetch(`${API_URL}/comments/${commentId}/approve`, { method: 'POST' });
    loadAdminView(); 
}

async function rejectComment(commentId) {
    if (!confirm("Czy na pewno chcesz trwale usunąć ten komentarz?")) return;

    await fetch(`${API_URL}/comments/${commentId}`, { method: 'DELETE' });
    loadAdminView();
}

async function createNewPost() {
    const titleInput = document.getElementById('new-title');
    const bodyInput = document.getElementById('new-body');
    
    const title = titleInput.value;
    const body = bodyInput.value;

    if (!title || !body) {
        alert("Podaj tytuł i treść!");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, body })
        });

        if (res.ok) {
            alert("Post został opublikowany!");
            titleInput.value = '';
            bodyInput.value = '';
        } else {
            alert("Błąd serwera.");
        }
    } catch (err) {
        console.error(err);
        alert("Błąd połączenia.");
    }
}