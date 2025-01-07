-- it requires python 3.10 --

### Install and requirements:
```
git clone git@github.com:mlionello/MySciLibManager_via_OpenAI.git
conda create -n lib python==3.10
conda activate lib
cd MySciLibManager_via_OpenAI
pip install -r requirements.txt
```
### Configuration:
modify config.py by inserting your openai api key, and the prompt for GPT models
modify main.py at line 59: 
```
truncated_text = truncate_text(text, max_tokens=4000)
```
in case you want more inputs to be read from your library.
Do change max_tokens higher than 10-15k to be sure all the content of the article is read

### Launch GUI
```
python app.py 
```
if not done automatically, please navigate with your most favourite web browser to **http://localhost:5000** *or* **http://127.0.0.1:5000**

### Run!
Generate a CSV by reading all the pdfs in the subdirs of a specific parent folder

if not done automatically convert the csv into a db from the GUI

if not done automatically load the generated db directly from the GUI

## Explore!
You can play around by adding specific questions in **RESULT_LABELS** in *config.py*.
For each new question be sure to:
- add a keyword for the database in **DB_LABELS** in *config.py*
- add the variable name in static_fields in app.py by keeping the same order of DB_LABELS
