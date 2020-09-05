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
    
    if column == 'restaurant.type.food':
        result = 'Some delicious {} coming right up!'.format(value)
    else: result = "Sorry, we don't support that just yet!"
    return result

def bot_response(userText):
    if intent.current_intent == None:
        intent.update_intent(get_intent(userText))
    
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

    check_identified_entities(entity, rec)
    slot_needed = check_unfilled_entities(rec)

    if slot_needed:
        return get_rec_response(slot_needed)
    
    else:
        # check_database_using_query
        intent.reset_intent()
        return "Ready to query!"
    

def enquiry_handler(text):
    entity = PredictNer(text)
    
    check_identified_entities(entity, enq)
    slot_needed = check_unfilled_entities(enq)

    if slot_needed:
        return get_enq_response(slot_needed)

    else:
        intent.reset_intent()
        return "Ready for enquiry!"

def reservation_handler(text):
    entity = PredictNer(text)
    
    check_identified_entities(entity, res)
    slot_needed = check_unfilled_entities(res)

    if slot_needed:
        return get_res_response(slot_needed)

    else:
        intent.reset_intent()
        return "Ready to make a reservation!"

def check_identified_entities(in_dict, ref):
    # check for which entities have yet to be identified
    # return bot response to get the missing entities
    ref_keys = set(vars(ref).keys())
    in_keys = set(in_dict.keys())
    shared_keys = in_keys.intersection(ref_keys)
    
    for key in shared_keys:
        setattr(ref, key, in_dict[key])

    return

def check_unfilled_entities(ref):
    for key in vars(ref).keys():
        if getattr(ref, key) == None:
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
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_enq_response(text):
    if text == 'restaurant':
        return "Okay, what restaurant would you like to enquire about?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_res_response(text):
    if text == 'date':
        return "What date is the reservation for?"
    if text == 'time':
        return "What time is the reservation for?"
    # if text == 'reserve_name':
    #     return "Who is this reservation for?"
    if text == 'reserve_num':
        return "And for how many people?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"
