import entities_functions
import intents_functions
from mdl_classification import PredictClass
from mdl_recognition import PredictNer
from mdl_similarities import similar_resto, load_resto
from numerizer import numerize
import re

intent = intents_functions.Intents()
slot = entities_functions.Slots()

def bot_reset():
    slot.clear_slots()
    intent.reset_intent()
    return None

def bot_response(userText):
    print(vars(slot))
    print("current intent: {}".format(vars(intent)))

    user_intent = get_intent(userText)

    if userText.lower().strip() == 'quit':
        slot.clear_slots()
        intent.reset_intent()
        return "Bye! Have a great day! (You may ask another question to start a new conversation)"

    options = ['reservation', 'enquiry', 'recommendation']
    opt_found = [word for word in options if word in userText.lower().strip()]
    if len(opt_found) > 0:
        intent.update_intent(opt_found[0])


    # check update current_intent if None
    if intent.current_intent == None:
        intent.update_intent(user_intent)

    # decide what to do based on current_intent
    if intent.current_intent == 'greeting':
        intent.reset_intent()
        return "Hi! I can help with a recommendation, an enquiry or even reservations!"
    elif intent.current_intent == 'unclassified':
        intent.reset_intent()
        return "Sorry I don't understand what you mean, could you rephrase that please?"
    elif intent.current_intent == 'recommendation':
        return recommendation_handler(userText)
    elif intent.current_intent == 'enquiry':
        return enquiry_handler(userText)
    elif intent.current_intent == 'reservation':
        # if userText in ['today', 'tomorrow', 'tonight']:
        #     slot.date = userText

        # time_pattern = '([\d]{0,2}[\.:]?[\d]{1,2})\s?(pm|p\.m\.|am|a\.m\.|nn|noon)'

        # if re.search(time_pattern, userText) != None:
        #     slot.time = ''.join([x for x in re.search(time_pattern, userText).group(0).split()])
        
        return reservation_handler(userText)
    else:   #if none of the above, it is an 'goodbye' intent
        intent.reset_intent()
        return "Bye! Have a great day!"
    
def get_intent(userText):
    predict = PredictClass(userText)
    return predict[1]

def recommendation_handler(text):
    entity = PredictNer(text)
    
    if entity.get('food_type', None)!=None:
        # entity['food_type'] += [x.lower() for x in set(text.split())]
        entity['food_type'] += [x.lower() for x in [text] if len(x.split())<3]
        entity['food_type'] = list(set(entity['food_type']))

    # check_identified_entities(entity, rec)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(rec)
    slot_needed = slot.check_rec()
   
    if slot_needed:
        return get_rec_response(slot_needed)
    
    if slot.restaurant_choice == 0:
        if text.lower() == 'more':
            return get_recommendation(slot)
        else:
            return get_restaurant(text)
    
    else:
        # check_database_using_query
        # intent.reset_intent()
        result, error_state = get_recommendation(slot)
        if error_state == 0:
            slot.restaurant_choice = 0

        else:
            error_state = 0
            slot.clear_slots()
            intent.reset_intent()

        return result
    
def get_restaurant(text):
    s = numerize(text)
    choice = int(re.search("\d+", s).group(0))

    if choice <= len(slot.result.index):
        slot.restaurant = [slot.result.name.iloc[choice - 1]]
        intent.update_intent('reservation')
        setattr(slot, 'restaurant_choice', 1)
        return "You have selected {}! Would you like to make a reservation?".format(slot.restaurant)
    else:
        return "Sorry that's not a valid restaurant number, please select 1, 2 or 3"

def enquiry_handler(text):
    entity = PredictNer(text)
    
    # check_identified_entities(entity, enq)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(enq)
    slot_needed = slot.check_enq()

    if slot_needed:
        return get_enq_response(slot_needed)

    else:
        intent.update_intent('reservation')
        result, error_state = get_enquiry(slot)
        return result

def reservation_handler(text):    
    if slot.reservation_required == 0:
        # check how we entered here
        if slot.result is None:
            # we came in directly
            slot.reservation_required = 1
        
        else:
            # we came in from enquiry or recommendation
            # check if we want to make a reservation
            return check_reservation_choice(text)
    
    entity = PredictNer(text)
    
    # check_identified_entities(entity, res)
    check_identified_entities(entity, slot)
    # slot_needed = check_unfilled_entities(res)
    slot_needed = slot.check_res()
    

    if slot_needed:
        return get_res_response(slot_needed)

    else:
        intent.reset_intent()
        result, error_state = get_reservation(slot)
        return result

def check_reservation_choice(text):
    # hardcoded for now, replace with ner?
    if text.lower().find("yes") > -1:
        slot.reservation_required = 1
        return reservation_handler(text)
    
    else:
        intent.reset_intent()
        slot.clear_slots()
        return "Okay! Is there anything else I can help you with?"

def check_identified_entities(in_dict, ref):
    # check for which entities have yet to be identified
    # return bot response to get the missing entities
    ref_keys = set(vars(ref).keys())
    in_keys = set(in_dict.keys())
    shared_keys = in_keys.intersection(ref_keys)
    
    if slot.restaurant_choice == 1:
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
        return "What type of meal is this (e.g. breakfast, lunch, dinner)?"
    if text == 'price':
        return "Alright, do you have a budget in mind?"
    if text == 'rating':
        return "How good of a restaurant (e.g. 1-5 stars)?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_enq_response(text):
    if text == 'restaurant':
        return "Okay, what restaurant would you like to know about?"
    else:
        return "Sorry I don't understand what you mean, could you rephrase that please?"

