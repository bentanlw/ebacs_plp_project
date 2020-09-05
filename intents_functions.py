def process_input(text):
    return ' '.join(text.lower().strip('; ').split())

def process_input2(text):
    text = text.lower() # form variable name
    text = text.strip('; ')
    text = ' '.join(text.split())
    return text

class Intents:
    def __init__(self):
        self.current_intent = None

    def update_intent(self, new_intent):
        self.current_intent = new_intent

    def reset_intent(self):
        self.current_intent = None