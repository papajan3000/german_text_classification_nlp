#%%
import wikipediaapi
from nltk import word_tokenize
from src.data_generation import parserutils
import pandas as pd
import numpy as np
import json
from pathlib import Path
import argparse
import logging
import sys
import time
import datetime


### wikipediaapi logging handler ###

wikipediaapi.log.setLevel(level=wikipediaapi.logging.WARNING)
out_hdlr = wikipediaapi.logging.StreamHandler(sys.stderr)
out_hdlr.setFormatter(wikipediaapi.logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(wikipediaapi.logging.WARNING)
wikipediaapi.log.addHandler(out_hdlr)


### wikiparser logging handler ###

logging.basicConfig(level=logging.INFO, filename="wikiparser.log", filemode="w")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s: %(message)s")
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


#%%


def main():   
    ### loading categories from JSON-file ###
    with Path(args.path).open('r', encoding="utf-8") as f:
        wikicategories = json.load(f)
        logging.info(f"Successfully loaded the categories from the JSON-File.")
    
    ### hyperparams ###
    wikipedia = wikipediaapi.Wikipedia('de', extract_format
                                       =wikipediaapi.ExtractFormat.WIKI)
    unnecessary_sections = ["Literatur", "Weblinks", 
                            "Einzelnachweis", "Einzelnachweise", "Siehe auch"]
    
    
    if len(wikicategories) <= 10:
        csv_name = "data/smallwikicorpus"
    elif len(wikicategories) > 10 and len(wikicategories) <= 50:
        csv_name = "data/wikicorpus"
    else:
        csv_name = "data/bigwikicorpus"
        
    #TODO: eleganterer Weg?
    if args.save_date:
        now = datetime.datetime.now()
        if now.minute < 10:
            minute = f"0{now.minute}"
        else:
            minute = now.minute
        if now.month < 10:
            month = f"0{now.month}"
        else:
            month = now.month
        year = str(now.year)[2:]
        csv_name += f" ({now.day}.{month}.{year}_{now.hour}:{minute}).csv"
    else:
        csv_name += ".csv"
        
    
    st = time.time()
    
    
    
    ### generating categories dictionary ###
    
    #TODO: max articles argparse
    #TODO: cutting articles to 200
    if args.max_articles is not None:
        max_articles = args.max_articles
    else:
        max_articles=240
    categories = parserutils.generate_categories(wikipedia,
                                                      wikicategories,
                                                      unnecessary_sections,
                                                      max_articles=max_articles)
    logging.info(f"Successfully generated lists of the articles (time: {int((time.time() - st) / 60)} minutes).")
    
    ### generating dataframe and saving csv###
    
    df = pd.DataFrame([v for k, v in categories.items()])
    logging.info(f"Successfully generated the dataframe (time: {int((time.time() - st))} seconds).")
    
    df.to_csv(f"{csv_name}")

    logging.info(f"Successfully saved the articles to the csv file '{csv_name}' (time: {int((time.time() - st))} seconds).")
    logging.info(f"Total runtime: {np.around((time.time() - st) / 60, decimals=2)} minutes.")
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog="wikiparser", description="Tool to create a corpus of Wikipedia articles based on Wikipedia categories.")
    parser.add_argument("--path", "-p", help="Path to the JSON-File which contains the dictionary of the Wikipedia categories.")
    parser.add_argument("--tokenization", "-t", type=bool, help="Indicates if the articles should be tokenized or not.")
    parser.add_argument("--only_german", "-g", type=bool, help="Indicates if given german translations should replace the original phrases.")
    parser.add_argument("--no_latin", "-l", type=bool, help="Indicates if non-latin characters should be removed.")
    parser.add_argument("--no_umlauts", "-u", type=bool, help="Indicates if umlauts should be replaced.")
    parser.add_argument("--postprocessing", "-pp", type=bool, help="Indicates if general postprocessing should be applied.")
    parser.add_argument("--max_articles", "-ma", type=int, help="Sets the maximum of articles per category.")
    parser.add_argument("--save_date", "-sd", action="store_true", help="Indicates if the generation date of the corpus should be saved.")
    args = parser.parse_args()
    #TODO: bearbeite arguments
    #TODO: birth death dates wieder rausnehmen
    
    

    ### main ###
    main()


