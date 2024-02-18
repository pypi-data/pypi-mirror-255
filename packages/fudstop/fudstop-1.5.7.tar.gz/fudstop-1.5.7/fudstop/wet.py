import requests
import pandas as pd

term = 'protective'
r = requests.get(f'https://www.fudstop.io/api/law/{term}').json()

articles = [i.get('article') for i in r if i.get('article') != 'CASE BULLETS']
notes = [i.get('notes') for i in r]
parent = [i.get('parent_doc') for i in r]
rule = [i.get('rule') for i in r]
text = [i.get('text') for i in r]

data_dict = { 
    'article': articles,
    'notes': notes,
    'parent': parent,
    'rule': rule,
    'text': text
}

