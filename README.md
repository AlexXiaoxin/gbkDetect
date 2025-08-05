

# C++ （.cpp）文件编码GBK检测脚本

Author:肖行Nyx

Data:2025-08-05

### How to use this script:

1. Save the script as `encoding_checker.py`
2. Install the required dependency:

```
pip install chardet
```

3. Run the script:
   
   `python gbkDetect.py`



### Features of this script:

1. **Batch Detection**: Detects encoding of all `.cpp` files in a directory and subdirectories
2. **Encoding Conversion**: Converts non-GBK files to GBK encoding
3. **GBK File Preservation**: Leaves GBK-encoded files unchanged
4. **Garbled Text Detection**: Identifies common garbled text patterns in GBK files and highlights them in red
5. **Detailed Reporting**: Provides information about each file's processing status

### Notes:

- The script uses the `chardet` library for accurate encoding detection
- For garbled text detection, it looks for common patterns like "锟斤拷", "锘", and ""
- When garbled text is found, it's displayed in red using ANSI escape codes
- The script handles files with various encodings and converts them properly to GBK


