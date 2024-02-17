import re

# function for cleaning articles and extracting text
def clean_article(text):
    
    # cleaning html tags from text
    clean_text = re.sub(r'<[^<>]*>', '', text)

    # cleaning http links
    clean_text = re.sub(r'http\S+ | \n', ' ', clean_text)
    
    # cleaning emoji
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    
    clean_text = emoji_pattern.sub(r'', clean_text)
    
    # storing words in list with no extra spaces
    clean_text_with_no_extra_spaces = [j for j in clean_text.split(" ") if j !=""]
    

    return " ".join(clean_text_with_no_extra_spaces)



