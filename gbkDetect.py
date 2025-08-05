#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import chardet
import codecs
from pathlib import Path

def detect_encoding(file_path):
    """
    Detect the encoding of a file
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def is_chinese_character(char):
    """
    Check if a character is Chinese
    """
    return '\u4e00' <= char <= '\u9fff'

def has_chinese_text(text):
    """
    Check if text contains Chinese characters
    """
    for char in text:
        if is_chinese_character(char):
            return True
    return False

def find_chinese_garbled_chars(text):
    """
    Find potentially garbled Chinese characters
    """
    garbled_chars = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for i, char in enumerate(line):
            # Check for common garbled patterns in Chinese text
            if is_chinese_character(char):
                # Check if surrounding characters look like garbled text
                # This is a simple heuristic - looks for non-Chinese characters in Chinese text
                if i > 0 and i < len(line) - 1:
                    prev_char = line[i-1]
                    next_char = line[i+1]
                    
                    # If Chinese character is surrounded by non-Chinese characters
                    # it might be correctly encoded
                    if not is_chinese_character(prev_char) and not is_chinese_character(next_char):
                        # This is a simple check - in real cases, more sophisticated checks needed
                        pass
                        
            # Look for typical garbled patterns like "锟斤拷", "锘", etc.
            if '\ufffd' in char or (char.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore') != char and 
                                    len(char.encode('utf-8', errors='ignore')) > 1):
                garbled_chars.append((line_num, i, char))
    
    return garbled_chars

def convert_to_gbk(file_path):
    """
    Convert file encoding to GBK
    """
    try:
        # Read with detected encoding
        encoding = detect_encoding(file_path)
        if encoding is None:
            print(f"Cannot detect encoding for {file_path}")
            return False
            
        with codecs.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        # Write with GBK encoding
        with codecs.open(file_path, 'w', encoding='gbk', errors='ignore') as f:
            f.write(content)
            
        print(f"Converted {file_path} from {encoding} to GBK")
        return True
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return False

def check_gbk_file_for_garbled_text(file_path):
    """
    Check a GBK file for garbled Chinese text
    """
    try:
        with codecs.open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
        
        # Check for common garbled text patterns
        garbled_patterns = ['锟斤拷', '锘', '', '锘']
        found_garbled = False
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in garbled_patterns:
                if pattern in line:
                    found_garbled = True
                    # Highlight garbled text in red (ANSI escape codes)
                    highlighted_line = line.replace(pattern, f"\033[31m{pattern}\033[0m")
                    print(f"\033[31mGarbled text found\033[0m in {file_path} at line {i}: {highlighted_line}")
        
        if not found_garbled and has_chinese_text(content):
            # Try to detect other forms of garbled text
            # This is a simplified check - real implementation might need more sophisticated approach
            pass
            
        return found_garbled
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def process_cpp_files(directory):
    """
    Process all .cpp files in the directory
    """
    cpp_files = list(Path(directory).rglob("*.cpp"))
    
    print(f"Found {len(cpp_files)} .cpp files")
    
    for file_path in cpp_files:
        print(f"\nProcessing: {file_path}")
        
        # Detect encoding
        detected_encoding = detect_encoding(file_path)
        print(f"Detected encoding: {detected_encoding}")
        
        if detected_encoding is None:
            print(f"Cannot determine encoding for {file_path}")
            continue
            
        # Normalize encoding name
        detected_encoding = detected_encoding.lower()
        
        if detected_encoding.startswith('gb') or detected_encoding.startswith('windows'):
            # File is already in GBK or similar encoding (like GB2312, GB18030, Windows-1252)
            print(f"{file_path} is already in GBK-compatible encoding")
            
            # Check for garbled Chinese text
            has_garbled = check_gbk_file_for_garbled_text(file_path)
            if has_garbled:
                print(f"\033[31mWarning: Found garbled text in {file_path}\033[0m")
            else:
                print(f"No obvious garbled text found in {file_path}")
        else:
            # Convert to GBK
            print(f"Converting {file_path} from {detected_encoding} to GBK...")
            if convert_to_gbk(file_path):
                print(f"Successfully converted {file_path}")
            else:
                print(f"Failed to convert {file_path}")

if __name__ == "__main__":
    # Get directory from user input or use current directory
    directory = input("Enter directory path (or press Enter for current directory): ").strip()
    if not directory:
        directory = "."
    
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        exit(1)
    
    process_cpp_files(directory)
    print("\nProcessing complete.")