const API = "http://localhost:8000/api";

// === API HELPERS ===
async function req(endpoint, method="GET", body=null) {
    try {
        const opts = { method, headers: { 'Content-Type': 'application/json' } };
        if(body) opts.body = JSON.stringify(body);
        const res = await fetch(API + endpoint, opts);
        const data = await res.json();
        if(!res.ok) throw new Error(data.detail || "Błąd");
        return data;
    } catch(e) {
        msg(e.message, true);
        return null;
    }
}

function msg(text, isError=false) {
    const el = document.getElementById('message');
    el.textContent = text;
    el.className = isError ? 'error' : 'success';
    setTimeout(() => el.textContent = '', 3000);
}

// === GŁÓWNA LOGIKA ===
async function loadAll() {
    const [members, books, loans] = await Promise.all([
        req('/members'), req('/books'), req('/loans')
    ]);

    const mList = document.getElementById('membersList');
    mList.innerHTML = '';
    members?.forEach(m => {
        mList.innerHTML += `
            <div class="row">
                <span>${m.name} (${m.email})</span>
                <small>ID: ${m.id}</small>
            </div>`;
    });

    // 1. Dropdown Czytelników
    const sel = document.getElementById('memberSelect');
    const savedVal = sel.value;
    sel.innerHTML = '<option value="">-- Wybierz Osobę --</option>';
    members?.forEach(m => sel.innerHTML += `<option value="${m.id}">${m.name}</option>`);
    sel.value = savedVal;

    // 2. Lista Książek (z przyciskiem Wypożycz)
    const bList = document.getElementById('booksList');
    bList.innerHTML = '';
    books?.forEach(b => {
        const avail = b.available_copies > 0;
        bList.innerHTML += `
            <div class="row">
                <span><b>${b.title}</b> (${b.author}) - Dostępne: ${b.available_copies}/${b.copies}</span>
                <button onclick="borrow(${b.id})" ${!avail ? 'disabled' : ''}>Wypożycz</button>
            </div>`;
    });

    // 3. Lista Wypożyczeń (z przyciskiem Zwróć)
    const lList = document.getElementById('loansList');
    lList.innerHTML = '';
    // Pokaż tylko aktywne (bez daty zwrotu)
    const activeLoans = loans?.filter(l => l.return_date === null) || [];
    
    if(activeLoans.length === 0) lList.innerHTML = 'Brak aktywnych wypożyczeń.';
    
    activeLoans.forEach(l => {
        lList.innerHTML += `
            <div class="row">
                <span>${l.book.title} (użytkownik: ${l.member.name})</span>
                <button onclick="returnBook(${l.id})">Zwróć</button>
            </div>`;
    });

    // 4. Wszystkie Wypożyczenia
    const aList = document.getElementById('allLoansList');
    aList.innerHTML = '';
    loans?.forEach(l => {
        aList.innerHTML += `
            <div class="row">
                <span>${l.book.title} (użytkownik: ${l.member.name}) - Wypożyczono: ${new Date(l.loan_date).toLocaleDateString()} 
                ${l.return_date ? `- Zwrócono: ${new Date(l.return_date).toLocaleDateString()}` : '- Nie zwrócono'}</span>
            </div>`;
    });
}

// === AKCJE ===
async function addMember(e) {
    e.preventDefault();
    const res = await req('/members', 'POST', {
        name: document.getElementById('m_name').value,
        email: document.getElementById('m_email').value
    });
    if(res) { msg("Dodano czytelnika"); e.target.reset(); loadAll(); }
}

async function addBook(e) {
    e.preventDefault();
    const res = await req('/books', 'POST', {
        title: document.getElementById('b_title').value,
        author: document.getElementById('b_author').value,
        copies: parseInt(document.getElementById('b_copies').value)
    });
    if(res) { msg("Dodano książkę"); e.target.reset(); loadAll(); }
}

async function borrow(bookId) {
    const memberId = document.getElementById('memberSelect').value;
    if(!memberId) return alert("Wybierz czytelnika z listy!");
    
    const res = await req('/loans/borrow', 'POST', { 
        member_id: parseInt(memberId), book_id: bookId 
    });
    if(res) { msg("Wypożyczono!"); loadAll(); }
}

async function returnBook(loanId) {
    if(!confirm("Potwierdź zwrot")) return;
    const res = await req('/loans/return', 'POST', { loan_id: loanId });
    if(res) { msg("Zwrócono!"); loadAll(); }
}

// Start
loadAll();