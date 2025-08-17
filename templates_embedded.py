"""
Embedded templates as fallback if templates directory is missing
"""

def get_embedded_template(template_name):
    """Get embedded template content"""
    templates = {
        'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnAvg Tech - Home</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .hero { text-align: center; margin-bottom: 40px; }
        .hero h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
        .hero p { color: #666; font-size: 1.2em; }
        .categories { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; }
        .category { background: #007bff; color: white; padding: 8px 16px; border-radius: 20px; text-decoration: none; }
        .blogs { display: grid; gap: 20px; }
        .blog-card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        .blog-title { color: #333; margin-bottom: 10px; }
        .blog-snippet { color: #666; line-height: 1.6; }
        .no-blogs { text-align: center; color: #666; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🚀 UnAvg Tech</h1>
            <p>This is a place to read, explore, and discover.</p>
        </div>
        
        {% if categories %}
        <div class="categories">
            {% for category in categories %}
            <a href="/category/{{ category.id }}" class="category" style="background-color: {{ category.color }};">
                {{ category.name.upper() }}
            </a>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if blogs %}
        <div class="blogs">
            {% for blog in blogs %}
            <div class="blog-card">
                <h3 class="blog-title">{{ blog.title }}</h3>
                <p class="blog-snippet">{{ blog.content[:150] }}{% if blog.content|length > 150 %}...{% endif %}</p>
                <small>Category: {{ blog.category_name }} | Date: {{ blog.created_at.split(' ')[0] if blog.created_at else 'Recently' }}</small>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-blogs">
            <p>🛌 No blogs yet. Maybe the writer is still dreaming!</p>
        </div>
        {% endif %}
        
        <hr style="margin: 40px 0;">
        <p style="text-align: center; color: #999;">
            <small>Powered by Flask | Template: Embedded Fallback</small>
        </p>
    </div>
</body>
</html>''',
        
        'categories.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categories - UnAvg Tech</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .category { background: #007bff; color: white; padding: 15px; margin: 10px 0; border-radius: 8px; text-decoration: none; display: block; }
        .category:hover { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Categories</h1>
        {% if categories %}
            {% for category in categories %}
            <a href="/category/{{ category.id }}" class="category" style="background-color: {{ category.color }};">
                {{ category.name }} ({{ category.blog_count }} blogs)
            </a>
            {% endfor %}
        {% else %}
            <p>No categories found.</p>
        {% endif %}
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>'''
    }
    
    return templates.get(template_name, f'<h1>Template {template_name} not found</h1>')

def render_embedded_template(template_name, **kwargs):
    """Render embedded template with variables"""
    template_content = get_embedded_template(template_name)
    
    # Simple template variable replacement
    for key, value in kwargs.items():
        if isinstance(value, list):
            # Handle lists (categories, blogs)
            if key == 'categories':
                categories_html = ''
                for category in value:
                    categories_html += f'<a href="/category/{category["id"]}" class="category" style="background-color: {category["color"]};">{category["name"].upper()}</a>'
                template_content = template_content.replace('{% for category in categories %}', '')
                template_content = template_content.replace('{{ category.name.upper() }}', '')
                template_content = template_content.replace('{% endfor %}', categories_html)
        else:
            # Handle simple variables
            template_content = template_content.replace(f'{{{{ {key} }}}}', str(value))
    
    return template_content
