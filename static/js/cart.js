// Функции для работы с корзиной
$(document).ready(function() {
    // AJAX для добавления товара в корзину
    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const url = form.attr('action');
        
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data) {
                if (data.success) {
                    // Обновление счетчика товаров в корзине
                    $('#cart-items-count').text(data.cart_items_count);
                    
                    // Показать уведомление
                    showNotification('Товар добавлен в корзину', 'success');
                }
            },
            error: function() {
                showNotification('Ошибка при добавлении товара в корзину', 'danger');
            }
        });
    });
    
    // AJAX для удаления товара из корзины
    $('.remove-from-cart-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const url = form.attr('action');
        const itemRow = form.closest('.cart-item');
        
        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data) {
                if (data.success) {
                    // Удаление строки товара
                    itemRow.fadeOut(300, function() {
                        $(this).remove();
                        
                        // Если корзина пуста
                        if (data.cart_items_count === 0) {
                            $('.cart-container').html('<div class="alert alert-info">Ваша корзина пуста.</div>');
                        }
                    });
                    
                    // Обновление счетчика и суммы
                    $('#cart-items-count').text(data.cart_items_count);
                    $('.cart-total').text(data.cart_total + ' ₽');
                    
                    // Показать уведомление
                    showNotification('Товар удален из корзины', 'success');
                }
            },
            error: function() {
                showNotification('Ошибка при удалении товара из корзины', 'danger');
            }
        });
    });
});

// Функция для отображения уведомлений
function showNotification(message, type) {
    const notification = $(`
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(notification);
    const toast = new bootstrap.Toast(notification);
    toast.show();
    
    // Автоматическое удаление уведомления после закрытия
    notification.on('hidden.bs.toast', function() {
        $(this).remove();
    });
} 