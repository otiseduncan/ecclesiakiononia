#!/usr/bin/env python3
"""
Parse the Sacred Texts Archive HTML files to extract book structure and metadata.
"""

import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
import json

def extract_book_info(html_content, filename):
    """Extract title, chapter info, and content from HTML file."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title from meta tags or page title
    title = None
    
    # Try og:title first
    og_title = soup.find('meta', property='og:title')
    if og_title:
        title = og_title.get('content', '').replace(' | Sacred Texts Archive', '')
    
    # Fall back to title tag
    if not title:
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().replace(' | Sacred Texts Archive', '')
    
    # Extract main content (remove navigation and metadata)
    content_div = soup.find('body')
    if content_div:
        # Remove navigation elements
        for nav in content_div.find_all(['nav', 'center']):
            # Keep center tags that contain main content
            if nav.name == 'center' and (nav.find('h1') or nav.find('h2') or nav.find('p')):
                continue
            nav.decompose()
        
        # Remove script tags and ads
        for script in content_div.find_all(['script', 'img']):
            script.decompose()
        
        # Get clean text content
        content = content_div.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
    else:
        content = ""
    
    return {
        'filename': filename,
        'title': title or filename,
        'content': content,
        'html': str(soup) if soup else html_content
    }

def analyze_book_structure():
    """Analyze all HTML files to determine book structure."""
    sacred_texts_dir = Path('/home/otis/Documents/projects/christianresearch/sacred-texts')
    
    books = {}
    file_info = []
    
    # Process all HTML files
    html_files = sorted([f for f in os.listdir(sacred_texts_dir) if f.endswith('.htm')])
    
    for filename in html_files:
        filepath = sacred_texts_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            book_info = extract_book_info(content, filename)
            file_info.append(book_info)
            
            print(f"Processed: {filename} - {book_info['title'][:60]}...")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Group files by book based on titles and content
    # The main book appears to be "The Forgotten Books of Eden"
    main_book = {
        'title': 'The Forgotten Books of Eden',
        'editor': 'Rutherford H. Platt, Jr.',
        'year': 1926,
        'files': []
    }
    
    # Categorize files
    for info in file_info:
        if 'errata' in info['filename'].lower():
            continue  # Skip errata
        
        main_book['files'].append(info)
    
    # Save the analysis
    analysis_file = sacred_texts_dir.parent / 'book_analysis.json'
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump({
            'main_book': main_book,
            'total_files': len(file_info),
            'file_details': file_info
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis complete!")
    print(f"Total files processed: {len(file_info)}")
    print(f"Main book: {main_book['title']}")
    print(f"Analysis saved to: {analysis_file}")
    
    return main_book, file_info

if __name__ == "__main__":
    analyze_book_structure()