from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
from database import get_db_connection
from routes.auth import is_logged_in

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/')
@shop_bp.route('/products')
def products():
    """Danh sách sản phẩm với phân trang"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy tham số tìm kiếm và lọc
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    sort = request.args.get('sort', 'name_asc')
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Số sản phẩm mỗi trang
    
    # Xây dựng query
    query = "SELECT * FROM products WHERE is_active = 1"
    count_query = "SELECT COUNT(*) as total FROM products WHERE is_active = 1"
    params = []
    
    if search:
        query += " AND name LIKE %s"
        count_query += " AND name LIKE %s"
        params.append(f'%{search}%')
    
    if category:
        query += " AND category = %s"
        count_query += " AND category = %s"
        params.append(category)
    
    if min_price is not None:
        query += " AND price >= %s"
        count_query += " AND price >= %s"
        params.append(min_price)
    
    if max_price is not None:
        query += " AND price <= %s"
        count_query += " AND price <= %s"
        params.append(max_price)
    
    # Đếm tổng số sản phẩm
    cursor.execute(count_query, params)
    total_products = cursor.fetchone()['total']
    total_pages = (total_products + per_page - 1) // per_page  # Làm tròn lên
    
    # Sắp xếp
    if sort == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort == 'name_desc':
        query += " ORDER BY name DESC"
    else:
        query += " ORDER BY name ASC"
    
    # Thêm LIMIT và OFFSET cho phân trang
    offset = (page - 1) * per_page
    query += f" LIMIT {per_page} OFFSET {offset}"
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    
    # Lấy danh sách categories
    cursor.execute("SELECT DISTINCT category FROM products WHERE is_active = 1 ORDER BY category")
    categories = [cat['category'] for cat in cursor.fetchall()]
    
    # Lấy số lượng sản phẩm trong giỏ hàng
    cart_count = 0
    if is_logged_in():
        cursor.execute("SELECT SUM(quantity) as total FROM cart WHERE user_id = %s", (session['user_id'],))
        result = cursor.fetchone()
        cart_count = result['total'] if result['total'] else 0
    
    cursor.close()
    conn.close()
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         cart_count=cart_count,
                         search=search,
                         selected_category=category,
                         min_price=min_price,
                         max_price=max_price,
                         sort=sort,
                         page=page,
                         total_pages=total_pages,
                         total_products=total_products)

@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Chi tiết sản phẩm"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE id = %s AND is_active = 1", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('❌ Sản phẩm không tồn tại!', 'error')
        return redirect(url_for('shop.products'))
    
    # Lấy số lượng sản phẩm trong giỏ hàng
    cart_count = 0
    if is_logged_in():
        cursor.execute("SELECT SUM(quantity) as total FROM cart WHERE user_id = %s", (session['user_id'],))
        result = cursor.fetchone()
        cart_count = result['total'] if result['total'] else 0
    
    cursor.close()
    conn.close()
    
    return render_template('product_detail.html', product=product, cart_count=cart_count)

@shop_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Thêm sản phẩm vào giỏ hàng"""
    if not is_logged_in():
        flash('⚠️ Vui lòng đăng nhập để mua hàng!', 'warning')
        return redirect(url_for('auth.login'))
    
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('❌ Số lượng không hợp lệ!', 'error')
        return redirect(request.referrer or url_for('shop.products'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kiểm tra sản phẩm tồn tại và còn hàng
    cursor.execute("SELECT * FROM products WHERE id = %s AND is_active = 1", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('❌ Sản phẩm không tồn tại!', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('shop.products'))
    
    if product['stock'] < quantity:
        flash(f'❌ Chỉ còn {product["stock"]} sản phẩm trong kho!', 'error')
        cursor.close()
        conn.close()
        return redirect(request.referrer or url_for('shop.products'))
    
    # Thêm hoặc cập nhật giỏ hàng
    try:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (session['user_id'], product_id, quantity, quantity))
        conn.commit()
        flash(f'✅ Đã thêm {product["name"]} vào giỏ hàng!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'❌ Lỗi: {str(e)}', 'error')
    
    cursor.close()
    conn.close()
    
    return redirect(request.referrer or url_for('shop.products'))

@shop_bp.route('/cart')
def cart():
    """Giỏ hàng"""
    if not is_logged_in():
        flash('⚠️ Vui lòng đăng nhập để xem giỏ hàng!', 'warning')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.quantity, p.id as product_id, p.name, p.price, p.image_url, p.stock
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['user_id'],))
    cart_items = cursor.fetchall()
    
    # Tính tổng tiền
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Lấy số lượng sản phẩm trong giỏ hàng
    cart_count = sum(item['quantity'] for item in cart_items)
    
    cursor.close()
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total, cart_count=cart_count)

