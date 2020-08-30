def process_input(text):
    return ' '.join(text.lower().strip('; ').split())

def process_input2(text):
    text = text.lower() # form variable name
    text = text.strip('; ')
    text = ' '.join(text.split())
    return text
