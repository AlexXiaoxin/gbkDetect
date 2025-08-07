#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import chardet
import codecs
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

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

def find_chinese_garbled_chars(text, encoding):
    """
    Find potentially garbled Chinese characters with improved detection
    """
    garbled_chars = []
    lines = text.split('\n')
    
    # Common garbled patterns
    garbled_patterns = [
        '锟斤拷', '锘', '烫烫烫', '屯屯屯',
        '��',  # Replacement character
        '\ufffd',  # Unicode replacement character
        '?',  # Common replacement when decoding fails
    ]
    
    # Statistical analysis of Chinese character distribution
    chinese_chars_in_line = []
    for line_num, line in enumerate(lines, 1):
        chinese_count = 0
        for i, char in enumerate(line):
            if is_chinese_character(char):
                chinese_count += 1
                
                # Check for invalid encoding sequences
                try:
                    encoded = char.encode(encoding, errors='strict')
                    decoded = encoded.decode(encoding, errors='strict')
                    if decoded != char:
                        garbled_chars.append((line_num, i, char, "ENCODING_MISMATCH"))
                except UnicodeError:
                    garbled_chars.append((line_num, i, char, "INVALID_ENCODING"))
                
                # Check for common garbled patterns
                for pattern in garbled_patterns:
                    if pattern in line[i:i+len(pattern)]:
                        garbled_chars.append((line_num, i, char, "COMMON_PATTERN"))
            
            # Check for isolated Chinese characters (potential encoding issues)
            if is_chinese_character(char):
                context = line[max(0,i-2):min(len(line),i+3)]
                chinese_in_context = sum(1 for c in context if is_chinese_character(c))
                if chinese_in_context < 2:  # Isolated Chinese character
                    garbled_chars.append((line_num, i, char, "ISOLATED_CHARACTER"))
        
        chinese_chars_in_line.append((line_num, chinese_count))
    
    return garbled_chars, chinese_chars_in_line

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
    Process all .cpp files in the directory with enhanced detection
    """
    cpp_files = list(Path(directory).rglob("*.cpp"))
    
    print(f"Found {len(cpp_files)} .cpp files")
    
    for file_path in cpp_files:
        print(f"\nProcessing: {file_path}")
        
        # Detect encoding with confidence threshold
        detected_encoding = detect_encoding(file_path)
        print(f"Detected encoding: {detected_encoding}")
        
        if detected_encoding is None:
            print(f"Cannot determine encoding for {file_path}")
            continue
            
        # Normalize encoding name
        detected_encoding = detected_encoding.lower()
        
        try:
            # Read file with detected encoding
            with open(file_path, 'rb') as f:
                raw_content = f.read()
            
            # Decode content
            try:
                content = raw_content.decode(detected_encoding)
            except UnicodeDecodeError:
                # Try common fallback encodings
                for enc in ['utf-8', 'gbk', 'gb18030', 'big5']:
                    try:
                        content = raw_content.decode(enc)
                        detected_encoding = enc
                        print(f"Used fallback encoding: {enc}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"Failed to decode {file_path} with any encoding")
                    continue
            
            # Enhanced garbled character detection
            garbled_chars, chinese_stats = find_chinese_garbled_chars(content, detected_encoding)
            total_chinese = sum(count for _, count in chinese_stats)
            
            print(f"\nFile: {file_path}")
            print(f"Encoding: {detected_encoding.upper()}")
            print(f"Total Chinese characters: {total_chinese}")
            
            if garbled_chars:
                print("\n\033[31mGARBLED TEXT DETECTED:\033[0m")
                for line_num, pos, char, reason in garbled_chars:
                    print(f"Line {line_num}, Pos {pos}: {char} (Reason: {reason})")
                
                # Provide conversion suggestions
                print("\n\033[33mSUGGESTED FIXES:\033[0m")
                if detected_encoding.startswith('gb'):
                    print("1. Try converting to UTF-8:")
                    print(f"   iconv -f {detected_encoding} -t utf-8 {file_path} > {file_path}.utf8")
                else:
                    print("1. Try converting to GBK:")
                    print(f"   iconv -f {detected_encoding} -t gbk {file_path} > {file_path}.gbk")
                
                print("2. Manually check the reported positions")
                print("3. Verify the original file encoding")
            else:
                print("\n\033[32mNo garbled Chinese text detected\033[0m")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    # Automatically process current directory
    directory = "."
    process_cpp_files(directory)
    print("\nProcessing complete.")