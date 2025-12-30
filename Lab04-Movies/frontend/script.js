const API_URL = "http://localhost:8003/api";

async function loadMovies() {
    try {
        const res = await fetch(`${API_URL}/movies`);
        const movies = await res.json();
        
        const list = document.getElementById('moviesList');
        list.innerHTML = '';

        movies.forEach((movie, index) => {
            const rank = index + 1;
            
            let rankClass = '';
            if(rank <= 3) rankClass = `rank-${rank}`;

            list.innerHTML += `
                <div class="movie-card ${rankClass}">
                    <div class="movie-info">
                        <span class="rank-badge">#${rank}</span>
                        <h2>${movie.title}</h2>
                        <span>Rok produkcji: ${movie.year}</span>
                    </div>

                    <div class="right-section">
                        <div class="movie-stats">
                            <span class="score">${movie.avg_score.toFixed(2)}</span>
                            <span class="votes">Głosów: ${movie.votes}</span>
                        </div>
                        
                        <div class="vote-actions">
                            <button class="vote-btn" onclick="rateMovie(${movie.id}, 1)">1</button>
                            <button class="vote-btn" onclick="rateMovie(${movie.id}, 2)">2</button>
                            <button class="vote-btn" onclick="rateMovie(${movie.id}, 3)">3</button>
                            <button class="vote-btn" onclick="rateMovie(${movie.id}, 4)">4</button>
                            <button class="vote-btn" onclick="rateMovie(${movie.id}, 5)">5</button>
                        </div>
                    </div>
                </div>
            `;
        });

    } catch (err) {
        showError("Nie udało się pobrać danych z API.");
        console.error(err);
    }
}

async function addMovie() {
    const title = document.getElementById('newTitle').value;
    const year = document.getElementById('newYear').value;

    if(!title || !year) return showError("Wypełnij tytuł i rok!");

    try {
        const res = await fetch(`${API_URL}/movies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, year: parseInt(year) })
        });

        if(res.ok) {
            document.getElementById('newTitle').value = '';
            document.getElementById('newYear').value = '';
            loadMovies();
        } else {
            showError("Błąd przy dodawaniu filmu.");
        }
    } catch (err) {
        showError("Błąd sieci.");
    }
}

async function rateMovie(movieId, score) {
    try {
        const res = await fetch(`${API_URL}/ratings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                movie_id: movieId, 
                score: score 
            })
        });

        if(res.ok) {
 
            loadMovies();
        } else {
            showError("Błąd głosowania.");
        }
    } catch (err) {
        showError("Nie można połączyć z serwerem.");
    }
}

function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

loadMovies();