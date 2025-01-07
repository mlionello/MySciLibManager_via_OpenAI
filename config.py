OPENAI_API_KEY='INSERT HERE YOUR OPENAI API KEY' # keep it between the ' '

# you can use a short introduction as prior knowledge in order to help to foccus on a problem, otherwise you can keep it clean or sue some output provided by https://consensus.app/ 
PROMPT_INIT = '''IT WORKS BETTER IF YOU GIVE SOME CONTEXT HERE''' 

# This is also helpful to focalize on a specific aspect while reading throughout the pubs
PROMPT_INSTRUCTION = '''My interest is how/I am studying/... \n
        Given the following scientific publication, please just fill the following form (no formatting):\n"''' ### keep this line as it is to input the instruction to the model

# add the information you are looking for in the following set of labels. keep RESULT_LABELS and DB_LABELS aligned (saved for Path and Filename in DB_LABELS)
RESULT_LABELS = [
    "Title",
    "Authors",
    "In-text Citation (authors, year)",
    "Year of publication",
    "Keywords",
    "Main finding",
    "Two-sentences abstract",
    "Subtopic",
    "What key message for my research interest", ## ADD MORE questions (but add also one keyword in DB_LABELS for each of them)
]
DB_LABELS = [
    "Path", # this is mandatory
    "Filename", # this is mandatory
    "Title", # from here on they must match the order of RESULT_LABELS and must be included in static_fields in app.py
    "Authors",
    "Citation",
    "Year",
    "Keywords",
    "Findings",
    "ShortAbstract",
    "Subtopic",
    "RQ",
]