#%%
"""
    OLD
"""
"""

#%%
#####
# dropping duplicates and reducing the count of every article per catgory to 200
#####
df = df.drop_duplicates("summary")
df["category"].value_counts()

# only 200 articles per category
actual_category = ""
new_df = pd.DataFrame(columns=dfcolumns)
for idx, category in enumerate(df["category"]):
    if actual_category != category:
        actual_category = category
        print(actual_category)
        new_df = new_df.append(df.loc[df["category"] == category][0:200])
        

new_df.to_csv("data/corpora/wikicatcorpus_v2.csv", index=False)
#%%
#####
# postprocessing and creation of different corpus variants
#####


## everything removed##
# no doubleequalsigns, only german translation, remove birth-death-dates, no non latin #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_1 = postprocessing.corpus_postprocessing(df)
df_v3_1.to_csv("data/corpora/wikicatcorpus_v3_1.csv", index=False)
# no doubleequalsigns, only german translation, remove birth-death-dates, no non latin, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_1t = postprocessing.corpus_postprocessing(df, tokenization=True)
df_v3_1t.to_csv("data/corpora/wikicatcorpus_v3_1t.csv", index=False)
# no doubleequalsigns, only german translation, remove birth-death-dates, no non latin, replaces umlauts #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_1u = postprocessing.corpus_postprocessing(df, replacing_umlauts=True)
df_v3_1u.to_csv("data/corpora/wikicatcorpus_v3_1u.csv", index=False)
# no doubleequalsigns, only german translation, remove birth-death-dates, no non latin, replaces umlauts, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_1tu = postprocessing.corpus_postprocessing(df, tokenization=True, replacing_umlauts=True)
df_v3_1tu.to_csv("data/corpora/wikicatcorpus_v3_1tu.csv", index=False)

## no german translation inside parantheses ##
# no doubleequalsigns, remove birth-death-dates, no non latin #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_2 = postprocessing.corpus_postprocessing(df, only_german=False)
df_v3_2.to_csv("data/corpora/wikicatcorpus_v3_2.csv", index=False)
# no doubleequalsigns, remove birth-death-dates, no non latin, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_2t = postprocessing.corpus_postprocessing(df, tokenization=True, only_german=False)
df_v3_2t.to_csv("data/corpora/wikicatcorpus_v3_2t.csv", index=False)
# no doubleequalsigns, remove birth-death-dates, no non latin, replaces umlauts #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_2u = postprocessing.corpus_postprocessing(df, only_german=False, replacing_umlauts=True)
df_v3_2u.to_csv("data/corpora/wikicatcorpus_v3_2u.csv", index=False)
# no doubleequalsigns, remove birth-death-dates, no non latin, replaces umlauts, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_2tu = postprocessing.corpus_postprocessing(df, tokenization=True, only_german=False, replacing_umlauts=True)
df_v3_2tu.to_csv("data/corpora/wikicatcorpus_v3_2tu.csv", index=False)


## no removed birth death dates ##
# no doubleequalsigns, only german translation, no non latin #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_3 = postprocessing.corpus_postprocessing(df, birth_death_dates=False)
df_v3_3.to_csv("data/corpora/wikicatcorpus_v3_3.csv", index=False)
# no doubleequalsigns, only german translation, no non latin, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_3t = postprocessing.corpus_postprocessing(df, tokenization=True, birth_death_dates=True)
df_v3_3t.to_csv("data/corpora/wikicatcorpus_v3_3t.csv", index=False)
# no doubleequalsigns, only german translation, no non latin, replaces umlauts #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_3u = postprocessing.corpus_postprocessing(df, birth_death_dates=False, replacing_umlauts=True)
df_v3_3u.to_csv("data/corpora/wikicatcorpus_v3_3u.csv", index=False)
# no doubleequalsigns, only german translation, no non latin, replaces umlauts, tokenized text #
df = pd.read_csv("data/corpora/wikicatcorpus_v2.csv")
df_v3_3tu = postprocessing.corpus_postprocessing(df, tokenization=True, birth_death_dates=True, replacing_umlauts=True)
df_v3_3tu.to_csv("data/corpora/wikicatcorpus_v3_3tu.csv", index=False)
"""
