import spacy
from pathlib import Path
from timefhuman import timefhuman

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
        self.date = None
        self.time = None
        # self.reserve_name = None
        self.num_guests = None

class Slots:
    def  __init__(self):
        self.food_type = None
        self.meal_type = None
        self.price = None
        self.rating = 4
        self.restaurant = None
        self.date = None
        self.time = None
        self.reserve_name = None
        self.num_guests = None

    def check_rec(self):
        if self.food_type == None:
            return "food_type"
        if self.meal_type == None:
            return "meal_type"
        if self.price == None:
            return "price"
        if self.rating == None:
            return "rating"

    def check_enq(self):
        if self.restaurant == None:
            return "restaurant"
    
    def check_res(self):
        if self.date == None:
            return "date"
        if self.time == None:
            return "time"
        if self.reserve_name == None:
            return "reserve_name"
        if self.num_guests == None:
            return "num_guests"

    def get_date(self):
        dt = timefhuman(self.date)
        return dt.strftime('%d%m%y')

    def get_weekday(self):
        dt = timefhuman(self.date)
        return dt.weekday()

    def get_time(self):
        dt = timefhuman(self.time)
        return dt.strftime('%H%M')

    def get_mealtime(self):
        #figure out which mealtime slot the time fits into
        #breakfast is 6-11am
        breakfast_range = range(600,1100)
        #brunch is 10-12pm
        brunch_range = range(1000,1200)
        #lunch is 11-4pm
        lunch_range = range(1100,1600)
        #dinner is 4-12am
        dinner_range = range(1600,2400)
        
        time = int(self.get_time())
        mealtime = 10000

        if time in breakfast_range:
            mealtime += 1
        if time in brunch_range:
            mealtime += 10
        if time in lunch_range:
            mealtime += 100
        if time in dinner_range:
            mealtime += 1000
        
        return mealtime

slot = Slots()
setattr(slot, 'time', '10:15am')