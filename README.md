### Install and requirements:
```
git clone git@github.com:mlionello/lit_review.git
pip install -r requirements
```
### Fit
**metadatada.py** contains the prompt for openai query

**config.py** create and specify your api key here (OPENAI_API_KEY='abc...')

```
python main.py /your/path/to/paper/folder/root /your/path/to/save/csv/results.csv
```
### Display
**app.py** will generate a database from the csv file.
```
python app.py /your/path/to/save/csv/results.csv
```
if not done automatically, please navigate with your most favourite web browser to *http://localhost:5000*
