#!/usr/bin/env python3
"""
Simple script to add the Adam and Eve books using the table of contents info.
"""

import os
from bs4 import BeautifulSoup
from pathlib import Path

def add_adam_eve_books():
    """Add Adam and Eve books based on file ranges from table of contents."""
    source_dir = Path('/home/otis/Documents/projects/christianresearch/sacred-texts')
    output_dir = Path('/home/otis/Documents/projects/christianresearch/website')
    
    # Based on the table of contents we saw earlier:
    # First Book of Adam and Eve starts at page 3 (around fbe005.htm)
    # Second Book of Adam and Eve starts at page 60 (around fbe085.htm) 
    # Secrets of Enoch starts at page 81 (around fbe106.htm)
    
    # Let's use file number ranges
    first_adam_files = [f"fbe{str(i).zfill(3)}.htm" for i in range(5, 85)]  # fbe005 to fbe084
    second_adam_files = [f"fbe{str(i).zfill(3)}.htm" for i in range(85, 106)]  # fbe085 to fbe105
    
    # Filter to only existing files
    all_files = [f for f in os.listdir(source_dir) if f.endswith('.htm')]
    
    first_adam_files = [f for f in first_adam_files if f in all_files]
    second_adam_files = [f for f in second_adam_files if f in all_files]
    
    print(f"First Book files: {len(first_adam_files)} files ({first_adam_files[0]} to {first_adam_files[-1]})")
    print(f"Second Book files: {len(second_adam_files)} files ({second_adam_files[0]} to {second_adam_files[-1]})")
    
    # Create the books
    create_book("first_book_adam_eve", "The First Book of Adam and Eve", first_adam_files, source_dir, output_dir)
    create_book("second_book_adam_eve", "The Second Book of Adam and Eve", second_adam_files, source_dir, output_dir)
    
    print("✅ Added Adam and Eve books to the website!")

def create_book(book_id, book_title, files, source_dir, output_dir):
    """Create a book page."""
    chapters = []
    
    for filename in files:
        try:
            with open(source_dir / filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title, clean_html = extract_clean_content(content)
            
            if title and clean_html.strip():
                chapters.append({
                    'filename': filename,
                    'title': title,
                    'content': clean_html
                })
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    if chapters:
        create_book_html(book_id, book_title, chapters, output_dir)
        print(f"✅ Created {book_title} with {len(chapters)} chapters")
    else:
        print(f"❌ No chapters found for {book_title}")

def extract_clean_content(html_content):
    """Extract clean content from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get title from meta tag
    title = ""
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        content_val = og_title.get('content')
        if isinstance(content_val, list):
            content_val = content_val[0] if content_val else ""
        title = str(content_val).replace(' | Sacred Texts Archive', '')
    
    # Find body content
    body = soup.find('body')
    if not body:
        return "", ""
    
    # Remove navigation elements
    for element in body.find_all(['script', 'nav', 'style']):
        element.decompose()
    
    # Remove navigation centers and hrs
    for element in body.find_all(['center', 'hr']):
        if element.name == 'center':
            # Keep centers with actual content
            has_content = (element.find('h1') or element.find('h2') or element.find('h3') or 
                          (element.find('p') and len(element.get_text().strip()) > 50))
            if not has_content:
                element.decompose()
        else:
            element.decompose()
    
    # Extract main content
    content_html = ""
    for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote', 'div']):
        text = element.get_text().strip()
        if text and len(text) > 10:  # Only include substantial content
            # Clean up the element
            for sub in element.find_all(['a']):
                if 'href' in sub.attrs:
                    del sub.attrs['href']
            content_html += str(element) + "\n"
    
    return title, content_html

def create_book_html(book_id, book_title, chapters, output_dir):
    """Create the HTML page for a book."""
    
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
    
    # Add chapter navigation
    for i, chapter in enumerate(chapters[:20]):  # Limit to first 20 for dropdown
        short_title = chapter['title'].replace('The Forgotten Books of Eden: ', '').replace(book_title + ': ', '')
        if len(short_title) > 50:
            short_title = short_title[:47] + "..."
        html_content += f'<option value="#{chapter["filename"]}">{short_title}</option>'
    
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
                    </div>
                    <hr style="margin: 3rem 0; border: none; border-top: 1px solid #eee;">'''
    
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

if __name__ == "__main__":
    add_adam_eve_books()