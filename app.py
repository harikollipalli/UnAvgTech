from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import sqlite3
import random
from datetime import datetime
from urllib.parse import urljoin

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# List of colors for categories
COLORS = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1',
    '#14B8A6', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'
]

def get_random_color():
    return random.choice(COLORS)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Visitor tracking middleware
@app.before_request
def track_visitor():
    # Skip tracking for admin routes and static files
    if request.path.startswith('/admin') or request.path.startswith('/static'):
        return
    
    # Get visitor information
    page = request.path
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Log the visit
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO visitors (page, ip_address, user_agent, visited_at)
        VALUES (?, ?, ?, ?)
    ''', (page, ip_address, user_agent, datetime.now()))
    conn.commit()
    conn.close()

@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for SEO"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all blogs
    cursor.execute('SELECT id, title, created_at FROM blogs ORDER BY created_at DESC')
    blogs = cursor.fetchall()
    
    # Get all categories
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    
    conn.close()
    
    # Base URL - change this to your actual domain
    base_url = request.url_root.rstrip('/')
    
    # Create sitemap XML
    sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/search</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{base_url}/about</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/contact</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>{base_url}/categories</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>'''
    
    # Add category URLs
    for category in categories:
        sitemap_xml += f'''
    <url>
        <loc>{base_url}/category/{category['id']}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>'''
    
    # Add blog URLs
    for blog in blogs:
        lastmod = blog['created_at'] if blog['created_at'] else datetime.now()
        if isinstance(lastmod, str):
            lastmod = datetime.strptime(lastmod.split(' ')[0], '%Y-%m-%d')
        sitemap_xml += f'''
    <url>
        <loc>{base_url}/blog/{blog['id']}</loc>
        <lastmod>{lastmod.strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>'''
    
    sitemap_xml += '''
</urlset>'''
    
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get categories with blogs count
    cursor.execute('''
        SELECT c.id, c.name, c.color, COUNT(b.id) as blog_count
        FROM categories c
        LEFT JOIN blogs b ON c.id = b.category_id
        GROUP BY c.id, c.name, c.color
        ORDER BY c.id
    ''')
    categories = cursor.fetchall()
    
    # Get recent blogs with category names
    cursor.execute('''
        SELECT b.*, c.name as category_name, c.color as category_color
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.created_at DESC
        LIMIT 6
    ''')
    blogs = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', categories=categories, blogs=blogs)

@app.route('/categories')
def categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, COUNT(b.id) as blog_count
        FROM categories c
        LEFT JOIN blogs b ON c.id = b.category_id
        GROUP BY c.id, c.name, c.color
        ORDER BY c.id
    ''')
    categories = cursor.fetchall()
    
    conn.close()
    return render_template('categories.html', categories=categories)

@app.route('/category/<int:category_id>')
def category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get category info
    cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
    category = cursor.fetchone()
    
    if not category:
        flash('Category not found!', 'error')
        return redirect(url_for('index'))
    
    # Get blogs in this category
    cursor.execute('''
        SELECT b.*, c.name as category_name, c.color as category_color
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        WHERE b.category_id = ?
        ORDER BY b.created_at DESC
    ''', (category_id,))
    blogs = cursor.fetchall()
    
    conn.close()
    return render_template('category.html', category=category, blogs=blogs)

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get blog with category info
    cursor.execute('''
        SELECT b.*, c.name as category_name, c.color as category_color
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
    ''', (blog_id,))
    blog = cursor.fetchone()
    
    if not blog:
        flash('Blog not found!', 'error')
        return redirect(url_for('index'))
    
    # Get reviews for this blog
    cursor.execute('''
        SELECT * FROM reviews 
        WHERE blog_id = ? 
        ORDER BY created_at DESC
    ''', (blog_id,))
    reviews = cursor.fetchall()
    
    conn.close()
    return render_template('blog.html', blog=blog, reviews=reviews)

@app.route('/blog/<int:blog_id>/review', methods=['POST'])
def add_review(blog_id):
    review_text = request.form.get('review_text', '').strip()
    
    if not review_text:
        flash('Review text cannot be empty!', 'error')
        return redirect(url_for('blog', blog_id=blog_id))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (blog_id, text, created_at)
        VALUES (?, ?, ?)
    ''', (blog_id, review_text, datetime.now()))
    conn.commit()
    conn.close()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('blog', blog_id=blog_id))

@app.route('/api/like/<int:blog_id>', methods=['POST'])
def like_blog(blog_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE blogs SET likes = likes + 1 WHERE id = ?', (blog_id,))
    conn.commit()
    
    cursor.execute('SELECT likes FROM blogs WHERE id = ?', (blog_id,))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'likes': result['likes']})

