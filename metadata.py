import openai
import traceback

def query_llm_for_metadata(text):
    prompt = (
        "My interest is how analytical or affective information and descriptors (context) of a music piece manipulates the "
        "listening, engagement and emotional experience when listening to that music\n"
        "Given the following scientific publication, please just fill the following form (no formatting):\n"
        "Title: ###INSERT HERE###\n"
        "Authors: ###INSERT HERE###\n"
        "In-text Citation (authors, year): ###INSERT HERE###\n"
        "Year of publication: ###INSERT HERE###\n"
        "Keywords: ###INSERT HERE###\n"
        "Main finding: ###INSERT HERE###\n"
        "Two-sentences abstract: ###INSERT HERE###\n"
        "Subtopic: ###INSERT HERE###\n"
        "What key message for my research interest: ###INSERT HERE###\n"
        "\nText:\n" + text
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Adjust as needed
        )
        result = response.choices[0].message['content'].strip().split("\n")

        def extract_field(label, result_lines):
            for line in result_lines:
                if line.startswith(f"{label}:"):
                    return line.split(f"{label}:")[1].strip()
            return "N/A"

        title = extract_field("Title", result)
        author = extract_field("Authors", result)
        cit = extract_field("In-text Citation (authors, year)", result)
        year = extract_field("Year of publication", result)
        keywords = extract_field("Keywords", result)
        main_finding = extract_field("Main finding", result)
        abstract = extract_field("Two-sentences abstract", result)
        subtopic = extract_field("Subtopic", result)
        rq = extract_field("What key message for my research interest", result)

        return title, author, cit, year, keywords, main_finding, abstract, subtopic, rq, result
    except Exception as e:
        print(f"Error querying LLM: {e}")
        print(traceback.format_exc())
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", []
