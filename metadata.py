import openai
import traceback
from config import PROMPT_INIT
from config import PROMPT_INSTRUCTION
from config import RESULT_LABELS

def create_prompt(text):
    # Build the prompt string using the result labels
    prompt = PROMPT_INIT + PROMPT_INSTRUCTION
    for label in RESULT_LABELS:
        prompt += f"{label}: ###INSERT HERE###\n"
    prompt += "\nText:\n" + text
    return prompt

def query_llm_for_metadata(text):
    prompt = create_prompt(text)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Adjust as needed
        )
        result_lines = response.choices[0].message['content'].strip().split("\n")

        def extract_field(label, result_lines):
            for line in result_lines:
                if line.startswith(f"{label}:"):
                    return line.split(f"{label}:")[1].strip()
            return "N/A"

        extracted_data = {label: extract_field(label, result_lines) for label in RESULT_LABELS}

        return extracted_data, result_lines
    except Exception as e:
        print(f"Error querying LLM: {e}")
        print(traceback.format_exc())
        # Return a dictionary with "N/A" values and the raw result lines
        return {label: "N/A" for label in RESULT_LABELS}, []
