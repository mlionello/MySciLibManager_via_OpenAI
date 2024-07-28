import openai

def query_llm_for_metadata(text):
    prompt = (
        "Given the following excerpt of a scientific publication, complete as follows:\n"
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
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", []
