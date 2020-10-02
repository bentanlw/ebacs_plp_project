import entities_functions
import intents_functions
import query_functions
from mdl_classification import PredictClass
from mdl_recognition import PredictNer
from mdl_similarities import similar_resto, load_resto
from numerizer import numerize
import re

intent = intents_functions.Intents()
# enq = entities_functions.Enquiry()
# rec = entities_functions.Recommendation()
# res = entities_functions.Reservation()
slot = entities_functions.Slots()

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

    # check_identified_entities(entity, rec)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(rec)
    slot_needed = slot.check_rec()
   
    if slot_needed:
        return get_rec_response(slot_needed)
    
    if slot.restaurant_choice == 0:
        return get_restaurant(text)
    
    else:
        # check_database_using_query
        # intent.reset_intent()
        result, error_state = get_recommendation(slot)
        if error_state == 0:
            slot.restaurant_choice = 0
        return result
    
def get_restaurant(text):
    s = numerize(text)
    choice = int(re.search("\d+", s).group(0))
    if choice <= len(slot.result.index):
        slot.restaurant = slot.result.name[choice - 1]
        intent.update_intent('reservation')
        return "You have selected {}! Would you like to make a reservation?".format(slot.restaurant)
    else:
        return "Sorry that's not a valid restaurant number"

def enquiry_handler(text):
    entity = PredictNer(text)
    
    # check_identified_entities(entity, enq)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(enq)
    slot_needed = slot.check_enq()

    if slot_needed:
        return get_enq_response(slot_needed)

    else:
        intent.reset_intent()
        return get_enquiry(slot)

def reservation_handler(text):
    # should check if a restaurant has been identified yet
    entity = PredictNer(text)
    
    # check_identified_entities(entity, res)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(res)
    slot_needed = slot.check_res()
    

    if slot_needed:
        return get_res_response(slot_needed)

    else:
        intent.reset_intent()
        return query_functions.get_reservation(slot)

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
        return "Okay, what restaurant would you like to know about?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_res_response(text):
    if text == 'date':
        return "What date is the reservation for?"
    if text == 'time':
        return "What time is the reservation for?"
    if text == 'reserve_name':
        return "Who is this reservation for?"
    if text == 'num_guests':
        return "And for how many people?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_recommendation(slot):
    error_state = 0 #0 no error, 1 df is None, 2 df filtered out 
    df = similar_resto(slot.food_type, top_n = 1000)
    result = "Sorry, we did not manage to locate any restaurants that match your query"
    if df is None:
        error_state = 1
        return result, error_state
    # print(len(df.index))
    # is resto open?
    ## check if open on that day
    # df = df.loc[df[slot.get_weekday()].dropna().index]
    # print(len(df.index))
    # ## check if open at that timing
    # df = df[df.index.isin(restaurant_open(df[slot.get_weekday()], slot.get_mealtime()))]
    # print(len(df.index))
    df = df[df[slot.get_weekday()] == slot.get_mealtime()]
   
    # is resto within budget?
    df = df[df['PriceRange'].isin(slot.get_budget())]

    # is resto above rating? add in Sentiment_mean here
    df = df[df['stars'] >= slot.rating]
    
    if len(df.index) == 0:
        error_state = 2
    # return df[:5].name.to_string()

    if error_state == 2:
        return result, error_state
    
    else:
        slot.result = df[['name', 'categories']][:3]
        result = build_rec_response(slot.result.to_csv(index = False), slot)
        return result, error_state
        # return df[:5]

def get_enquiry(slot):
    df = load_resto()
    
    return df[df.name.str.lower() == slot.restaurant.lower()]

def get_reservation(slot):
    # need some way of differentiating if we got here from enquiry or recommendation or directly
    pass

def restaurant_open(series, list):
    open_list = []
    series_idx = series.index
    for idx, item in enumerate(series):
        if check_mealtime(item[2], list):
            open_list.append(series_idx[idx])
    return open_list

def check_mealtime(list_1, list_2):
    is_open = False
    for index, (e1, e2) in enumerate(zip(list_1, list_2)):
        if e1 == e2:
            if e1 == 1:
                is_open = True
    return is_open

def format_rec_response(s):
    s_list = s.split("\r\n")[1:-1]
    s_list = [element.split(",\"") for element in s_list]
    s_list = [[m.replace("\"","") for m in n] for n in s_list]

    return s_list

def build_rec_response(s, slot):
    start = "We found the following restaurants that match {}<br/><br/>".format(slot.food_type)
    ss = ""
    end = "<br/>Which number of restaurant would you prefer?"
    for i, n in enumerate(format_rec_response(s)):
        ss = ss + "{}.&ensp;{}&emsp;&emsp;[{}]<br/>".format(i+1, n[0], n[1])
    return start+ss+end
# setattr(slot, 'food_type', ['sashimi'])
# bot_response("are there any good salmon sashimi restaurants under 30 for dinner tomorrow at 7pm?")

