const API = "http://localhost:8001/api"; 

let currentCartTotal = 0;
let activeCoupon = null;

async function req(url, method="GET", body=null) {
    try {
        const opts = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(API + url, opts);
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Błąd');
        }
        return res.json();
    } catch (e) {
        showMsg(e.message);
        return null;
    }
}

function showMsg(text) {
    const el = document.getElementById('msg');
    el.innerText = text;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

// Logika przeliczania cen w UI
function updateTotalsDisplay() {
    const subtotalEl = document.getElementById('cartSubtotal');
    const discountEl = document.getElementById('cartDiscount');
    const finalEl = document.getElementById('cartFinalTotal');
    const msgEl = document.getElementById('discountMsg');

    let discountAmount = 0;

    if (activeCoupon) {
        discountAmount = currentCartTotal * (activeCoupon.percent / 100);
        msgEl.textContent = `Aktywny kupon: ${activeCoupon.code} (-${activeCoupon.percent}%)`;
        msgEl.style.display = 'block';
    } else {
        msgEl.style.display = 'none';
    }

    const finalTotal = currentCartTotal - discountAmount;

    subtotalEl.innerText = currentCartTotal.toFixed(2);
    discountEl.innerText = discountAmount.toFixed(2);
    finalEl.innerText = finalTotal.toFixed(2);
}

async function refresh() {
    const [products, cart] = await Promise.all([req('/products'), req('/cart')]);
    
    const pList = document.getElementById('productList');
    pList.innerHTML = '';
    products?.forEach(p => {
        pList.innerHTML += `
            <div class="item">
                <div>
                    <strong>${p.name}</strong> <br> 
                    <span style="color:#059669">${p.price.toFixed(2)} PLN</span>
                </div>
                <button class="add" onclick="addToCart(${p.id})">+</button>
            </div>`;
    });

    const cList = document.getElementById('cartList');
    cList.innerHTML = '';
    currentCartTotal = 0;

    if (!cart || cart.length === 0) {
        cList.innerHTML = '<div style="padding:10px; color:#94a3b8; text-align:center">Koszyk jest pusty</div>';
    } else {
        cart.forEach(item => {
            const itemTotal = item.qty * item.product.price;
            currentCartTotal += itemTotal;
            
            cList.innerHTML += `
                <div class="item">
                    <div>
                        <strong>${item.product.name}</strong><br>
                        <small>${item.product.price.toFixed(2)} x </small>
                        <input class="qty-input" type="number" value="${item.qty}" min="1" 
                            onchange="updateQty(${item.product.id}, this.value)">
                    </div>
                    <div>
                        <b>${itemTotal.toFixed(2)}</b> 
                        <button class="remove" onclick="removeFromCart(${item.product.id})" style="margin-left:5px">X</button>
                    </div>
                </div>`;
        });
    }
    
    updateTotalsDisplay();
    
    loadOrders();
}

async function applyCoupon() {
    const codeInput = document.getElementById('couponInput');
    const code = codeInput.value.trim();
    const errEl = document.getElementById('errorMsg');
    const successMsg = document.getElementById('discountMsg');
    
    errEl.style.display = 'none';
    successMsg.style.display = 'none';
    activeCoupon = null;
    updateTotalsDisplay();
    
    if (!code) {
        errEl.textContent = "Wpisz kod rabatowy";
        errEl.style.display = 'block';
        return;
    }

    try {
        const coupon = await req(`/coupons/${code}`);
        
        if (coupon) {
            activeCoupon = { code: coupon.code, percent: coupon.discount_percent };
            
            successMsg.style.display = 'block'; 
            updateTotalsDisplay();
        }
    } catch (e) {
        console.error(e); 
        errEl.textContent = "Kod nieprawidłowy lub nieaktywny";
        errEl.style.display = 'block';
        
        activeCoupon = null;
        updateTotalsDisplay();
    }
}

async function createCoupon() {
    const code = document.getElementById('c_code').value;
    const percent = parseInt(document.getElementById('c_percent').value);
    if(!code || !percent) return alert("Podaj kod i procent");
    
    const res = await req('/coupons', 'POST', { code, discount_percent: percent });
    if(res) {
        showMsg(`Utworzono kupon ${code} (-${percent}%)`);
    }
}

async function addProduct() {
    const name = document.getElementById('new_name').value;
    const price = parseFloat(document.getElementById('new_price').value);
    if(!name || !price) return alert("Podaj nazwę i cenę");
    await req('/products', 'POST', { name, price });
    refresh();
}

async function addToCart(id) {
    await req('/cart/add', 'POST', { product_id: id, qty: 1 });
    refresh();
}

async function updateQty(id, qty) {
    await req(`/cart/item/${id}`, 'PATCH', { qty: parseInt(qty) });
    refresh();
}

async function removeFromCart(id) {
    await req(`/cart/item/${id}`, 'DELETE');
    refresh();
}

async function checkout() {
    const couponCode = activeCoupon ? activeCoupon.code : null;
    
    const order = await req('/checkout', 'POST', { coupon_code: couponCode });
    
    if (order) {
        activeCoupon = null;
        document.getElementById('couponInput').value = '';
        
        let msg = `Zamówienie #${order.id} złożone!`;
        if (order.discount_amount > 0) {
            msg += `\nNaliczono rabat: -${order.discount_amount.toFixed(2)} PLN`;
        }
        msg += `\nDo zapłaty: ${order.final_total.toFixed(2)} PLN`;
        
        alert(msg);
        refresh();
    } else {
        const errEl = document.getElementById('errorMsg');
        errEl.textContent = "Kupon nieważny (odrzucony przez serwer)";
        errEl.style.display = 'block';
        activeCoupon = null;
        updateTotalsDisplay();
    }
}

async function loadOrders() {
    const orders = await req('/orders');
    const list = document.getElementById('orderList');
    list.innerHTML = '';
    if(!orders || orders.length === 0) {
        list.innerHTML = '<div style="padding:10px; color:#94a3b8; text-align:center">Brak zamówień</div>';
        return;
    }
    orders.forEach(order => {
        const date = new Date(order.created_at).toLocaleString();
        let itemsHtml = order.items.map(i => `
            <div>
                • <strong>${i.product.name}</strong> 
                (${i.qty} szt.) x ${i.price.toFixed(2)} PLN
            </div>
        `).join('');
        const discountInfo = order.discount_amount > 0 
            ? `<div style="color:#ef4444; font-size:0.8em">Rabat: -${order.discount_amount.toFixed(2)} PLN</div>` 
            : '';

        list.innerHTML += `
            <div style="background:#f8fafc; border:1px solid #e2e8f0; padding:10px; margin-bottom:10px; border-radius:6px; font-size:0.9em">
                <div style="display:flex; justify-content:space-between; font-weight:bold; margin-bottom:5px;">
                    <span>#${order.id}</span>
                    <span>${date}</span>
                </div>
                <div style="margin-bottom:5px; color:#64748b">${itemsHtml}</div>
                ${discountInfo}
                <div style="text-align:right; font-weight:bold; margin-top:5px; border-top:1px dashed #e2e8f0; padding-top:5px;">
                    Razem: ${order.final_total.toFixed(2)} PLN
                </div>
            </div>`;
    });
}

refresh();