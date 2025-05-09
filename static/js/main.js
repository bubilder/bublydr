// Основний файл JavaScript для проєкту

// Функція, яка виконується після завантаження DOM
document.addEventListener('DOMContentLoaded', function() {
    // Активація підказок
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Обробка кліків по столам у списку столів
    const tableCards = document.querySelectorAll('.table-card');
    tableCards.forEach(card => {
        card.addEventListener('click', () => {
            window.location.href = card.dataset.url;
        });
    });
    
    // Функція для оновлення суми замовлення при зміні кількості або знижки
    function updateOrderTotal() {
        const items = document.querySelectorAll('.order-item');
        let subtotal = 0;
        
        items.forEach(item => {
            const price = parseFloat(item.dataset.price);
            const quantity = parseInt(item.dataset.quantity);
            subtotal += price * quantity;
        });
        
        const discountPercent = parseFloat(document.getElementById('id_discount')?.value || 0);
        const discount = subtotal * (discountPercent / 100);
        const total = subtotal - discount;
        
        // Оновлюємо відображення
        if(document.getElementById('order-subtotal')) {
            document.getElementById('order-subtotal').textContent = subtotal.toFixed(2) + ' грн';
        }
        if(document.getElementById('order-discount')) {
            document.getElementById('order-discount').textContent = discount.toFixed(2) + ' грн';
        }
        if(document.getElementById('order-total')) {
            document.getElementById('order-total').textContent = total.toFixed(2) + ' грн';
        }
    }
    
    // Виклик функції при завантаженні сторінки
    updateOrderTotal();
    
    // Оновлення суми при зміні знижки
    const discountInput = document.getElementById('id_discount');
    if(discountInput) {
        discountInput.addEventListener('input', updateOrderTotal);
    }
    
    // Обробка вибору способу оплати
    const paymentMethodInputs = document.querySelectorAll('input[name="payment_method"]');
    const cashFields = document.getElementById('cash-payment-fields');
    
    paymentMethodInputs.forEach(input => {
        input.addEventListener('change', () => {
            if(input.value === 'CASH' && cashFields) {
                cashFields.classList.remove('d-none');
            } else if(cashFields) {
                cashFields.classList.add('d-none');
            }
        });
    });
    
    // Обчислення решти при готівковій оплаті
    const amountTenderedInput = document.getElementById('id_amount_tendered');
    const changeDisplay = document.getElementById('change-amount');
    const totalAmount = document.getElementById('total-to-pay');
    
    if(amountTenderedInput && changeDisplay && totalAmount) {
        amountTenderedInput.addEventListener('input', () => {
            const tendered = parseFloat(amountTenderedInput.value) || 0;
            const total = parseFloat(totalAmount.dataset.total) || 0;
            const change = tendered - total;
            
            if(change >= 0) {
                changeDisplay.textContent = change.toFixed(2) + ' грн';
                changeDisplay.className = 'text-success';
            } else {
                changeDisplay.textContent = 'Недостатньо коштів';
                changeDisplay.className = 'text-danger';
            }
        });
    }
});

// Функція для додавання страв до замовлення через AJAX
function addDishToOrder(orderId, dishId, el) {
    // Отримуємо CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Показуємо індикатор завантаження
    el.disabled = true;
    el.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Додаю...';
    
    // Виконуємо AJAX запит
    fetch(`/orders/${orderId}/add-item/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `dish=${dishId}&quantity=1`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Помилка мережі');
        }
        return response.json();
    })
    .then(data => {
        // Оновлюємо сторінку для відображення нового елемента
        window.location.reload();
    })
    .catch(error => {
        console.error('Помилка:', error);
        alert('Виникла помилка при додаванні страви до замовлення');
        el.disabled = false;
        el.innerHTML = 'Додати до замовлення';
    });
}

// Функція для видалення страв із замовлення через AJAX
function removeDishFromOrder(orderId, itemId, el) {
    if(!confirm('Ви впевнені, що хочете видалити цю страву з замовлення?')) {
        return;
    }
    
    // Отримуємо CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Показуємо індикатор завантаження
    el.disabled = true;
    el.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    
    // Виконуємо AJAX запит
    fetch(`/orders/${orderId}/remove-item/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Помилка мережі');
        }
        // Оновлюємо сторінку після видалення
        window.location.reload();
    })
    .catch(error => {
        console.error('Помилка:', error);
        alert('Виникла помилка при видаленні страви з замовлення');
        el.disabled = false;
        el.innerHTML = '<i class="fas fa-trash"></i>';
    });
}

// Функція для оновлення статусу замовлення
function updateOrderStatus(orderId, newStatus, el) {
    // Отримуємо CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Показуємо індикатор завантаження
    el.disabled = true;
    const originalText = el.innerHTML;
    el.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Оновлюю...';
    
    // Виконуємо AJAX запит
    fetch(`/orders/${orderId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `status=${newStatus}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Помилка мережі');
        }
        // Оновлюємо сторінку
        window.location.reload();
    })
    .catch(error => {
        console.error('Помилка:', error);
        alert('Виникла помилка при оновленні статусу замовлення');
        el.disabled = false;
        el.innerHTML = originalText;
    });
}