#!/usr/bin/env python3
"""
Test script to scrape HTML pages and extract text content
"""

import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path

def scrape_and_extract(url, save_html_path, save_text_path, description):
    """Scrape HTML page and extract text content"""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print('='*80)

    try:
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        # Make request
        print("Fetching page...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"✓ Fetched: {len(response.content)} bytes")

        # Save HTML
        os.makedirs(os.path.dirname(save_html_path), exist_ok=True)
        with open(save_html_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ Saved HTML: {save_html_path}")

        # Parse with BeautifulSoup
        print("Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)

        # Save text
        os.makedirs(os.path.dirname(save_text_path), exist_ok=True)
        with open(save_text_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        print(f"✓ Saved Text: {save_text_path}")
        print(f"✓ Extracted {len(clean_text)} characters")
        print(f"✓ {len(lines)} lines of text")

        # Show preview
        preview_lines = clean_text.split('\n')[:10]
        print("\nPreview (first 10 lines):")
        print("-" * 80)
        for line in preview_lines:
            print(line[:75] + '...' if len(line) > 75 else line)
        print("-" * 80)

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("HTML SCRAPING & TEXT EXTRACTION TEST")
    print("="*80)

    base_dir = "/home/user/claude-code-task-4-Building-And-Road-Code/Test-Downloads/HTML-Scraping-Test"

    # Test cases
    tests = [
        # USA ICC Codes (view only)
        {
            'url': 'https://codes.iccsafe.org/content/IBC2024P1/chapter-1-scope-and-administration',
            'html_path': f'{base_dir}/USA-IBC-2024-Chapter-1.html',
            'text_path': f'{base_dir}/USA-IBC-2024-Chapter-1.txt',
            'description': 'USA - IBC 2024 Chapter 1 (Scope and Administration)'
        },
        # OSHA HTML version
        {
            'url': 'https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.451',
            'html_path': f'{base_dir}/USA-OSHA-1926-451-Scaffolds.html',
            'text_path': f'{base_dir}/USA-OSHA-1926-451-Scaffolds.txt',
            'description': 'USA - OSHA 1926.451 (Scaffolds)'
        },
        # UK Legislation
        {
            'url': 'https://www.legislation.gov.uk/uksi/2015/51/contents/made',
            'html_path': f'{base_dir}/UK-CDM-2015-Regulations.html',
            'text_path': f'{base_dir}/UK-CDM-2015-Regulations.txt',
            'description': 'UK - CDM Regulations 2015 (Construction Safety)'
        },
    ]

    # Run tests
    results = []
    for test in tests:
        success = scrape_and_extract(
            test['url'],
            test['html_path'],
            test['text_path'],
            test['description']
        )
        results.append({
            'description': test['description'],
            'success': success,
            'html_path': test['html_path'] if success else None,
            'text_path': test['text_path'] if success else None
        })

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)

    print(f"\nResults: {success_count}/{total_count} successful")
    print("\nDetailed Results:")

    for i, result in enumerate(results, 1):
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n{i}. {status}")
        print(f"   {result['description']}")
        if result['html_path'] and os.path.exists(result['html_path']):
            html_size = os.path.getsize(result['html_path']) / 1024
            text_size = os.path.getsize(result['text_path']) / 1024
            print(f"   HTML: {html_size:.2f} KB - {result['html_path']}")
            print(f"   Text: {text_size:.2f} KB - {result['text_path']}")

    print("\n" + "="*80)

    if success_count > 0:
        print(f"✅ {success_count} pages scraped successfully!")
        print(f"   Check folder: {base_dir}")
    else:
        print("❌ No pages scraped. Check network connection and URLs.")

    print("="*80 + "\n")

if __name__ == "__main__":
    main()