def get_res_response(text):
    if text == 'restaurant':
        return "Okay, which restaurant would you like to make a reservation for?"
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
    df = similar_resto(slot.food_type, top_n = 20)
    df.to_csv('rec_top_n.csv')

    result = "Sorry, we did not manage to locate any restaurants that match your query"
    if df is None:
        error_state = 1
        # return result, error_state
    # print(len(df.index))
    # is resto open?
    ## check if open on that day
    # df = df.loc[df[slot.get_weekday()].dropna().index]
    # print(len(df.index))
    # ## check if open at that timing
    # df = df[df.index.isin(restaurant_open(df[slot.get_weekday()], slot.get_mealtime()))]
    # print(len(df.index))
    else:

        print(df.head())

        df['score'] = df['similarity']
        df['similarity'] = df['similarity'].apply(lambda x: int(x*100)/100)
        df['Sentiment_mean'] = df['Sentiment_mean'].apply(lambda x: int(x*100)/100)
        
        # multiplied stars by sentiment, so here i sort by the final product
        df = df.sort_values(by=['similarity', 'Sentiment_mean', 'stars'], ascending = False)
        print(df.head())

        # check if open at that timing
        df1 = df[df.index.isin(restaurant_open(df[slot.get_weekday()], str(slot.get_mealtime())))]
    
        # is resto within budget?
        df1 = df1[df1['PriceRange'].isin(slot.get_budget())]

        if len(df1.index) == 0:
            error_state = 2
    
        else:
            slot.result = df1[['name', 'categories']].sample(3)
            # result = build_rec_response(slot.result.to_csv(index = False), slot)
            result = build_rec_response(slot.result, slot)
        
    return result, error_state
        # return df[:5]

def get_enquiry(slot):
    error_state = 0
    result = "Sorry, we couldn't find that restaurant!"
    df = load_resto()
    get_fields=['name', 'address', 'hours', 'categories']

    if df is None:
        error_state = 1
    else:
        rest_list = [n.lower() for n in slot.restaurant]
        df = df[df.name.str.lower().isin(rest_list)]
        df = df.sort_values(by = ['score'], ascending = False).head(1)
        slot.result = df[get_fields]
        if len(slot.result.index) == 0:
            error_state = 2
        else:
            result = build_enq_response(slot.result.values.tolist(), slot)
    return result, error_state

def get_reservation(slot):
    error_state = 0
    result = "Sorry, we couldn't find that restaurant!"
    df = load_resto()
    if df is None:
        error_state = 1
    else:
        rest_list = [n.lower() for n in slot.restaurant]
        df = df[df.name.str.lower().isin(rest_list)]
        df = df[df.index.isin(restaurant_open(df[slot.get_weekday()], str(slot.get_mealtime())))]
        df = df[df.name.str.lower().isin(rest_list)]
        if len(df.index) == 0:
            error_state = 2
            result = "Sorry, this restaurant isn't open at that time!"
        else:
            result = build_res_response(df.to_csv(index = False), slot)
    return result, error_state

def restaurant_open(series, list):
    open_list = []
    series_idx = series.index
    for idx, item in enumerate(series):
        if check_mealtime(str(item)[1:], list[1:]):
            open_list.append(series_idx[idx])
    return open_list

#  [print(index) if e1 == e2 for index, (e1,e2) in enumerate(zip(list(i), list(j)))]

def check_mealtime(list_1, list_2):
    is_open = False
    for index, (e1, e2) in enumerate(zip(list_1, list_2)):
        if e1 == e2:
            if int(e1) == 1:
                is_open = True
        # print(is_open)
    return is_open

def format_rec_response(s):
    # s_list = s.split("\r\n")[1:-1]
    # print(s_list)
    # s_list = [element.split(",\"") for element in s_list]
    # print(s_list)
    # s_list = [[m.replace("\"","") for m in n] for n in s_list]
    # print(s_list)
    # return s_list

    return [[resto, category] for (resto, category) in zip(s['name'], s['categories'])]

def format_enq_response(s):
    s_list = s.split("\r\n")[1:-1]
    # print(s_list)
    s_list = [element.split(",\"") for element in s_list]
    # print(s_list)
    s_list = [[m.replace("\"","") for m in n] for n in s_list]
    # print(s_list)
    return s_list

def build_rec_response(s, slot):
    start = "We found the following restaurants that match {}<br/><br/>".format(slot.food_type)
    ss = ""
    end = '<br/>Which number of restaurant would you prefer? (type "more" for other options!)'

    for i, n in enumerate(format_rec_response(s)):
        ss = ss + "{}.&ensp;{}&emsp;&emsp;[{}]<br/>".format(i+1, n[0], n[1])
    return start+ss+end

def build_enq_response(s, slot):
    start = "Here are the details for {}<br/><br/>".format(slot.restaurant)
    ss = ""
    end = "<br/>Would you like to make a reservation?"
    # for i, n in enumerate(format_enq_response(s)):
        # ss = ss + "{}.&ensp;{}&emsp;&emsp;[{}]<br/>".format(i+1, n[0], n[1])
    ss = "Address:&ensp;{}<br/>Opening Hours:&ensp;{}<br/>Categories:&ensp;{}<br/>".format(slot.result.address[0], slot.result.hours[0], slot.result.categories[0])
    return start+ss+end

def build_res_response(s, slot):
    start = "Success! You have made a reservation at {}<br/>".format(slot.restaurant)
    ss = "for {} at {} for {} guests.".format(slot.get_date(), slot.get_time(), slot.num_guests)
    end = "<br/>We hope you have a great meal!"

    return start+ss+end
# setattr(slot, 'food_type', ['sashimi'])
# bot_response("are there any good salmon sashimi restaurants under 30 for dinner tomorrow at 7pm?")

