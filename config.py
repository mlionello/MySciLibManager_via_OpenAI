OPENAI_API_KEY='INSERT HERE YOUR OPENAI API KEY'
PROMPT_INIT = '''IT WORKS BETTER IF YOU GIVE SOME CONTEXT HERE'''
PROMPT_INSTRUCTION = '''My interest is how/I am studying/....\n
        Given the following scientific publication, please just fill the following form (no formatting):\n"'''
RESULT_LABELS = [
    "Title",
    "Authors",
    "In-text Citation (authors, year)",
    "Year of publication",
    "Keywords",
    "Main finding",
    "Two-sentences abstract",
    "Subtopic",
    "What key message for my research interest",
]
DB_LABELS = [
    "Path",
    "Filename",
    "Title",
    "Authors",
    "Citation",
    "Year",
    "Keywords",
    "Findings",
    "ShortAbstract",
    "Subtopic",
    "RQ"
]
