import os
import pandas as pd
import openai
import argparse
import traceback

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


def collect_pdfs_info(root_dir, log_file, existing_paths):
    pdf_info_list = []
    pdf_files = [os.path.join(dirpath, file)
                 for dirpath, _, filenames in os.walk(root_dir)
                 for file in filenames
                 if file.lower().endswith('.pdf')]

    total_files = len(pdf_files)

    for idx, file_path in enumerate(pdf_files):
        if existing_paths and file_path in existing_paths:
            print(f"Skipping already processed file: {os.path.basename(file_path)}")
            continue

        print(f"Processing file {idx + 1}/{total_files}: {os.path.basename(file_path)}", end='\r')
        try:
            text = extract_text_from_pdf(file_path)
            truncated_text = truncate_text(text, max_tokens=4000)
            extracted_data, result = query_llm_for_metadata(truncated_text)

            # Create pdf_info dictionary with file path and extracted metadata
            pdf_info = {
                "Path": file_path,
                **extracted_data  # Merge extracted data into the dictionary
            }
            pdf_info_list.append(pdf_info)

            # Append results to log.txt
            with open(log_file, 'a') as log:
                log.write(f"File: {os.path.basename(file_path)}\n")
                log.write(f"{result}\n")
                log.write(f"Path: {file_path}\n")
                log.write("\n" + "=" * 80 + "\n\n")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            with open(log_file, 'a') as log:
                log.write(f"Error processing file: {file_path}\n")
                log.write(f"Exception: {e}\n")
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
    parser.add_argument('--skip-existing', action='store_true', help='Skip files already listed in the existing CSV')

    args = parser.parse_args()

    root_directory = args.root_directory
    output_csv_file = args.output_csv
    log_file = args.log_file
    skip_existing = args.skip_existing

    base, ext = os.path.splitext(log_file)
    counter = 1
    while os.path.exists(log_file):
        log_file = f"{base}_{counter}{ext}"
        counter += 1

    # Check if CSV exists
    if os.path.exists(output_csv_file):
        if skip_existing:
            # Read existing CSV and extract file paths
            existing_df = pd.read_csv(output_csv_file)
            existing_paths = set(existing_df["Path"])
        else:
            print(
                f"CSV file {output_csv_file} already exists. Use --skip-existing to skip existing files or use a different file.")
            exit()
    else:
        existing_paths = None

    try:
        pdf_info_list = collect_pdfs_info(root_directory, log_file, existing_paths)
        save_to_csv(pdf_info_list, output_csv_file)
        print(f"\nPDF information saved to {output_csv_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        with open(log_file, 'a') as log:
            log.write(f"An error occurred: {e}\n")
            log.write(traceback.format_exc())
