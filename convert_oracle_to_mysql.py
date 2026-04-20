#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle SQL to MySQL SQL Converter
Converts Oracle INSERT statements to MySQL compatible format
"""

import re
import os
from pathlib import Path


def convert_oracle_to_mysql(input_file, output_file):
    """
    Convert Oracle SQL file to MySQL compatible format
    
    Args:
        input_file: Path to Oracle SQL file
        output_file: Path for output MySQL SQL file
    """
    print(f"Converting {input_file}...")
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract table name from first INSERT statement
    table_match = re.search(r'"MONITORWO"\."(\w+)"', ''.join(lines[:5]))
    if not table_match:
        print(f"Error: Could not find table name in {input_file}")
        return False
    
    table_name = table_match.group(1)
    print(f"Found table name: {table_name}")
    
    converted_lines = []
    for line in lines:
        # Replace schema.table with just table name using backticks
        line = re.sub(
            r'"MONITORWO"\."' + table_name + r'"',
            f'`{table_name}`',
            line
        )
        
        # Replace all double quotes with backticks (for column names)
        line = re.sub(r'"([^"]+)"', r'`\1`', line)
        
        # Convert Oracle timestamp format to MySQL datetime
        # Oracle: '2025-01-08 09:54:40.000000'
        # MySQL: '2025-01-08 09:54:40'
        line = re.sub(
            r"'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\.\d+'",
            r"'\1'",
            line
        )
        
        # Handle NULL values - ensure consistency (keep uppercase)
        # line = re.sub(r'\bnull\b', 'NULL', line)
        
        converted_lines.append(line)
    
    # Write the converted content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)
    
    # Count number of INSERT statements
    insert_count = sum(1 for line in converted_lines if re.search(r'INSERT INTO', line, re.IGNORECASE))
    print(f"Converted {insert_count} INSERT statements")
    print(f"Output saved to: {output_file}")
    
    return True


def main():
    """Main function to convert all Oracle SQL files"""
    
    # Define input and output files
    base_dir = "/Users/linziwang/Downloads"
    
    files_to_convert = [
        "MW_ORDER_CIRCULATE_INFO.sql",
        "MW_ORDER_WORK.sql",
        "MW_ORDER_PUBLIC_INCIDENT.sql",
        "MW_ORDER_CIRCULATE.sql"
    ]
    
    print("=" * 60)
    print("Oracle SQL to MySQL Converter")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for filename in files_to_convert:
        input_path = os.path.join(base_dir, filename)
        
        # Check if file exists
        if not os.path.exists(input_path):
            print(f"Warning: File not found - {input_path}")
            fail_count += 1
            continue
        
        # Generate output filename
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}_mysql.sql"
        output_path = os.path.join(base_dir, output_filename)
        
        try:
            if convert_oracle_to_mysql(input_path, output_path):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"Error converting {filename}: {str(e)}")
            fail_count += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {len(files_to_convert)}")
    print()
    
    if success_count > 0:
        print("Next steps:")
        print("1. Review the converted SQL files")
        print("2. Import into MySQL using:")
        for filename in files_to_convert:
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_mysql.sql"
            print(f"   mysql -u root -p monitorwo < {base_dir}/{output_filename}")


if __name__ == "__main__":
    main()
