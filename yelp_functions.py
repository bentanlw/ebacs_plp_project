import spacy
from pathlib import Path

output_dir=Path('C:\\Users\\Ben\\Documents\\ebacs\\practical_language_processing\\ebacs_plp_project\\model\\')
ner = spacy.load(output_dir)

def entity_extractor(string, ner_model):
    if string is None: return
    else:
        doc = ner_model(string)
        entities = []
        for ent in doc.ents:
            entities.append(ent.text)
            entities.append(ent.label_)
    print(entities)
    return entities

def get_user_string():
    return input("Hi, what would you like to eat?\n")

def get_yelp_resto(entity_list):
    if not entity_list: return "Sorry I can't understand you :(("
    value = entity_list[0]
    column = entity_list[1]
    # print(value)
    if column == 'restaurant.type.food':
        result = 'Some delicious {} coming right up!'.format(value)
    else: result = "Sorry, we don't support that just yet!"
    return result

def bot_response(userText):
    entity = entity_extractor(userText, ner)
    return get_yelp_resto(entity)