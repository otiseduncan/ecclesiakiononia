#!/usr/bin/env python3
"""
Simple HTTP server to preview The Forgotten Books of Eden website locally.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_website():
    """Serve the website locally for preview."""
    website_dir = Path('/home/otis/Documents/projects/christianresearch/website')
    
    if not website_dir.exists():
        print("❌ Website directory not found!")
        return
    
    # Change to website directory
    os.chdir(website_dir)
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Serving The Forgotten Books of Eden at http://localhost:{PORT}")
            print(f"📁 Serving from: {website_dir}")
            print(f"📚 Available books:")
            
            books_dir = website_dir / 'books'
            if books_dir.exists():
                for book_file in sorted(books_dir.glob('*.html')):
                    book_name = book_file.stem.replace('_', ' ').title()
                    print(f"   📖 {book_name}")
            
            print(f"\n🚀 Open http://localhost:{PORT} in your browser")
            print("Press Ctrl+C to stop the server")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}')
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    serve_website()