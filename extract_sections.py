#!/usr/bin/env python3
"""
Script to extract all sections, subsections, and headings from
Building and Roads Code text files (1989 and 1994 versions)
"""

import re
from collections import defaultdict

def detect_encoding(file_path):
    """Detect file encoding"""
    import chardet

    # Try reading first 10000 bytes to detect encoding
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)

    # Check for UTF-16 BOM
    if raw_data[:2] == b'\xff\xfe' or raw_data[:2] == b'\xfe\xff':
        return 'utf-16'

    # Use chardet for detection
    try:
        result = chardet.detect(raw_data)
        if result['confidence'] > 0.7:
            return result['encoding']
    except:
        pass

    # Default to utf-8
    return 'utf-8'

def extract_headings(file_path, version):
    """Extract all headings and structure from a text file"""

    headings = []

    # Detect encoding
    try:
        encoding = detect_encoding(file_path)
        print(f"  Detected encoding: {encoding}")
    except:
        # If chardet is not available, try different encodings manually
        encodings = ['utf-16', 'utf-16-le', 'utf-16-be', 'utf-8', 'latin-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    lines = f.readlines()
                if len(lines) > 10 and any(len(line.strip()) > 5 for line in lines[:10]):
                    encoding = enc
                    print(f"  Using encoding: {encoding}")
                    break
            except:
                continue
        else:
            encoding = 'utf-8'
            print(f"  Fallback to encoding: {encoding}")

    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        lines = f.readlines()

    # Patterns to match different heading levels
    patterns = {
        'chapter': re.compile(r'^[\s]*CHAPTER\s+([IVXLCDM]+|[0-9]+)\s*[-–—]?\s*(.+)$', re.IGNORECASE),
        'main_section': re.compile(r'^[\s]*([A-Z])\s*[-–—\.]\s*(.+)$'),
        'roman_section': re.compile(r'^[\s]*(I{1,3}|IV|V|VI{1,3}|IX|X)\s*[-–—\.]\s*(.+)$'),
        'numbered_para': re.compile(r'^[\s]*([0-9]+\.[0-9]+)\s*[-–—\.]\s*(.+)$'),
        'subsection': re.compile(r'^[\s]*\(([a-z]|[0-9]+)\)\s*(.+)$'),
    }

    current_chapter = None
    current_section = None

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip empty lines and very short lines
        if len(line_stripped) < 3:
            continue

        # Remove line numbers if present (format: "123→")
        line_cleaned = re.sub(r'^\s*\d+→', '', line_stripped)

        # Check for CHAPTER
        match = patterns['chapter'].match(line_cleaned)
        if match:
            chapter_num = match.group(1)
            chapter_title = match.group(2).strip()
            current_chapter = f"CHAPTER {chapter_num} - {chapter_title}"
            headings.append({
                'type': 'chapter',
                'number': chapter_num,
                'title': chapter_title,
                'full_text': current_chapter,
                'version': version,
                'line_num': i+1
            })
            continue

        # Check for main sections (A, B, C, etc.)
        match = patterns['main_section'].match(line_cleaned)
        if match and len(line_cleaned) < 100:  # Avoid matching long sentences
            section_letter = match.group(1)
            section_title = match.group(2).strip()
            # Only if it's a single uppercase letter followed by title
            if len(section_letter) == 1 and section_letter.isupper():
                current_section = f"{section_letter}. {section_title}"
                headings.append({
                    'type': 'main_section',
                    'number': section_letter,
                    'title': section_title,
                    'full_text': current_section,
                    'parent_chapter': current_chapter,
                    'version': version,
                    'line_num': i+1
                })
                continue

        # Check for Roman numeral subsections (I, II, III, etc.)
        match = patterns['roman_section'].match(line_cleaned)
        if match and len(line_cleaned) < 100:
            roman_num = match.group(1)
            subsection_title = match.group(2).strip()
            headings.append({
                'type': 'roman_subsection',
                'number': roman_num,
                'title': subsection_title,
                'full_text': f"{roman_num}. {subsection_title}",
                'parent_chapter': current_chapter,
                'parent_section': current_section,
                'version': version,
                'line_num': i+1
            })
            continue

        # Check for numbered paragraphs (1.1, 1.2, etc.)
        match = patterns['numbered_para'].match(line_cleaned)
        if match:
            para_num = match.group(1)
            para_title = match.group(2).strip()
            # Only add if there's a meaningful title (not just continuation text)
            if para_title and not para_title.startswith('The '):
                headings.append({
                    'type': 'numbered_paragraph',
                    'number': para_num,
                    'title': para_title[:100],  # Limit title length
                    'full_text': f"{para_num} - {para_title[:100]}",
                    'parent_chapter': current_chapter,
                    'version': version,
                    'line_num': i+1
                })
            continue

        # Check for lettered subsections (a), (b), etc.
        match = patterns['subsection'].match(line_cleaned)
        if match and len(line_cleaned) < 100:
            subsection_letter = match.group(1)
            subsection_title = match.group(2).strip()
            headings.append({
                'type': 'lettered_subsection',
                'number': subsection_letter,
                'title': subsection_title,
                'full_text': f"({subsection_letter}) {subsection_title}",
                'parent_chapter': current_chapter,
                'version': version,
                'line_num': i+1
            })
            continue

    return headings

def generate_master_index(headings_1989, headings_1994, output_file):
    """Generate master index file with all headings from both versions"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("BUILDING AND ROADS CODE - MASTER INDEX\n")
        f.write("Complete Directory of Sections, Subsections, and Headings\n")
        f.write("=" * 80 + "\n\n")

        # Write 1989 version headings
        f.write("\n" + "=" * 80 + "\n")
        f.write("1989 VERSION\n")
        f.write("=" * 80 + "\n\n")

        current_chapter = None
        for heading in headings_1989:
            if heading['type'] == 'chapter':
                f.write("\n" + "-" * 80 + "\n")
                f.write(f"{heading['full_text']}\n")
                f.write("-" * 80 + "\n")
                current_chapter = heading['full_text']
            elif heading['type'] == 'main_section':
                f.write(f"\n  {heading['full_text']}\n")
            elif heading['type'] == 'roman_subsection':
                f.write(f"    {heading['full_text']}\n")
            elif heading['type'] == 'numbered_paragraph':
                f.write(f"      {heading['full_text']}\n")
            elif heading['type'] == 'lettered_subsection':
                f.write(f"        {heading['full_text']}\n")

        # Write 1994 version headings
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("1994 VERSION\n")
        f.write("=" * 80 + "\n\n")

        current_chapter = None
        for heading in headings_1994:
            if heading['type'] == 'chapter':
                f.write("\n" + "-" * 80 + "\n")
                f.write(f"{heading['full_text']}\n")
                f.write("-" * 80 + "\n")
                current_chapter = heading['full_text']
            elif heading['type'] == 'main_section':
                f.write(f"\n  {heading['full_text']}\n")
            elif heading['type'] == 'roman_subsection':
                f.write(f"    {heading['full_text']}\n")
            elif heading['type'] == 'numbered_paragraph':
                f.write(f"      {heading['full_text']}\n")
            elif heading['type'] == 'lettered_subsection':
                f.write(f"        {heading['full_text']}\n")

        # Write summary statistics
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")

        # Count by type for each version
        for version, headings in [("1989", headings_1989), ("1994", headings_1994)]:
            f.write(f"\n{version} Version:\n")
            f.write("-" * 40 + "\n")
            type_counts = defaultdict(int)
            for h in headings:
                type_counts[h['type']] += 1
            for htype, count in sorted(type_counts.items()):
                f.write(f"  {htype}: {count}\n")
            f.write(f"  Total headings: {len(headings)}\n")

def main():
    print("Extracting headings from Building and Roads Code files...")

    file_1989 = "/home/user/claude-code-task-4-Building-And-Road-Code/B&R Code 1989.txt"
    file_1994 = "/home/user/claude-code-task-4-Building-And-Road-Code/BNR 1994.txt"
    output_file = "/home/user/claude-code-task-4-Building-And-Road-Code/BNR-Initial/MASTER_INDEX.txt"

    print(f"Reading {file_1989}...")
    headings_1989 = extract_headings(file_1989, "1989")
    print(f"Found {len(headings_1989)} headings in 1989 version")

    print(f"\nReading {file_1994}...")
    headings_1994 = extract_headings(file_1994, "1994")
    print(f"Found {len(headings_1994)} headings in 1994 version")

    print(f"\nGenerating master index at {output_file}...")
    generate_master_index(headings_1989, headings_1994, output_file)

    print("\n✓ Master index generated successfully!")
    print(f"  Output: {output_file}")
    print(f"  Total headings: {len(headings_1989) + len(headings_1994)}")

if __name__ == "__main__":
    main()
