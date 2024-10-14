### Install and requirements:
```
git clone git@github.com:mlionello/lit_review.git
pip install -r requirements
```
### Configuration:
modify config.py by inserting your openai api key, and the prompt for GPT models
modify main.py at line 59: 
```
truncated_text = truncate_text(text, max_tokens=4000)
```
in case you want more inputs to be read from your library

### Launch GUI
```
python app.py 
```
if not done automatically, please navigate with your most favourite web browser to *http://localhost:5000*

### Fit
Generate a CSV by reading all the pdfs in the subdirs of a specific parent folder

if not done automatically convert the csv into a db from the GUI

if not done automatically load the generated db directly from the GUI