@app.route('/api/dislike/<int:blog_id>', methods=['POST'])
def dislike_blog(blog_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE blogs SET dislikes = dislikes + 1 WHERE id = ?', (blog_id,))
    conn.commit()
    
    cursor.execute('SELECT dislikes FROM blogs WHERE id = ?', (blog_id,))
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({'dislikes': result['dislikes']})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([name, email, message]):
            flash('All fields are required!', 'error')
            return render_template('contact.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, email, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, email, message, datetime.now()))
        conn.commit()
        conn.close()
        
        flash('Thank you for reaching out!', 'success')
        return render_template('contact.html')
    
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'Hari' and password == 'Life@123':
            session['admin'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get categories
    cursor.execute('SELECT * FROM categories ORDER BY id')
    categories = cursor.fetchall()
    
    # Get blogs with category names
    cursor.execute('''
        SELECT b.*, c.name as category_name
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.created_at DESC
    ''')
    blogs = cursor.fetchall()
    
    # Get contact submissions
    cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
    contacts = cursor.fetchall()
    
    # Get visitor statistics
    cursor.execute('SELECT COUNT(*) as total_visits FROM visitors')
    total_visits = cursor.fetchone()['total_visits']
    
    cursor.execute('SELECT COUNT(DISTINCT ip_address) as unique_visitors FROM visitors')
    unique_visitors = cursor.fetchone()['unique_visitors']
    
    cursor.execute('SELECT COUNT(*) as today_visits FROM visitors WHERE DATE(visited_at) = DATE("now")')
    today_visits = cursor.fetchone()['today_visits']
    
    cursor.execute('''
        SELECT page, COUNT(*) as visits
        FROM visitors
        GROUP BY page
        ORDER BY visits DESC
        LIMIT 10
    ''')
    top_pages = cursor.fetchall()
    
    conn.close()
    
    visitor_stats = {
        'total_visits': total_visits,
        'unique_visitors': unique_visitors,
        'today_visits': today_visits,
        'top_pages': top_pages
    }
    
    return render_template('admin.html', 
                         categories=categories, 
                         blogs=blogs, 
                         contacts=contacts,
                         visitor_stats=visitor_stats)

@app.route('/admin/add_blog', methods=['POST'])
def add_blog():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category_id = request.form.get('category')
    
    if not all([title, content, category_id]):
        flash('All fields are required!', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO blogs (title, content, category_id, created_at)
        VALUES (?, ?, ?, ?)
    ''', (title, content, category_id, datetime.now()))
    conn.commit()
    conn.close()
    
    flash('Blog created successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_category', methods=['POST'])
def add_category():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('Category name is required!', 'error')
        return redirect(url_for('admin_panel'))
    
    color = get_random_color()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', (name, color))
        conn.commit()
        flash('Category added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Category name already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_category', methods=['POST'])
def edit_category():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    category_id = request.form.get('id')
    new_name = request.form.get('new_name', '').strip()
    
    if not all([category_id, new_name]):
        flash('All fields are required!', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
        conn.commit()
        flash('Category updated successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Category name already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_category', methods=['POST'])
def delete_category():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    category_id = request.form.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if category has blogs
    cursor.execute('SELECT COUNT(*) FROM blogs WHERE category_id = ?', (category_id,))
    blog_count = cursor.fetchone()[0]
    
    if blog_count > 0:
        flash('Cannot delete category with existing blogs!', 'error')
        conn.close()
        return redirect(url_for('admin_panel'))
    
    cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    conn.commit()
    conn.close()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_blog', methods=['POST'])
def edit_blog():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    blog_id = request.form.get('id')
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category_id = request.form.get('category')
    
    if not all([blog_id, title, content, category_id]):
        flash('All fields are required!', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE blogs 
        SET title = ?, content = ?, category_id = ?
        WHERE id = ?
    ''', (title, content, category_id, blog_id))
    conn.commit()
    conn.close()
    
    flash('Blog updated successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_blog', methods=['POST'])
def delete_blog():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    blog_id = request.form.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete reviews first
    cursor.execute('DELETE FROM reviews WHERE blog_id = ?', (blog_id,))
    
    # Delete blog
    cursor.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
    conn.commit()
    conn.close()
    
    flash('Blog deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_review', methods=['POST'])
def delete_review():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    review_id = request.form.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
    conn.commit()
    conn.close()
    
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/search')
def search():
    """Search functionality for blogs"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search in blog titles and content
    cursor.execute('''
        SELECT b.*, c.name as category_name, c.color as category_color
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        WHERE b.title LIKE ? OR b.content LIKE ?
        ORDER BY b.created_at DESC
    ''', (f'%{query}%', f'%{query}%'))
    
    blogs = cursor.fetchall()
    conn.close()
    
    return render_template('search_results.html', blogs=blogs, query=query)

@app.route('/blog/<int:blog_id>/share/<platform>')
def share_blog(blog_id, platform):
    """Social media sharing functionality"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get blog with category info
    cursor.execute('''
        SELECT b.*, c.name as category_name, c.color as category_color
        FROM blogs b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
    ''', (blog_id,))
    blog = cursor.fetchone()
    
    if not blog:
        flash('Blog not found!', 'error')
        return redirect(url_for('index'))
    
    conn.close()
    
    # Generate sharing URLs
    base_url = request.url_root.rstrip('/')
    blog_url = f"{base_url}/blog/{blog_id}"
    title = blog['title']
    description = blog['content'][:150] + "..." if len(blog['content']) > 150 else blog['content']
    
    sharing_urls = {
        'whatsapp': f"https://wa.me/?text={title}%20{blog_url}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={blog_url}",
        'twitter': f"https://twitter.com/intent/tweet?text={title}&url={blog_url}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={blog_url}",
        'telegram': f"https://t.me/share/url?url={blog_url}&text={title}",
        'email': f"mailto:?subject={title}&body=Check out this blog: {blog_url}",
        'copy': blog_url
    }
    
    if platform in sharing_urls:
        return redirect(sharing_urls[platform])
    else:
        flash('Invalid sharing platform!', 'error')
        return redirect(url_for('blog', blog_id=blog_id))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=False)