# Here I want to create a skeleton to demonstrate the chatbot in action.
# - up to this point, i have already produced a model to extract the entities from a string
# - I also know how to read off the identified entities
# - so here, I will want to define a function that would take in the user string, run it through the model
#   and return the identified entities.

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
    if entity_list is None: return
    value = entity_list[0]
    column = entity_list[1]

    if column == 'restaurant.type.food':
        print('Finding you some delicious {} food!'.format(value))
    else: print("Sorry, we don't support that just yet!")
    return
# main loop
# load spacy model
import spacy
from pathlib import Path

output_dir=Path('C:\\Users\\Ben\\Documents\\ebacs\\practical_language_processing\\ebacs_plp_project\\model\\')
ner = spacy.load(output_dir)

get_yelp_resto(entity_extractor(get_user_string(), ner))