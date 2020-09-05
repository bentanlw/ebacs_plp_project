import spacy
from pathlib import Path

output_dir=Path('models/resto_entity_recognition')
ner = spacy.load(output_dir)

def extractor(string, ner_model):
    ner_mdl = ner
    if string is None: return
    else:
        doc = ner_mdl(string)
        entities = []
        for ent in doc.ents:
            entities.append(ent.text)
            entities.append(ent.label_)
    print(entities)
    return entities

class Recommendation:
    def __init__(self):
        self.food_type = None
        self.meal_type = None
        self.price = None
        self.rating = 4

class Enquiry:
    def __init__(self):
        self.restaurant = None

class Reservation:
    def __init__(self):
        self.reserve_date = None
        self.reserve_time = None
        self.reserve_name = None
        self.reserve_num = None