import entities_functions
from mdl_classification import PredictClass

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
    intent = get_intent(userText)
    
    if intent == 'unclassified':
        return "Sorry I don't understand what you mean, could you rephrase that please?"
    elif intent == 'greeting':
        return "Hi! I can help with a recommendation, an enquiry or even reservations!"
    elif intent == 'recommendation':
        return recommendation_handler(userText)
    elif intent == 'enquiry':
        return enquiry_handler(userText)
    elif intent == 'reservation':
        return reservation_handler(userText)
    else:#if none of the above, it is an 'goodbye' intent
        return "Bye! Have a great day!"

def get_intent(userText):
    predict = PredictClass(userText)
    return predict[1]

def recommendation_handler(text):
    entity = entities_functions.extractor(text, 'ner')

    # check_identified_entities()
    # check_entities_filled()
    # if some_entities_missing or all_entities_missing:
    #     ask_for_more_info
    # else:
    #     check_database_using_query
    return "Here's a recommendation!"

def enquiry_handler(text):
    entity = entities_functions.extractor(text, 'ner')
    return "Here's a enquiry!"

def reservation_handler(text):
    entity = entities_functions.extractor(text, 'ner')
    return "Here's a reservation!"