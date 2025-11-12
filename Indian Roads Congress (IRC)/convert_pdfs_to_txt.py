#!/usr/bin/env python3
"""
PDF to Text Converter
Converts all PDF files in current directory to .txt files
Output: Same directory as PDFs
"""

import os
from pathlib import Path

# Try to import PyMuPDF
try:
    import fitz  # PyMuPDF
except ImportError:
    print("=" * 70)
    print("❌ ERROR: PyMuPDF not installed")
    print("=" * 70)
    print()
    print("Please install PyMuPDF first:")
    print("  python -m pip install PyMuPDF")
    print()
    print("Or run the install_pymupdf.py script if available.")
    print()
    input("Press ENTER to exit...")
    exit(1)

print("=" * 70)
print("📄 PDF to Text Converter")
print("=" * 70)
print()

# Get current directory
current_dir = Path(__file__).parent
print(f"📁 Directory: {current_dir}")
print()

# Find all PDF files
pdf_files = list(current_dir.glob("*.pdf"))

if not pdf_files:
    print("⚠️  No PDF files found in this directory!")
    print()
    input("Press ENTER to exit...")
    exit(0)

print(f"✅ Found {len(pdf_files)} PDF files")
print()

# Ask for confirmation
print("This will create .txt files for each PDF in the same directory.")
confirm = input(f"Convert {len(pdf_files)} PDFs to text? (y/n): ").strip().lower()

if confirm != 'y':
    print("❌ Cancelled.")
    exit(0)

print()
print("=" * 70)
print("🔄 Starting conversion...")
print("=" * 70)
print()

# Counters
success_count = 0
skip_count = 0
error_count = 0

# Convert each PDF
for idx, pdf_path in enumerate(pdf_files, 1):
    # Create text file path
    txt_path = pdf_path.with_suffix('.txt')

    # Display progress
    print(f"[{idx}/{len(pdf_files)}] {pdf_path.name}")

    # Check if text file already exists
    if txt_path.exists():
        print(f"  ⏭️  Text file already exists, skipping")
        skip_count += 1
        continue

    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        page_count = len(doc)

        # Extract text from all pages
        full_text = []
        full_text.append(f"{'='*70}")
        full_text.append(f"SOURCE PDF: {pdf_path.name}")
        full_text.append(f"TOTAL PAGES: {page_count}")
        full_text.append(f"{'='*70}")
        full_text.append("\n")

        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():  # Only add non-empty pages
                full_text.append(f"{'='*70}")
                full_text.append(f"PAGE {page_num} of {page_count}")
                full_text.append(f"{'='*70}")
                full_text.append(text)
                full_text.append("\n")

        doc.close()

        # Save as text file
        combined_text = "\n".join(full_text)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(combined_text)

        # Get file sizes
        txt_size_kb = txt_path.stat().st_size / 1024

        print(f"  ✅ Converted: {page_count} pages → {txt_size_kb:.1f} KB")
        success_count += 1

    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        error_count += 1

print()
print("=" * 70)
print("✅ CONVERSION COMPLETE!")
print("=" * 70)
print()
print(f"📊 Summary:")
print(f"  • Total PDFs found: {len(pdf_files)}")
print(f"  • Successfully converted: {success_count}")
print(f"  • Already existed (skipped): {skip_count}")
print(f"  • Errors: {error_count}")
print(f"  • Output directory: {current_dir}")
print()
print("=" * 70)
print()
input("Press ENTER to exit...")
