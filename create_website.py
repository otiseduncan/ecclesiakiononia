#!/usr/bin/env python3
"""
Advanced book parser and modern website generator for The Forgotten Books of Eden.
Creates a clean, modern, responsive website with proper book organization.
"""

import os
import re
import json
from bs4 import BeautifulSoup
from pathlib import Path

class BookParser:
    def __init__(self, source_dir, output_dir):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.books = {}
        self.chapters = {}
        
    def extract_clean_content(self, html_content):
        """Extract clean, readable content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove all navigation, scripts, and metadata
        for element in soup.find_all(['script', 'nav', 'style', 'head']):
            element.decompose()
        
        # Find the main content body
        body = soup.find('body')
        if not body:
            return "", ""
        
        # Remove navigation elements but keep content
        for nav_element in body.find_all(['center', 'hr']):
            # Keep center elements that contain actual content (headings, paragraphs)
            if nav_element.name == 'center' and not (nav_element.find('h1') or nav_element.find('h2') or nav_element.find('h3') or nav_element.find('p')):
                nav_element.decompose()
            elif nav_element.name == 'hr':
                nav_element.decompose()
        
        # Extract title from first heading
        title = ""
        for heading in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            title = heading.get_text().strip()
            if title and not title.lower().startswith('the forgotten books'):
                break
        
        # Convert to clean text while preserving structure
        content_html = ""
        for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'blockquote']):
            if element.get_text().strip():
                content_html += str(element) + "\n"
        
        return title, content_html
    
    def identify_book_sections(self):
        """Identify the different books and their file ranges."""
        book_sections = {
            'title_pages': ['fbe000.htm', 'fbe001.htm', 'fbe002.htm', 'fbe003.htm', 'fbe004.htm'],
            'first_book_adam_eve': [],
            'second_book_adam_eve': [],
            'secrets_enoch': [],
            'psalms_solomon': [],
            'odes_solomon': [],
            'letter_aristeas': [],
            'fourth_maccabees': [],
            'story_ahikar': [],
            'testaments_patriarchs': [],
            'index_pages': ['index.htm', 'pageidx.htm']
        }
        
        # Based on the table of contents, determine file ranges
        html_files = sorted([f for f in os.listdir(self.source_dir) if f.endswith('.htm') and f.startswith('fbe')])
        
        current_section = 'title_pages'
        for filename in html_files:
            if filename in book_sections['title_pages'] or filename in book_sections['index_pages']:
                continue
            
            # Read file to determine which book section it belongs to
            try:
                with open(self.source_dir / filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title, _ = self.extract_clean_content(content)
                title_lower = title.lower()
                
                if 'first book of adam' in title_lower:
                    current_section = 'first_book_adam_eve'
                elif 'second book of adam' in title_lower:
                    current_section = 'second_book_adam_eve'
                elif 'secrets of enoch' in title_lower or 'book of the secrets of enoch' in title_lower:
                    current_section = 'secrets_enoch'
                elif 'psalms of solomon' in title_lower:
                    current_section = 'psalms_solomon'
                elif 'odes of solomon' in title_lower:
                    current_section = 'odes_solomon'
                elif 'letter of aristeas' in title_lower:
                    current_section = 'letter_aristeas'
                elif 'fourth book of maccabees' in title_lower or 'maccabees' in title_lower:
                    current_section = 'fourth_maccabees'
                elif 'story of ahikar' in title_lower or 'ahikar' in title_lower:
                    current_section = 'story_ahikar'
                elif 'testament' in title_lower:
                    current_section = 'testaments_patriarchs'
                
                book_sections[current_section].append(filename)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        return book_sections
    
    def generate_modern_website(self):
        """Generate a complete modern website."""
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / 'css').mkdir(exist_ok=True)
        (self.output_dir / 'js').mkdir(exist_ok=True)
        (self.output_dir / 'books').mkdir(exist_ok=True)
        
        # Get book sections
        book_sections = self.identify_book_sections()
        
        # Process each book section
        books_data = {}
        for section_name, files in book_sections.items():
            if section_name in ['title_pages', 'index_pages'] or not files:
                continue
            
            book_data = self.process_book_section(section_name, files)
            if book_data:
                books_data[section_name] = book_data
        
        # Generate website files
        self.create_css()
        self.create_javascript()
        self.create_index_page(books_data)
        self.create_book_pages(books_data)
        
        return books_data
    
    def process_book_section(self, section_name, files):
        """Process a section of files into a structured book."""
        book_data = {
            'id': section_name,
            'title': self.get_book_title(section_name),
            'chapters': []
        }
        
        for filename in files:
            try:
                with open(self.source_dir / filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title, clean_html = self.extract_clean_content(content)
                
                if title and clean_html:
                    chapter = {
                        'filename': filename,
                        'title': title,
                        'content': clean_html
                    }
                    book_data['chapters'].append(chapter)
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        return book_data if book_data['chapters'] else None
    
    def get_book_title(self, section_name):
        """Get human-readable book title."""
        titles = {
            'first_book_adam_eve': 'The First Book of Adam and Eve',
            'second_book_adam_eve': 'The Second Book of Adam and Eve',
            'secrets_enoch': 'The Book of the Secrets of Enoch',
            'psalms_solomon': 'The Psalms of Solomon',
            'odes_solomon': 'The Odes of Solomon',
            'letter_aristeas': 'The Letter of Aristeas',
            'fourth_maccabees': 'The Fourth Book of Maccabees',
            'story_ahikar': 'The Story of Ahikar',
            'testaments_patriarchs': 'The Testaments of the Twelve Patriarchs'
        }
        return titles.get(section_name, section_name.replace('_', ' ').title())
    
    def create_css(self):
        """Create modern CSS stylesheet."""
        css_content = '''
/* Modern CSS for The Forgotten Books of Eden */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #34495e;
    --accent-color: #e74c3c;
    --background-color: #ecf0f1;
    --text-color: #2c3e50;
    --light-gray: #bdc3c7;
    --white: #ffffff;
    --font-size-base: 18px;
    --line-height-base: 1.6;
    --border-radius: 8px;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: var(--font-size-base);
    line-height: var(--line-height-base);
    color: var(--text-color);
    background-color: var(--background-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: var(--white);
    padding: 2rem 0;
    text-align: center;
    box-shadow: var(--shadow);
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 300;
}

.header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Navigation */
.nav {
    background: var(--white);
    padding: 1rem 0;
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
}

.nav a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
}

.nav a:hover {
    background-color: var(--primary-color);
    color: var(--white);
}

/* Main Content */
.main {
    padding: 3rem 0;
    min-height: 60vh;
}

/* Books Grid */
.books-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.book-card {
    background: var(--white);
    padding: 2rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.book-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.book-card h2 {
    color: var(--primary-color);
    margin-bottom: 1rem;
    font-size: 1.4rem;
}

.book-card p {
    color: var(--secondary-color);
    margin-bottom: 1.5rem;
}

.book-card .btn {
    display: inline-block;
    background: var(--accent-color);
    color: var(--white);
    padding: 0.75rem 1.5rem;
    text-decoration: none;
    border-radius: var(--border-radius);
    font-weight: 500;
    transition: background-color 0.3s ease;
}

.book-card .btn:hover {
    background-color: #c0392b;
}

/* Reading Interface */
.reading-container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--white);
    padding: 3rem;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}

.chapter-nav {
    background: var(--background-color);
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.chapter-select {
    padding: 0.5rem 1rem;
    border: 2px solid var(--light-gray);
    border-radius: var(--border-radius);
    font-size: 1rem;
    background: var(--white);
}

.chapter-nav .btn {
    background: var(--primary-color);
    color: var(--white);
    padding: 0.5rem 1rem;
    text-decoration: none;
    border-radius: var(--border-radius);
    font-size: 0.9rem;
}

.chapter-content h1, .chapter-content h2, .chapter-content h3 {
    color: var(--primary-color);
    margin: 2rem 0 1rem 0;
    line-height: 1.3;
}

.chapter-content h1 {
    font-size: 2rem;
    text-align: center;
    border-bottom: 2px solid var(--light-gray);
    padding-bottom: 1rem;
}

.chapter-content h2 {
    font-size: 1.5rem;
}

.chapter-content h3 {
    font-size: 1.2rem;
}

.chapter-content p {
    margin-bottom: 1.5rem;
    text-align: justify;
    text-indent: 1.5rem;
}

.chapter-content blockquote {
    border-left: 4px solid var(--accent-color);
    margin: 2rem 0;
    padding: 1rem 2rem;
    background: var(--background-color);
    font-style: italic;
}

/* Search */
.search-container {
    text-align: center;
    margin-bottom: 3rem;
}

.search-input {
    width: 100%;
    max-width: 500px;
    padding: 1rem 1.5rem;
    border: 2px solid var(--light-gray);
    border-radius: var(--border-radius);
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.search-input:focus {
    outline: none;
    border-color: var(--primary-color);
}

/* Footer */
.footer {
    background: var(--primary-color);
    color: var(--white);
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
    }
    
    .nav ul {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .reading-container {
        padding: 1.5rem;
        margin: 0 1rem;
    }
    
    .chapter-nav {
        flex-direction: column;
        text-align: center;
    }
    
    .books-grid {
        grid-template-columns: 1fr;
    }
    
    .container {
        padding: 0 15px;
    }
}

/* Print Styles */
@media print {
    .nav, .chapter-nav, .footer {
        display: none !important;
    }
    
    .reading-container {
        box-shadow: none;
        padding: 0;
    }
    
    .chapter-content {
        font-size: 12pt;
        line-height: 1.4;
    }
}
'''
        
        with open(self.output_dir / 'css' / 'style.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def create_javascript(self):
        """Create JavaScript for enhanced functionality."""
        js_content = '''
// JavaScript for The Forgotten Books of Eden Website

document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const bookCards = document.querySelectorAll('.book-card');
            
            bookCards.forEach(card => {
                const title = card.querySelector('h2').textContent.toLowerCase();
                const description = card.querySelector('p').textContent.toLowerCase();
                
                if (title.includes(query) || description.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Chapter navigation
    const chapterSelect = document.getElementById('chapterSelect');
    if (chapterSelect) {
        chapterSelect.addEventListener('change', function() {
            const selectedChapter = this.value;
            if (selectedChapter) {
                window.location.href = selectedChapter;
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Reading progress indicator
    const readingContainer = document.querySelector('.chapter-content');
    if (readingContainer) {
        const progressBar = document.createElement('div');
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: #e74c3c;
            z-index: 1000;
            transition: width 0.1s ease;
        `;
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.offsetHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            progressBar.style.width = scrollPercent + '%';
        });
    }
});
'''
        
        with open(self.output_dir / 'js' / 'script.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def create_index_page(self, books_data):
        """Create the main index page."""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Forgotten Books of Eden - Sacred Texts Collection</title>
    <meta name="description" content="A modern, readable collection of The Forgotten Books of Eden, featuring ancient texts including the Books of Adam and Eve, Enoch, Solomon, and the Twelve Patriarchs.">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>The Forgotten Books of Eden</h1>
            <p>Ancient Sacred Texts - Edited by Rutherford H. Platt, Jr. (1926)</p>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#books">Books</a></li>
                <li><a href="#about">About</a></li>
            </ul>
        </div>
    </nav>

    <main class="main">
        <div class="container">
            <section id="home">
                <div class="search-container">
                    <input type="text" id="search" class="search-input" placeholder="Search books and content...">
                </div>
                
                <div class="reading-container" style="margin-bottom: 3rem;">
                    <h2>Welcome to The Forgotten Books of Eden</h2>
                    <p>This collection contains ancient sacred texts that were not included in the canonical Bible but have been preserved through the centuries. These writings provide fascinating insights into early religious thought and the cultural context of biblical times.</p>
                    
                    <p>Originally edited by Rutherford H. Platt, Jr. in 1926, these texts include apocryphal and pseudepigraphal works that influenced early Christian and Jewish communities. The collection features stories that expand upon biblical narratives and provide additional context for understanding ancient religious traditions.</p>
                    
                    <p>Each book has been carefully formatted for modern reading while preserving the authentic content and meaning of these ancient texts.</p>
                </div>
            </section>

            <section id="books">
                <h2 style="text-align: center; margin-bottom: 2rem; color: var(--primary-color);">The Collection</h2>
                <div class="books-grid">'''
        
        # Add book cards
        book_descriptions = {
            'first_book_adam_eve': 'The story of Adam and Eve after their expulsion from Eden, including their trials, temptations, and the birth of Cain and Abel.',
            'second_book_adam_eve': 'Continuation of the Adam and Eve narrative, covering the patriarchs who lived before the Flood.',
            'secrets_enoch': 'The mystical journey of Enoch through the heavens and his revelations about divine mysteries.',
            'psalms_solomon': 'A collection of eighteen psalms attributed to King Solomon, reflecting on righteousness and divine judgment.',
            'odes_solomon': 'Forty-two mystical odes expressing deep spiritual truths and early Christian thought.',
            'letter_aristeas': 'The account of how the Hebrew scriptures were translated into Greek (the Septuagint).',
            'fourth_maccabees': 'A philosophical discourse on the supremacy of devout reason over the passions.',
            'story_ahikar': 'The tale of Ahikar, a wise counselor, and his ungrateful nephew Nadan.',
            'testaments_patriarchs': 'The final words and teachings of the twelve sons of Jacob to their descendants.'
        }
        
        for book_id, book_data in books_data.items():
            description = book_descriptions.get(book_id, 'An important ancient text preserved in this collection.')
            chapter_count = len(book_data['chapters'])
            
            html_content += f'''
                    <div class="book-card">
                        <h2>{book_data['title']}</h2>
                        <p>{description}</p>
                        <p><strong>{chapter_count} chapters</strong></p>
                        <a href="books/{book_id}.html" class="btn">Read Now</a>
                    </div>'''
        
        html_content += '''
                </div>
            </section>

            <section id="about" style="margin-top: 4rem;">
                <div class="reading-container">
                    <h2>About This Collection</h2>
                    <p>The Forgotten Books of Eden represents one of the most important collections of ancient religious texts outside the canonical Bible. These works, compiled and translated by various scholars, offer unique insights into the religious and cultural milieu of ancient times.</p>
                    
                    <p>This modern digital edition preserves the complete text while presenting it in a clean, readable format optimized for contemporary readers. The original 1926 edition by Rutherford H. Platt, Jr. has been carefully converted to provide an enhanced reading experience while maintaining scholarly accuracy.</p>
                    
                    <h3>Historical Context</h3>
                    <p>These texts come from various sources and time periods, representing the rich diversity of ancient religious literature. Many were known to early Christian communities and influenced the development of religious thought, even though they were not included in the final biblical canon.</p>
                    
                    <h3>Modern Presentation</h3>
                    <p>This website presents the texts with modern typography, responsive design, and enhanced navigation to make these ancient works accessible to today's readers. Each book includes chapter navigation and the full original content.</p>
                </div>
            </section>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 The Forgotten Books of Eden - Digital Edition</p>
            <p>Original text in the public domain. Modern presentation and formatting.</p>
        </div>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>'''
        
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def create_book_pages(self, books_data):
        """Create individual book reading pages."""
        for book_id, book_data in books_data.items():
            self.create_book_page(book_id, book_data, books_data)
    
    def create_book_page(self, book_id, book_data, all_books):
        """Create a single book reading page."""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_data['title']} - The Forgotten Books of Eden</title>
    <meta name="description" content="Read {book_data['title']} from The Forgotten Books of Eden collection. Ancient sacred text in modern, readable format.">
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{book_data['title']}</h1>
            <p>From The Forgotten Books of Eden Collection</p>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="../index.html#books">All Books</a></li>'''
        
        # Add navigation to other books
        for other_id, other_book in all_books.items():
            if other_id != book_id:
                html_content += f'<li><a href="{other_id}.html">{other_book["title"]}</a></li>'
        
        html_content += '''
            </ul>
        </div>
    </nav>

    <main class="main">
        <div class="container">
            <div class="reading-container">
                <div class="chapter-nav">
                    <select id="chapterSelect" class="chapter-select">
                        <option value="">Select Chapter...</option>'''
        
        # Add chapter options
        for i, chapter in enumerate(book_data['chapters']):
            html_content += f'<option value="#{chapter["filename"]}">{chapter["title"]}</option>'
        
        html_content += '''
                    </select>
                    <a href="../index.html" class="btn">← Back to Collection</a>
                </div>

                <div class="chapter-content">'''
        
        # Add all chapters
        for chapter in book_data['chapters']:
            html_content += f'''
                    <div id="{chapter['filename']}" class="chapter">
                        {chapter['content']}
                    </div>'''
        
        html_content += '''
                </div>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 The Forgotten Books of Eden - Digital Edition</p>
            <p>Original text in the public domain. Modern presentation and formatting.</p>
        </div>
    </footer>

    <script src="../js/script.js"></script>
</body>
</html>'''
        
        with open(self.output_dir / 'books' / f'{book_id}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    parser = BookParser(
        source_dir='/home/otis/Documents/projects/christianresearch/sacred-texts',
        output_dir='/home/otis/Documents/projects/christianresearch/website'
    )
    
    print("Generating modern website for The Forgotten Books of Eden...")
    books_data = parser.generate_modern_website()
    
    print(f"\n✅ Website generated successfully!")
    print(f"📁 Output directory: {parser.output_dir}")
    print(f"📚 Books processed: {len(books_data)}")
    
    for book_id, book_data in books_data.items():
        print(f"   📖 {book_data['title']}: {len(book_data['chapters'])} chapters")
    
    print(f"\n🌐 Open {parser.output_dir}/index.html in your browser to view the website!")