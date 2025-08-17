# UnAvg Tech - Blog Website

A modern, secure, and SEO-optimized blog website built with Flask.

## Features

- 🔍 **Search Functionality**: Search blogs by title or content
- 📱 **Social Sharing**: Share on WhatsApp, Facebook, Twitter, LinkedIn, Telegram
- 🔒 **Security**: CSRF protection, input validation, rate limiting
- 📊 **SEO Optimized**: Meta tags, structured data, sitemap, robots.txt
- 📈 **Analytics**: Visitor tracking and statistics
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Responsive**: Mobile-friendly design
- 👨‍💼 **Admin Panel**: Manage blogs, categories, and reviews

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   python setup_db.py
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the website:**
   - Homepage: http://localhost:5000
   - Admin: http://localhost:5000/admin/login

## Admin Access

- **Username**: admin (or as set in environment)
- **Password**: change-this-password (or as set in environment)

## Deployment

See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## Security

- All user inputs are validated and sanitized
- SQL injection protection with parameterized queries
- XSS protection with input sanitization
- CSRF protection on all forms
- Rate limiting on API endpoints
- Secure headers and HTTPS enforcement

## SEO Features

- Meta tags for social sharing
- Structured data (JSON-LD)
- XML sitemap generation
- Robots.txt configuration
- Mobile-friendly design
- Fast loading times

## License

MIT License - feel free to use this project for your own blog!
