#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import chardet
import codecs
from pathlib import Path

def detect_encoding(file_path):
    """
    检测文件编码
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def is_chinese_character(char):
    """
    检查字符是否为中文字符
    """
    return '\u4e00' <= char <= '\u9fff'

def has_chinese_text(text):
    """
    检查文本是否包含中文字符
    """
    for char in text:
        if is_chinese_character(char):
            return True
    return False

def find_chinese_garbled_chars(text):
    """
    查找可能的乱码中文字符
    """
    garbled_chars = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for i, char in enumerate(line):
            # 检查中文文本中的乱码模式
            if is_chinese_character(char):
                # 这里可以添加更复杂的乱码检测逻辑
                pass
                        
            # 查找典型的乱码模式如 "锟斤拷", "锘" 等
            if '\ufffd' in char or (char.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore') != char and 
                                    len(char.encode('utf-8', errors='ignore')) > 1):
                garbled_chars.append((line_num, i, char))
    
    return garbled_chars

def convert_to_gbk(file_path):
    """
    将文件编码转换为GBK
    """
    try:
        # 读取文件并检测编码
        encoding = detect_encoding(file_path)
        if encoding is None:
            print(f"无法检测 {file_path} 的编码")
            return False
            
        with codecs.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        # 用GBK编码写入文件
        with codecs.open(file_path, 'w', encoding='gbk', errors='ignore') as f:
            f.write(content)
            
        print(f"已将 {file_path} 从 {encoding} 转换为GBK")
        return True
    except Exception as e:
        print(f"转换 {file_path} 时出错: {e}")
        return False

def check_gbk_file_for_garbled_text(file_path):
    """
    检查GBK文件中的乱码中文文本
    """
    try:
        with codecs.open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
        
        # 检查常见的乱码文本模式
        garbled_patterns = ['锟斤拷', '锘', '', '锘']
        found_garbled = False
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern in garbled_patterns:
                if pattern in line:
                    found_garbled = True
                    # 用红色高亮显示乱码文本 (ANSI转义码)
                    highlighted_line = line.replace(pattern, f"\033[31m{pattern}\033[0m")
                    print(f"\033[31m发现乱码文本\033[0m 在 {file_path} 的第 {i} 行: {highlighted_line}")
        
        if not found_garbled and has_chinese_text(content):
            # 可以添加更复杂的乱码检测
            pass
            
        return found_garbled
    except Exception as e:
        print(f"读取 {file_path} 时出错: {e}")
        return False

def process_cpp_files(directory):
    """
    处理目录中的所有.cpp文件
    """
    cpp_files = list(Path(directory).rglob("*.cpp"))
    
    print(f"找到 {len(cpp_files)} 个 .cpp 文件")
    
    for file_path in cpp_files:
        print(f"\n正在处理: {file_path}")
        
        # 检测编码
        detected_encoding = detect_encoding(file_path)
        print(f"检测到的编码: {detected_encoding}")
        
        if detected_encoding is None:
            print(f"无法确定 {file_path} 的编码")
            continue
            
        # 标准化编码名称
        detected_encoding = detected_encoding.lower()
        
        if detected_encoding.startswith('gb') or detected_encoding.startswith('windows'):
            # 文件已经是GBK或相似编码 (如 GB2312, GB18030, Windows-1252)
            print(f"{file_path} 已经是GBK兼容编码")
            
            # 检查乱码中文文本
            has_garbled = check_gbk_file_for_garbled_text(file_path)
            if has_garbled:
                print(f"\033[31m警告: 在 {file_path} 中发现乱码文本\033[0m")
            else:
                print(f"在 {file_path} 中未发现明显的乱码文本")
        else:
            # 转换为GBK
            print(f"正在将 {file_path} 从 {detected_encoding} 转换为GBK...")
            if convert_to_gbk(file_path):
                print(f"成功转换 {file_path}")
            else:
                print(f"转换 {file_path} 失败")

if __name__ == "__main__":
    # 从用户输入获取目录或使用当前目录
    directory = input("请输入目录路径 (或按回车键使用当前目录): ").strip()
    if not directory:
        directory = "."
    
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在")
        exit(1)
    
    process_cpp_files(directory)
    print("\n处理完成。")