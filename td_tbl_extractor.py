#!/usr/bin/env python
import os
import re
import csv
import sys
# from pathlib import Path # This line is not needed

# regex for table names after FROM / JOIN keywords
TABLE_REGEX = re.compile(
    r'\b(?:FROM|JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN)\s+([a-zA-Z0-9_."`]+(?:\s+AS\s+[a-zA-Z0-9_`"]+|(?=\s))?)',
    re.IGNORECASE)

def extract_tables_from_sql(sql_text):
    return TABLE_REGEX.findall(sql_text)

def process_sql_files(base_dir, output_file):
    with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["script_path", "script_name", "table_name"])

        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                if fname.endswith(".sql"):
                    file_path = os.path.join(root, fname)
                    try:
                        sql_lines = []
                        with open(file_path, 'r') as f:
                            # Read the first line and check the condition
                            first_line = f.readline()
                            if not first_line.strip().endswith(".out"):
                                sql_lines.append(first_line)

                            # Process the remaining lines, skipping comments
                            for line in f:
                                if not line.strip().startswith("--"):
                                    sql_lines.append(line)

                        sql_text = "".join(sql_lines)
                        tables = extract_tables_from_sql(sql_text)
                        for t in tables:
                            writer.writerow([file_path, fname, t])
                    except Exception as e:
                        sys.stderr.write("Error reading %s: %s\n" % (file_path, str(e)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python tbl_extractor.py <base_dir> [--output <output_file>]"
        sys.exit(1)

    base_dir = sys.argv[1]
    output_file = "tbl_mapping.csv"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    # Check if the output file exists, delete it if it does
    if os.path.exists(output_file):
        os.remove(output_file)

    process_sql_files(base_dir, output_file)
    print "Done. Output written to %s" % output_file
