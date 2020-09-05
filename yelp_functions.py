import entities_functions
import intents_functions
from mdl_classification import PredictClass
from mdl_recognition import PredictNer

intent = intents_functions.Intents()
enq = entities_functions.Enquiry()
rec = entities_functions.Recommendation()
res = entities_functions.Reservation()

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
    if intent.current_intent == None:
        intent.update_intent(get_intent(userText))
    
    # needs a flag to maintain the chosen intent
    # remember to reset the intent later on
    
    if intent.current_intent == 'unclassified':
        intent.reset_intent()
        return "Sorry I don't understand what you mean, could you rephrase that please?"
    elif intent.current_intent == 'greeting':
        intent.reset_intent()
        return "Hi! I can help with a recommendation, an enquiry or even reservations!"
    elif intent.current_intent == 'recommendation':
        return recommendation_handler(userText)
    elif intent.current_intent == 'enquiry':
        return enquiry_handler(userText)
    elif intent.current_intent == 'reservation':
        return reservation_handler(userText)
    else:#if none of the above, it is an 'goodbye' intent
        intent.reset_intent()
        return "Bye! Have a great day!"

def get_intent(userText):
    predict = PredictClass(userText)
    return predict[1]

def recommendation_handler(text):
    entity = PredictNer(text)

    check_identified_entities(entity)
    slot_needed = check_unfilled_entities()

    if slot_needed:
        return get_rec_response(slot_needed)
    # if some_entities_missing or all_entities_missing:
    #     ask_for_more_info
    else:
        # check_database_using_query
        intent.reset_intent()
        return "Ready to query!"
    # return "Here's a recommendation!"

def enquiry_handler(text):
    entity = PredictNer(text)
    intent.reset_intent()
    return "Here's a enquiry!"

def reservation_handler(text):
    entity = PredictNer(text)
    intent.reset_intent()
    return "Here's a reservation!"

def check_identified_entities(in_dict):
    # check for which entities have yet to be identified
    # return bot response to get the missing entities
    ref_keys = set(vars(rec).keys())
    in_keys = set(in_dict.keys())
    shared_keys = in_keys.intersection(ref_keys)

    for key in shared_keys:
        setattr(rec, key, in_dict[key])

    return

def check_unfilled_entities():
    for key in vars(rec).keys():
        if getattr(rec, key) == None:
            return key

def get_rec_response(text):
    if text == 'food_type':
        return "Okay, what type of food would you like?"
    if text == 'meal_type':
        return "What type of meal is this?"
    if text == 'price':
        return "Alright, do you have a budget in mind?"
    if text == 'rating':
        return "How good of a restaurant?"

# a = "hello i'm looking for italian restaurants below 30 dollars"

# check_identified_entities(a)