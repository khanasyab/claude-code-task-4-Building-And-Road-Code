#!/usr/bin/env python3
"""
Complete extraction script for Building and Roads Code
Captures ALL paragraphs, sections, subsections, and headings for navigation
"""

import re
from collections import defaultdict, OrderedDict

def detect_encoding(file_path):
    """Detect file encoding"""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)

    # Check for UTF-16 BOM
    if raw_data[:2] == b'\xff\xfe' or raw_data[:2] == b'\xfe\xff':
        return 'utf-16'

    # Try different encodings
    encodings = ['utf-16', 'utf-16-le', 'utf-16-be', 'utf-8', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                lines = f.readlines()
            if len(lines) > 10 and any(len(line.strip()) > 5 for line in lines[:10]):
                return enc
        except:
            continue
    return 'utf-8'

def extract_all_content(file_path, version):
    """Extract ALL content including chapters, sections, subsections, and paragraphs"""

    encoding = detect_encoding(file_path)
    print(f"  Reading {version} file with encoding: {encoding}")

    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        lines = f.readlines()

    print(f"  Total lines: {len(lines)}")

    items = []

    # Patterns for different elements
    patterns = {
        'chapter': re.compile(r'^[\s]*CHAPTER\s+([IVXLCDM]+|[0-9]+)\s*[-–—]?\s*(.+)$', re.IGNORECASE),
        'main_section': re.compile(r'^[\s]*([A-Z])\.\s+(.+)$'),
        'main_section_dash': re.compile(r'^[\s]*([A-Z])\s*[-–—]\s*(.+)$'),
        'roman_section': re.compile(r'^[\s]*(I{1,3}|IV|V|VI{1,3}|IX|X|XI{1,3}|XIV|XV)\.\s+(.+)$'),
        'numbered_para': re.compile(r'^\s*(\d+\.\d+)\s*[-–—\.]?\s*(.+)$'),
        'lettered_sub': re.compile(r'^\s*\(([a-z]|[ivxlcdm]+)\)\s+(.+)$', re.IGNORECASE),
        'appendix': re.compile(r'^[\s]*APPENDIX\s+([IVXLCDM]+|[0-9]+)\s*[-–—]?\s*(.*)$', re.IGNORECASE),
        'annexure': re.compile(r'^[\s]*ANNEXURE\s+(.+)$', re.IGNORECASE),
    }

    current_chapter = None
    current_section = None

    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        if len(line_stripped) < 2:
            continue

        # Remove line numbers if present (format: "123→")
        line_cleaned = re.sub(r'^\s*\d+→', '', line_stripped)

        # Check for CHAPTER
        match = patterns['chapter'].match(line_cleaned)
        if match:
            chapter_num = match.group(1)
            chapter_title = match.group(2).strip()
            current_chapter = f"CHAPTER {chapter_num}"
            items.append({
                'type': 'chapter',
                'number': chapter_num,
                'title': chapter_title,
                'full_text': f"{current_chapter} - {chapter_title}",
                'version': version,
                'line': line_num,
                'chapter': current_chapter
            })
            continue

        # Check for ANNEXURE
        match = patterns['annexure'].match(line_cleaned)
        if match:
            annexure_title = match.group(1).strip()
            items.append({
                'type': 'annexure',
                'number': annexure_title,
                'title': annexure_title,
                'full_text': f"ANNEXURE {annexure_title}",
                'version': version,
                'line': line_num,
                'chapter': current_chapter
            })
            continue

        # Check for APPENDIX
        match = patterns['appendix'].match(line_cleaned)
        if match:
            appendix_num = match.group(1)
            appendix_title = match.group(2).strip() if match.group(2) else ""
            items.append({
                'type': 'appendix',
                'number': appendix_num,
                'title': appendix_title,
                'full_text': f"APPENDIX {appendix_num} {appendix_title}".strip(),
                'version': version,
                'line': line_num,
                'chapter': current_chapter
            })
            continue

        # Check for numbered paragraphs (MOST IMPORTANT - these were missing!)
        match = patterns['numbered_para'].match(line_cleaned)
        if match:
            para_num = match.group(1)
            para_text = match.group(2).strip()
            # Only add if it looks like a real paragraph (not just numbers or very short)
            if para_text and len(para_text) > 5:
                items.append({
                    'type': 'paragraph',
                    'number': para_num,
                    'title': para_text[:150],  # First 150 chars as preview
                    'full_text': f"{para_num} - {para_text[:150]}",
                    'version': version,
                    'line': line_num,
                    'chapter': current_chapter
                })
            continue

        # Check for main sections (A, B, C, etc.)
        match = patterns['main_section'].match(line_cleaned)
        if not match:
            match = patterns['main_section_dash'].match(line_cleaned)

        if match and len(line_cleaned) < 200:
            section_letter = match.group(1)
            section_title = match.group(2).strip()
            if len(section_letter) == 1 and section_letter.isupper():
                current_section = f"{section_letter}. {section_title}"
                items.append({
                    'type': 'main_section',
                    'number': section_letter,
                    'title': section_title,
                    'full_text': current_section,
                    'version': version,
                    'line': line_num,
                    'chapter': current_chapter
                })
            continue

        # Check for Roman numeral subsections
        match = patterns['roman_section'].match(line_cleaned)
        if match and len(line_cleaned) < 200:
            roman_num = match.group(1)
            subsection_title = match.group(2).strip()
            items.append({
                'type': 'roman_subsection',
                'number': roman_num,
                'title': subsection_title,
                'full_text': f"{roman_num}. {subsection_title}",
                'version': version,
                'line': line_num,
                'chapter': current_chapter
            })
            continue

        # Check for lettered subsections (a), (b), etc.
        match = patterns['lettered_sub'].match(line_cleaned)
        if match and len(line_cleaned) < 200:
            letter = match.group(1)
            sub_title = match.group(2).strip()
            items.append({
                'type': 'lettered_subsection',
                'number': letter,
                'title': sub_title,
                'full_text': f"({letter}) {sub_title}",
                'version': version,
                'line': line_num,
                'chapter': current_chapter
            })
            continue

    return items

def generate_complete_master_index(items_1989, items_1994, output_file):
    """Generate complete master index with all items from both versions"""

    # Organize by chapter and type
    def organize_by_chapter(items):
        organized = defaultdict(lambda: defaultdict(list))
        for item in items:
            chapter = item.get('chapter', 'NO_CHAPTER')
            organized[chapter][item['type']].append(item)
        return organized

    org_1989 = organize_by_chapter(items_1989)
    org_1994 = organize_by_chapter(items_1994)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("BUILDING AND ROADS CODE - COMPLETE MASTER INDEX\n")
        f.write("Complete Navigation Reference for 1989 and 1994 Versions\n")
        f.write("=" * 100 + "\n\n")
        f.write("PURPOSE: This file serves as a navigation guide to locate specific sections in the\n")
        f.write("         original 1989 and 1994 Building & Roads Code files.\n\n")
        f.write("STRUCTURE: Each entry shows:\n")
        f.write("           - Type (Chapter, Section, Paragraph, etc.)\n")
        f.write("           - Number/Identifier\n")
        f.write("           - Title/Description\n")
        f.write("           - Source Version (1989 or 1994)\n")
        f.write("           - Line number in source file\n\n")

        # Write 1989 version
        f.write("\n" + "=" * 100 + "\n")
        f.write("1989 VERSION - COMPLETE INDEX\n")
        f.write("Source File: B&R Code 1989.txt\n")
        f.write("=" * 100 + "\n\n")

        write_organized_content(f, org_1989, "1989")

        # Write 1994 version
        f.write("\n\n" + "=" * 100 + "\n")
        f.write("1994 VERSION - COMPLETE INDEX\n")
        f.write("Source File: BNR 1994.txt\n")
        f.write("=" * 100 + "\n\n")

        write_organized_content(f, org_1994, "1994")

        # Write statistics
        f.write("\n\n" + "=" * 100 + "\n")
        f.write("STATISTICS\n")
        f.write("=" * 100 + "\n\n")

        write_statistics(f, items_1989, items_1994)

def write_organized_content(f, organized, version):
    """Write organized content to file"""

    # Get all chapters in order
    chapters = sorted([ch for ch in organized.keys() if ch != 'NO_CHAPTER'])

    for chapter in chapters:
        chapter_data = organized[chapter]

        # Write chapter header
        if 'chapter' in chapter_data and chapter_data['chapter']:
            ch_item = chapter_data['chapter'][0]
            f.write("\n" + "-" * 100 + "\n")
            f.write(f"{ch_item['full_text']}\n")
            f.write(f"[Line {ch_item['line']} in {version} file]\n")
            f.write("-" * 100 + "\n\n")

        # Write main sections
        if 'main_section' in chapter_data:
            for section in sorted(chapter_data['main_section'], key=lambda x: x['number']):
                f.write(f"  {section['full_text']}\n")
                f.write(f"    [Line {section['line']}]\n\n")

        # Write paragraphs (CRITICAL - these were missing before!)
        if 'paragraph' in chapter_data:
            f.write("  Paragraphs:\n")
            for para in sorted(chapter_data['paragraph'], key=lambda x: float(x['number'])):
                f.write(f"    {para['number']}: {para['title'][:80]}...\n")
                f.write(f"      [Line {para['line']}]\n")
            f.write("\n")

        # Write roman subsections
        if 'roman_subsection' in chapter_data:
            for subsec in chapter_data['roman_subsection']:
                f.write(f"      {subsec['full_text']}\n")
                f.write(f"        [Line {subsec['line']}]\n")

        # Write lettered subsections
        if 'lettered_subsection' in chapter_data:
            for subsec in chapter_data['lettered_subsection']:
                f.write(f"        {subsec['full_text'][:100]}\n")

        # Write annexures
        if 'annexure' in chapter_data:
            for annex in chapter_data['annexure']:
                f.write(f"  {annex['full_text']}\n")
                f.write(f"    [Line {annex['line']}]\n\n")

        # Write appendices
        if 'appendix' in chapter_data:
            for append in chapter_data['appendix']:
                f.write(f"  {append['full_text']}\n")
                f.write(f"    [Line {append['line']}]\n\n")

def write_statistics(f, items_1989, items_1994):
    """Write detailed statistics"""

    def count_by_type(items):
        counts = defaultdict(int)
        for item in items:
            counts[item['type']] += 1
        return counts

    counts_1989 = count_by_type(items_1989)
    counts_1994 = count_by_type(items_1994)

    f.write("1989 VERSION:\n")
    f.write("-" * 50 + "\n")
    for item_type, count in sorted(counts_1989.items()):
        f.write(f"  {item_type}: {count}\n")
    f.write(f"  TOTAL: {len(items_1989)}\n\n")

    f.write("1994 VERSION:\n")
    f.write("-" * 50 + "\n")
    for item_type, count in sorted(counts_1994.items()):
        f.write(f"  {item_type}: {count}\n")
    f.write(f"  TOTAL: {len(items_1994)}\n\n")

    f.write(f"GRAND TOTAL: {len(items_1989) + len(items_1994)} items indexed\n")

def main():
    print("=" * 80)
    print("COMPLETE EXTRACTION - Building and Roads Code")
    print("=" * 80)

    file_1989 = "/home/user/claude-code-task-4-Building-And-Road-Code/B&R Code 1989.txt"
    file_1994 = "/home/user/claude-code-task-4-Building-And-Road-Code/BNR 1994.txt"
    output_file = "/home/user/claude-code-task-4-Building-And-Road-Code/BNR-Initial/MASTER_INDEX.txt"

    print(f"\nExtracting from 1989 file...")
    items_1989 = extract_all_content(file_1989, "1989")
    print(f"  ✓ Extracted {len(items_1989)} items from 1989 version")

    # Count paragraphs specifically
    para_1989 = [i for i in items_1989 if i['type'] == 'paragraph']
    print(f"    Including {len(para_1989)} numbered paragraphs")

    print(f"\nExtracting from 1994 file...")
    items_1994 = extract_all_content(file_1994, "1994")
    print(f"  ✓ Extracted {len(items_1994)} items from 1994 version")

    # Count paragraphs specifically
    para_1994 = [i for i in items_1994 if i['type'] == 'paragraph']
    print(f"    Including {len(para_1994)} numbered paragraphs")

    print(f"\nGenerating complete master index...")
    generate_complete_master_index(items_1989, items_1994, output_file)

    print(f"\n✓ COMPLETE!")
    print(f"  Output: {output_file}")
    print(f"  Total items indexed: {len(items_1989) + len(items_1994)}")
    print(f"  1989 paragraphs: {len(para_1989)}")
    print(f"  1994 paragraphs: {len(para_1994)}")
    print(f"  Total paragraphs: {len(para_1989) + len(para_1994)}")

if __name__ == "__main__":
    main()
