#%%
import re
from nltk import word_tokenize
import pandas as pd

### Helper functions ###

def hasNumbers(string):
    """Returns True if the string contains a number."""
    return any(char.isdigit() for char in string)


def load_dic(path="data/german.dic", encoding="ISO-8859-1"):
    """Returns a set with german dictionary words.
    
    Args:
        path (string): Path to the dic-file.
        encoding (string): Name of the Encoding.
    Returns:
        Set with german dictionary words.    
    """
    #detects the encoding of the file if the encoding is unknown
    if encoding == "unknown":
        import chardet
        rawdata = open(path, 'rb').read()
        result = chardet.detect(rawdata)
        encoding = result['encoding']
    
    with open(path, "r", encoding=encoding, errors="ignore") as dic: 
        germandic = [word[:-1] for word in dic]
    return set(germandic)


def find_foreign_phrase(string, dic=load_dic()):
    """Finds the foreign phrase in front of the parentheses, removes everything
        before the phrase and returns the leftover.
    
    Args:
        string (string): Sentence or phase as string.
        dic (set): Set with dictionary words as strings.
    Returns:
        String without the words before the foreign phrase in front of the
        parantheses.'
    """
    foreign_words = []
    for idx, word in enumerate(word_tokenize(string)):
        if word in dic or word.capitalize() in dic or word.lower() in dic:
            pass
        else:
            special_regex = re.compile('[@_!#$%^&*()<>?/\|}{~:"\'`.]')
            if special_regex.search(word) == None:
                foreign_words.append((word, idx))
    lw = 0
    last_phrase_word = ""
    for idx, tupel in enumerate(foreign_words[::-1]):
        if idx != 0:
            if (lw - tupel[1]) >= 2:
                break
        last_phrase_word = tupel[0]
        lw = tupel[1]
        
    return string[string.find(last_phrase_word):]

### postprocessing functions ###
  
    
def remove_nonlatin(text):
    """Removes non-latin characters and replaces some non-latin characters 
        with latin equivalents.
    
    Args:
        text (string): String with non-latin substrings.
    Returns:
        String with removed non-latin characters.        
    """
    new_text = re.sub('„', '"', text)
    new_text = re.sub('“', '"', new_text)
    new_text = re.sub('”', '"', new_text)
    new_text = re.sub('‚', "'", new_text)
    new_text = re.sub('‘', "'", new_text)
    new_text = re.sub('’', "'", new_text)
    new_text = re.sub('–', '-', new_text)
    new_text = re.sub('‒', '-', new_text)
    new_text = re.sub('−', '-', new_text)
    nonlatin = re.compile('[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\u2020]')
    new_text = re.sub(nonlatin,  "", new_text)
    
    return new_text

def remove_doubleequalsigns(string):
    """Removes the doubled equal from a string."""
    return re.sub("== .*? ==|==", "", string)

def replace_foreign_phrase(text, dic=load_dic()):
    """Removes foreign terms or phrases when their german translation is given 
        in parantheses.
    
    Args:
        text (string): String of a Wikipedia article.
        dic (set): Set with dictionary words as strings.
    Returns:
        String without the foreign terms or phrases 
        but their german translation instead.
    """
    # matches 15 words or quotation in front of the parantheses
    regex = re.compile("((?:(\w+\s+|\w+')){1,15}\(((d|D)eutsch:|zu (d|D)eutsch).*?\)|\"([^\"]*)\" \(((d|D)eutsch:|zu (d|D)eutsch):.*?\))")
    original_and_translation = regex.search(remove_nonlatin(text))
    
    if original_and_translation != None:
        original = re.search("^.*?\(", original_and_translation.group()).group()[:-1]
        
        if re.search("\"([^\"]*)\"", original) == None:
            original = find_foreign_phrase(original, dic)
        
        paranthesis = re.search("\(((d|D)eutsch:|zu (d|D)eutsch).*?\)", original_and_translation.group())
        if paranthesis != None:
            translation = re.sub("\(((d|D)eutsch:|zu (d|D)eutsch). |\)", "", paranthesis.group())
        
        return text[:text.find(original)] + translation + text[text.find(paranthesis.group()) + len(paranthesis.group()):]
    else:
        return text


def replace_umlauts(text):
    """Replaces german umlauts in a string.
    
    Args:
        text (string): String with umlaut-substrings.
    Returns:
        String with replaced umlaut-substrings
    """
    replaced_text = text.replace('ä', 'ae')
    replaced_text = replaced_text.replace('ö', 'oe')
    replaced_text = replaced_text.replace('ü', 'ue')
    replaced_text = replaced_text.replace('Ä', 'Ae')
    replaced_text = replaced_text.replace('Ö', 'Oe')
    replaced_text = replaced_text.replace('Ü', 'Ue')
    replaced_text = replaced_text.replace('ß', 'ss')
    
    return replaced_text


def tokenize(text):
    """Splits the text into tokens."""
    return " ".join(word_tokenize(text))


def unify_articles_amount(df, columns=["category", "length", "text"]):
    """Takes a DataFrame with the column 'category', finds the minimum value
        of the number of articles per category and unifies the amount of 
        articles per category based on the minimum value.
        
    Args:
        df (DataFrame): DataFrame with the column 'category'.
        columns (list): List of the column names.
    Returns:
        DataFrame with an unified amount of articles per category.
    """
    d = df["category"].value_counts().to_dict()
    min_value = d[min(d, key=d.get)]
    
    actual_category = ""
    new_df = pd.DataFrame(columns=columns)
    df = df.sort_values(by=["category"])
    for idx, category in enumerate(df["category"]):
        if actual_category != category:
            actual_category = category
            new_df = new_df.append(df.loc[df["category"] == category][0:min_value], sort=False)
    
    return new_df.drop_duplicates()
    