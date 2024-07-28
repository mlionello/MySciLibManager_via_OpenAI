import os
import fitz  # PyMuPDF
import pandas as pd
import openai
import argparse

# Set up your OpenAI API key
openai.api_key = 'sk-proj-MBRBkxaZSfnIajP7jdC9T3BlbkFJcXNlFXvrv94wOMZdQvSh'

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""


def truncate_text(text, max_tokens=1000):
    tokens = text.split()
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return ' '.join(tokens)


def query_llm_for_metadata(text):
    prompt = (
            "given the following excerpt of scientific publication, complete as follows:\n"
            "Title: ###INSERT HERE###\n"
            "Authors: ###INSERT HERE###\n"
            "Year of publication: ###INSERT HERE###\n"
            "Keywords: ###INSERT HERE###\n"
            "Main finding: ###INSERT HERE###\n"
            "One-sentence abstract: ###INSERT HERE###\n"
            "\nText:\n" + text
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250  # Adjust as needed
        )
        result = response.choices[0].message['content'].strip().split("\n")

        def extract_field(label, result_lines):
            for line in result_lines:
                if line.startswith(f"{label}:"):
                    return line.split(f"{label}:")[1].strip()
            return "N/A"

        title = extract_field("Title", result)
        author = extract_field("Authors", result)
        year = extract_field("Year of publication", result)
        keywords = extract_field("Keywords", result)
        main_finding = extract_field("Main finding", result)
        abstract = extract_field("One-sentence abstract", result)

        return title, author, year, keywords, main_finding, abstract, result
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", result


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

    args = parser.parse_args()

    root_directory = args.root_directory
    output_csv_file = args.output_csv
    log_file = args.log_file

    pdf_info_list = collect_pdfs_info(root_directory, log_file)
    save_to_csv(pdf_info_list, output_csv_file)
    print(f"\nPDF information saved to {output_csv_file}")

