import os
import pandas as pd
import openai
import argparse

from extractor import extract_text_from_pdf, truncate_text
from metadata import query_llm_for_metadata

# Try to load the API key from environment variables first
api_key = os.getenv('OPENAI_API_KEY')

# If the API key is not found in environment variables, load from the local config file
if not api_key:
    try:
        from config import OPENAI_API_KEY
        api_key = OPENAI_API_KEY
    except ImportError:
        raise ImportError("OpenAI API key is not set in environment variables or config.py file.")

openai.api_key = api_key

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
        truncated_text = truncate_text(text, max_tokens=4000)
        title, author, cit, year, keywords, main_finding, abstract, subtopic, rq, result = query_llm_for_metadata(truncated_text)
        pdf_info_list.append({
            "Title": title,
            "Authors": author,
            "Year": year,
            "Cit": cit,
            "Keywords": keywords,
            "Main_Finding": main_finding,
            "Abstract": abstract,
            "Path": file_path,
            "Subtopic": subtopic,
            "RQ": rq,
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

    args = parser.parse_args()

    root_directory = args.root_directory
    output_csv_file = args.output_csv
    log_file = args.log_file
    base, ext = os.path.splitext(log_file)
    counter = 1
    while os.path.exists(log_file):
        log_file = f"{base}_{counter}{ext}"
        counter += 1

    pdf_info_list = collect_pdfs_info(root_directory, log_file)
    save_to_csv(pdf_info_list, output_csv_file)
    print(f"\nPDF information saved to {output_csv_file}")


