import os
import pandas as pd
import openai
import argparse

from extractor import extract_text_from_pdf, truncate_text
from metadata import query_llm_for_metadata
from database import create_database, insert_into_database

# Set up your OpenAI API key
openai.api_key = 'sk-proj-MBRBkxaZSfnIajP7jdC9T3BlbkFJcXNlFXvrv94wOMZdQvSh'


def collect_pdfs_info(root_dir, log_file):
    pdf_info_list = []
    pdf_files = [os.path.join(dirpath, file)
                 for dirpath, _, filenames in os.walk(root_dir)
                 for file in filenames
                 if file.lower().endswith('.pdf')]

    total_files = len(pdf_files)

    for idx, file_path in enumerate(pdf_files):
        print(f"Processing file {idx + 1}/{total_files}: {os.path.basename(file_path)}", end='\r')
        text = extract_text_from_pdf(file_path)
        truncated_text = truncate_text(text, max_tokens=1000)
        title, author, year, keywords, main_finding, abstract, result = query_llm_for_metadata(truncated_text)
        pdf_info_list.append({
            "Title": title,
            "Author(s)": author,
            "Year": year,
            "Keywords": keywords,
            "Main Finding": main_finding,
            "One-sentence Abstract": abstract,
            "Path": file_path
        })

        # Append results to log.txt
        with open(log_file, 'a') as log:
            log.write(f"File: {os.path.basename(file_path)}\n")
            log.write(f"{result}\n")
            log.write(f"Path: {file_path}\n")
            log.write("\n" + "=" * 80 + "\n\n")

        # Print progress percentage
        progress = (idx + 1) / total_files * 100
        print(f"Processing file {idx + 1}/{total_files}: {os.path.basename(file_path)} - Progress: {progress:.2f}%",
              end='\r')

    print()  # Print a newline after the last update to ensure the final message is displayed
    return pdf_info_list


def save_to_csv(pdf_info_list, output_csv):
    df = pd.DataFrame(pdf_info_list)
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract metadata from PDFs in a directory.')
    parser.add_argument('root_directory', type=str, help='Path to the root directory containing PDF files')
    parser.add_argument('output_csv', type=str, help='Path to the output CSV file')
    parser.add_argument('log_file', type=str, help='Path to the log.txt file where results will be appended')
    parser.add_argument('database', type=str, help='Path to the SQLite database file')

    args = parser.parse_args()

    root_directory = args.root_directory
    output_csv_file = args.output_csv
    log_file = args.log_file
    database_file = args.database

    pdf_info_list = collect_pdfs_info(root_directory, log_file)
    save_to_csv(pdf_info_list, output_csv_file)
    print(f"\nPDF information saved to {output_csv_file}")

    create_database(database_file)
    insert_into_database(database_file, pdf_info_list)
    print(f"PDF information inserted into database {database_file
