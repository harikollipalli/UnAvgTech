// Dark mode functionality
function toggleTheme() {
    const body = document.body;
    const themeToggle = document.querySelector('.theme-toggle');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        themeToggle.innerHTML = '🌙';
        themeToggle.title = 'Toggle Dark Mode';
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-mode');
        themeToggle.innerHTML = '☀️';
        themeToggle.title = 'Toggle Light Mode';
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeToggle = document.querySelector('.theme-toggle');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '☀️';
            themeToggle.title = 'Toggle Light Mode';
        }
    }
});

// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const popup = document.getElementById('popup');
    if (popup) {
        setTimeout(() => {
            popup.style.opacity = '0';
            setTimeout(() => {
                popup.style.display = 'none';
            }, 500);
        }, 3000);
    }
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states to forms
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Processing...';
            submitBtn.disabled = true;
        }
    });
});

// Add hover effects to category buttons
document.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-3px) scale(1.02)';
    });
    
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
    });
});

// Add animation to blog cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.blog-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }
});

// Add focus management for accessibility
document.querySelectorAll('button, a, input, textarea, select').forEach(element => {
    element.addEventListener('focus', function() {
        this.style.outline = '2px solid #0d9488';
        this.style.outlineOffset = '2px';
    });
    
    element.addEventListener('blur', function() {
        this.style.outline = 'none';
    });
});

// Add confirmation for delete actions
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
});

// Add loading spinner for like/dislike buttons
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner">⏳</span>';
    button.disabled = true;
    
    return () => {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Enhanced like/dislike functions with loading states
function likeBlog(blogId) {
    const button = event.target;
    const resetButton = addLoadingState(button);
    
    fetch(`/api/like/${blogId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById(`likes-${blogId}`).textContent = data.likes;
            // Add success animation
            button.style.background = '#dcfce7';
            button.style.borderColor = '#22c55e';
            setTimeout(() => {
                button.style.background = '';
                button.style.borderColor = '';
            }, 1000);
        })
        .catch(error => {
            console.error('Error:', error);
            // Add error animation
            button.style.background = '#fef2f2';
            button.style.borderColor = '#ef4444';
            setTimeout(() => {
                button.style.background = '';
                button.style.borderColor = '';
            }, 1000);
        })
        .finally(resetButton);
}

function dislikeBlog(blogId) {
    const button = event.target;
    const resetButton = addLoadingState(button);
    
    fetch(`/api/dislike/${blogId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById(`dislikes-${blogId}`).textContent = data.dislikes;
            // Add success animation
            button.style.background = '#fef2f2';
            button.style.borderColor = '#ef4444';
            setTimeout(() => {
                button.style.background = '';
                button.style.borderColor = '';
            }, 1000);
        })
        .catch(error => {
            console.error('Error:', error);
            // Add error animation
            button.style.background = '#fef2f2';
            button.style.borderColor = '#ef4444';
            setTimeout(() => {
                button.style.background = '';
                button.style.borderColor = '';
            }, 1000);
        })
        .finally(resetButton);
}

// Add responsive menu toggle for mobile
function createMobileMenu() {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar && window.innerWidth <= 768) {
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = '☰';
        toggleBtn.className = 'mobile-menu-toggle';
        toggleBtn.style.cssText = `
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            display: none;
        `;
        
        const navbarContainer = document.querySelector('.navbar-container');
        navbarContainer.insertBefore(toggleBtn, navbar);
        
        toggleBtn.addEventListener('click', function() {
            navbar.classList.toggle('mobile-menu-open');
        });
        
        // Hide menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbar.contains(e.target) && !toggleBtn.contains(e.target)) {
                navbar.classList.remove('mobile-menu-open');
            }
        });
    }
}

// Initialize mobile menu
window.addEventListener('load', createMobileMenu);
window.addEventListener('resize', createMobileMenu);