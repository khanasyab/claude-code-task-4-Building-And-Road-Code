#!/usr/bin/env python3
"""
Test script to download sample PDFs from UK, USA, and India
"""

import requests
import os
from pathlib import Path

def download_file(url, save_path, description):
    """Download a file with progress indication"""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print(f"Save to: {save_path}")
    print('='*80)

    try:
        # Set headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Make request
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        print(f"File size: {total_size / (1024*1024):.2f} MB")

        # Download
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}% ({downloaded/(1024*1024):.2f} MB)", end='')

        print(f"\n✅ SUCCESS: Downloaded to {save_path}")
        print(f"   File size: {os.path.getsize(save_path) / 1024:.2f} KB")
        return True

    except requests.exceptions.RequestException as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("PDF DOWNLOAD TEST - UK, USA, INDIA")
    print("="*80)

    base_dir = "/home/user/claude-code-task-4-Building-And-Road-Code/Test-Downloads"

    # Test cases
    tests = [
        # UK TESTS
        {
            'url': 'https://assets.publishing.service.gov.uk/media/5a74b70ce5274a59fa48706c/BR_PDF_AD_A_2004.pdf',
            'save_path': f'{base_dir}/UK-Test/Approved-Document-A-Structure.pdf',
            'description': 'UK - Building Regulations Approved Document A (Structure)'
        },
        {
            'url': 'https://www.standardsforhighways.co.uk/dmrb/vol/0/pdfs/gd_100.pdf',
            'save_path': f'{base_dir}/UK-Test/DMRB-GD-100-Introduction.pdf',
            'description': 'UK - DMRB GD 100 (Introduction to DMRB)'
        },

        # USA TESTS
        {
            'url': 'https://www.osha.gov/sites/default/files/publications/osha2207.pdf',
            'save_path': f'{base_dir}/USA-Test/OSHA-Construction-Safety.pdf',
            'description': 'USA - OSHA 29 CFR 1926 Construction Safety'
        },
        {
            'url': 'https://www.acquisition.gov/sites/default/files/page_file_uploads/FAR%202024-05%20Edition.pdf',
            'save_path': f'{base_dir}/USA-Test/FAR-2024-Complete.pdf',
            'description': 'USA - Federal Acquisition Regulation (FAR) 2024'
        },
        {
            'url': 'https://mutcd.fhwa.dot.gov/pdfs/2009r1r2/mutcd2009r1r2edition.pdf',
            'save_path': f'{base_dir}/USA-Test/MUTCD-2009-Complete.pdf',
            'description': 'USA - MUTCD 2009 Edition (Traffic Control)'
        },

        # INDIA TESTS
        {
            'url': 'https://doe.gov.in/sites/default/files/GFR2017_0.pdf',
            'save_path': f'{base_dir}/India-Test/GFR-2017-General-Financial-Rules.pdf',
            'description': 'INDIA - General Financial Rules 2017'
        },
    ]

    # Run tests
    results = []
    for test in tests:
        success = download_file(test['url'], test['save_path'], test['description'])
        results.append({
            'description': test['description'],
            'success': success,
            'path': test['save_path'] if success else None
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
        if result['path']:
            size = os.path.getsize(result['path']) / 1024
            print(f"   Size: {size:.2f} KB")
            print(f"   Path: {result['path']}")

    print("\n" + "="*80)

    if success_count > 0:
        print(f"✅ {success_count} files downloaded successfully!")
        print(f"   Check folder: {base_dir}")
    else:
        print("❌ No files downloaded. Check network connection and URLs.")

    print("="*80 + "\n")

if __name__ == "__main__":
    main()
