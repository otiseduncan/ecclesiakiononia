#!/usr/bin/env python3
"""
Improved book parser for The Forgotten Books of Eden - ensures all books are captured.
"""

import os
import re
import json
from bs4 import BeautifulSoup
from pathlib import Path

def improve_website():
    """Improve the existing website by adding missing Adam and Eve books."""
    source_dir = Path('/home/otis/Documents/projects/christianresearch/sacred-texts')
    output_dir = Path('/home/otis/Documents/projects/christianresearch/website')
    
    # Read a few Adam and Eve files to check content
    adam_eve_files = []
    enoch_start = None
    
    html_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.htm') and f.startswith('fbe') and f[3:6].isdigit()])
    
    for filename in html_files[5:]:  # Skip first 5 (title pages)
        try:
            with open(source_dir / filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            og_title = soup.find('meta', property='og:title')
            
            title = ""
            if og_title:
                title = og_title.get('content', '').replace(' | Sacred Texts Archive', '')
            elif title_tag:
                title = title_tag.get_text().replace(' | Sacred Texts Archive', '')
            
            print(f"{filename}: {title}")
            
            # Check for book transitions
            if 'secrets of enoch' in title.lower() or 'book of the secrets' in title.lower():
                enoch_start = filename
                break
            elif 'adam' in title.lower() and 'eve' in title.lower():
                adam_eve_files.append(filename)
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    print(f"\nFound {len(adam_eve_files)} Adam and Eve files")
    print(f"Enoch starts at: {enoch_start}")
    
    # Now determine the split between first and second book of Adam and Eve
    first_book_files = []
    second_book_files = []
    
    current_book = "first"
    for filename in adam_eve_files:
        try:
            with open(source_dir / filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            og_title = soup.find('meta', property='og:title')
            
            title = ""
            if og_title:
                title = og_title.get('content', '').replace(' | Sacred Texts Archive', '')
            elif title_tag:
                title = title_tag.get_text().replace(' | Sacred Texts Archive', '')
            
            if 'second book of adam' in title.lower():
                current_book = "second"
            
            if current_book == "first":
                first_book_files.append(filename)
            else:
                second_book_files.append(filename)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"First Book of Adam and Eve: {len(first_book_files)} files")
    print(f"Second Book of Adam and Eve: {len(second_book_files)} files")
    
    # Create the Adam and Eve books
    create_adam_eve_book("first_book_adam_eve", "The First Book of Adam and Eve", first_book_files, source_dir, output_dir)
    create_adam_eve_book("second_book_adam_eve", "The Second Book of Adam and Eve", second_book_files, source_dir, output_dir)
    
    # Update the index page
    update_index_page(output_dir)

def create_adam_eve_book(book_id, book_title, files, source_dir, output_dir):
    """Create a book page for Adam and Eve."""
    chapters = []
    
    for filename in files:
        try:
            with open(source_dir / filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title, clean_html = extract_clean_content(content)
            
            if title and clean_html:
                chapters.append({
                    'filename': filename,
                    'title': title,
                    'content': clean_html
                })
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    if not chapters:
        print(f"No chapters found for {book_title}")
        return
    
    # Create the book page
    create_book_html(book_id, book_title, chapters, output_dir)
    print(f"Created {book_title} with {len(chapters)} chapters")

def extract_clean_content(html_content):
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
    
    # Extract title from first heading or meta tag
    title = ""
    og_title = soup.find('meta', property='og:title')
    if og_title:
        title = og_title.get('content', '').replace(' | Sacred Texts Archive', '')
    
    if not title:
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

def create_book_html(book_id, book_title, chapters, output_dir):
    """Create HTML for a book."""
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_title} - The Forgotten Books of Eden</title>
    <meta name="description" content="Read {book_title} from The Forgotten Books of Eden collection. Ancient sacred text in modern, readable format.">
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{book_title}</h1>
            <p>From The Forgotten Books of Eden Collection</p>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="../index.html#books">All Books</a></li>
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
    for i, chapter in enumerate(chapters):
        html_content += f'<option value="#{chapter["filename"]}">{chapter["title"]}</option>'
    
    html_content += '''
                    </select>
                    <a href="../index.html" class="btn">← Back to Collection</a>
                </div>

                <div class="chapter-content">'''
    
    # Add all chapters
    for chapter in chapters:
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
    
    with open(output_dir / 'books' / f'{book_id}.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def update_index_page(output_dir):
    """Update the index page to include Adam and Eve books."""
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
                <div class="books-grid">
                    <div class="book-card">
                        <h2>The First Book of Adam and Eve</h2>
                        <p>The story of Adam and Eve after their expulsion from Eden, including their trials, temptations, and the birth of Cain and Abel.</p>
                        <a href="books/first_book_adam_eve.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Second Book of Adam and Eve</h2>
                        <p>Continuation of the Adam and Eve narrative, covering the patriarchs who lived before the Flood.</p>
                        <a href="books/second_book_adam_eve.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Book of the Secrets of Enoch</h2>
                        <p>The mystical journey of Enoch through the heavens and his revelations about divine mysteries.</p>
                        <a href="books/secrets_enoch.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Psalms of Solomon</h2>
                        <p>A collection of eighteen psalms attributed to King Solomon, reflecting on righteousness and divine judgment.</p>
                        <a href="books/psalms_solomon.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Odes of Solomon</h2>
                        <p>Forty-two mystical odes expressing deep spiritual truths and early Christian thought.</p>
                        <a href="books/odes_solomon.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Letter of Aristeas</h2>
                        <p>The account of how the Hebrew scriptures were translated into Greek (the Septuagint).</p>
                        <a href="books/letter_aristeas.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Fourth Book of Maccabees</h2>
                        <p>A philosophical discourse on the supremacy of devout reason over the passions.</p>
                        <a href="books/fourth_maccabees.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Story of Ahikar</h2>
                        <p>The tale of Ahikar, a wise counselor, and his ungrateful nephew Nadan.</p>
                        <a href="books/story_ahikar.html" class="btn">Read Now</a>
                    </div>
                    
                    <div class="book-card">
                        <h2>The Testaments of the Twelve Patriarchs</h2>
                        <p>The final words and teachings of the twelve sons of Jacob to their descendants.</p>
                        <a href="books/testaments_patriarchs.html" class="btn">Read Now</a>
                    </div>
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
    
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    improve_website()