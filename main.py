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


def collect_pdfs_info(root_dir, log_file, existing_data):
    pdf_info_list = []
    pdf_files = [os.path.join(dirpath, file)
                 for dirpath, _, filenames in os.walk(root_dir)
                 for file in filenames
                 if file.lower().endswith('.pdf')]

    total_files = len(pdf_files)

    for idx, file_path in enumerate(pdf_files):
        filename = os.path.basename(file_path)

        if filename in existing_data:
            if existing_data[filename] != file_path:
                # Update path in existing data
                existing_data[filename] = file_path
            print(f"Skipping already processed file: {filename}")
            continue

        print(f"Processing file {idx + 1}/{total_files}: {filename}", end='\r')
        try:
            text = extract_text_from_pdf(file_path)
            truncated_text = truncate_text(text, max_tokens=4000)
            extracted_data, result = query_llm_for_metadata(truncated_text)

            # Create pdf_info dictionary with file path and extracted metadata
            pdf_info = {
                "Path": file_path,
                "Filename": filename,
                **extracted_data  # Merge extracted data into the dictionary
            }
            pdf_info_list.append(pdf_info)

            # Append results to log.txt
            with open(log_file, 'a') as log:
                log.write(f"File: {filename}\n")
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
        print(f"Processing file {idx + 1}/{total_files}: {filename} - Progress: {progress:.2f}%",
              end='\r')

    print()  # Print a newline after the last update to ensure the final message is displayed
    return pdf_info_list, existing_data


def save_to_csv(pdf_info_list, output_csv, updated_data):
    # Create a DataFrame from the new PDF info list
    new_df = pd.DataFrame(pdf_info_list)

    if os.path.exists(output_csv):
        # Load the existing CSV into a DataFrame
        existing_df = pd.read_csv(output_csv)

        # Update paths in existing DataFrame based on updated_data
        if updated_data:
            for filename, new_path in updated_data.items():
                if filename in existing_df['Filename'].values:
                    existing_df.loc[existing_df['Filename'] == filename, 'Path'] = new_path

        # Combine existing and new DataFrames
        # there should not be duplicated at this point
        # combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Filename'])
        combined_df = pd.concat([existing_df, new_df])
        combined_df.reset_index(drop=True, inplace=True)
    else:
        # If no existing CSV, just use the new DataFrame
        combined_df = new_df

    # Save the combined DataFrame to CSV
    combined_df.to_csv(output_csv, index=False)

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

    # Read existing CSV if it exists
    if os.path.exists(output_csv_file):
        existing_df = pd.read_csv(output_csv_file)
        existing_data = dict(zip(existing_df['Filename'], existing_df['Path']))
    else:
        existing_data = {}

    try:
        pdf_info_list, updated_data = collect_pdfs_info(root_directory, log_file, existing_data)
        save_to_csv(pdf_info_list, output_csv_file, updated_data)
        print(f"\nPDF information saved to {output_csv_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
        with open(log_file, 'a') as log:
            log.write(f"An error occurred: {e}\n")
            log.write(traceback.format_exc())