@shop_bp.route('/update-cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'}), 401
    
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        return jsonify({'success': False, 'message': 'Số lượng không hợp lệ'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kiểm tra quyền sở hữu cart item
    cursor.execute("SELECT * FROM cart WHERE id = %s AND user_id = %s", (cart_id, session['user_id']))
    cart_item = cursor.fetchone()
    
    if not cart_item:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    
    # Kiểm tra tồn kho
    cursor.execute("SELECT stock FROM products WHERE id = %s", (cart_item['product_id'],))
    product = cursor.fetchone()
    
    if product['stock'] < quantity:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': f'Chỉ còn {product["stock"]} sản phẩm'}), 400
    
    # Cập nhật
    cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", (quantity, cart_id))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Đã cập nhật'})

@shop_bp.route('/remove-from-cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    if not is_logged_in():
        flash('⚠️ Vui lòng đăng nhập!', 'warning')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (cart_id, session['user_id']))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    flash('✅ Đã xóa sản phẩm khỏi giỏ hàng!', 'success')
    return redirect(url_for('shop.cart'))

@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Thanh toán"""
    if not is_logged_in():
        flash('⚠️ Vui lòng đăng nhập để thanh toán!', 'warning')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Lấy thông tin giao hàng
        shipping_name = request.form.get('shipping_name', '').strip()
        shipping_phone = request.form.get('shipping_phone', '').strip()
        shipping_address = request.form.get('shipping_address', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not all([shipping_name, shipping_phone, shipping_address]):
            flash('❌ Vui lòng điền đầy đủ thông tin giao hàng!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('shop.checkout'))
        
        # Lấy giỏ hàng
        cursor.execute("""
            SELECT c.id, c.quantity, p.id as product_id, p.name, p.price, p.stock
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (session['user_id'],))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            flash('❌ Giỏ hàng trống!', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('shop.cart'))
        
        # Kiểm tra tồn kho
        for item in cart_items:
            if item['stock'] < item['quantity']:
                flash(f'❌ Sản phẩm {item["name"]} chỉ còn {item["stock"]} trong kho!', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('shop.cart'))
        
        # Tính tổng tiền
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        
        try:
            # Tạo đơn hàng
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, shipping_name, shipping_phone, shipping_address, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], total_amount, shipping_name, shipping_phone, shipping_address, notes))
            order_id = cursor.lastrowid
            
            # Thêm chi tiết đơn hàng và cập nhật tồn kho
            for item in cart_items:
                subtotal = item['price'] * item['quantity']
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (order_id, item['product_id'], item['name'], item['price'], item['quantity'], subtotal))
                
                # Giảm tồn kho
                cursor.execute("""
                    UPDATE products SET stock = stock - %s WHERE id = %s
                """, (item['quantity'], item['product_id']))
            
            # Xóa giỏ hàng
            cursor.execute("DELETE FROM cart WHERE user_id = %s", (session['user_id'],))
            
            conn.commit()
            flash('✅ Đặt hàng thành công! Chúng tôi sẽ liên hệ với bạn sớm.', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('shop.order_success', order_id=order_id))
            
        except Exception as e:
            conn.rollback()
            flash(f'❌ Lỗi: {str(e)}', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('shop.checkout'))
    
    # GET request - hiển thị trang checkout
    cursor.execute("""
        SELECT c.id, c.quantity, p.id as product_id, p.name, p.price, p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    """, (session['user_id'],))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('❌ Giỏ hàng trống!', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('shop.cart'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    cart_count = sum(item['quantity'] for item in cart_items)
    
    # Lấy thông tin user để điền sẵn
    cursor.execute("SELECT full_name, phone, address FROM users WHERE id = %s", (session['user_id'],))
    user_info = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         total=total, 
                         cart_count=cart_count,
                         user_info=user_info)

@shop_bp.route('/order-success/<int:order_id>')
def order_success(order_id):
    """Trang xác nhận đơn hàng thành công"""
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM orders WHERE id = %s AND user_id = %s
    """, (order_id, session['user_id']))
    order = cursor.fetchone()
    
    if not order:
        flash('❌ Không tìm thấy đơn hàng!', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('shop.products'))
    
    cursor.execute("""
        SELECT * FROM order_items WHERE order_id = %s
    """, (order_id,))
    order_items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('order_success.html', order=order, order_items=order_items)

@shop_bp.route('/order-history')
def order_history():
    """Lịch sử mua hàng của khách hàng"""
    if not is_logged_in():
        flash('⚠️ Vui lòng đăng nhập để xem lịch sử mua hàng!', 'warning')
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy danh sách đơn hàng của user
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()
    
    # Lấy chi tiết cho mỗi đơn hàng
    orders_with_items = []
    for order in orders:
        cursor.execute("""
            SELECT oi.*, p.image_url 
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order['id'],))
        items = cursor.fetchall()
        orders_with_items.append({
            'order': order,
            'items': items
        })
    
    cursor.close()
    conn.close()
    
    return render_template('order_history.html', orders_with_items=orders_with_items)
