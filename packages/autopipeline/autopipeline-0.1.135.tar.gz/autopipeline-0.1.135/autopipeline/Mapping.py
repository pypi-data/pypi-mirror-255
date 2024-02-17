import openai
import os
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
import textstat
import re
import csv
import ast
from PIL import Image
from gensim import corpora, models
from nltk.tokenize import word_tokenize
from summarizer import Summarizer
import json
import copy
from flair.models import SequenceTagger
from flair.data import Sentence
from textblob import TextBlob
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

from importlib import resources

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# print(openai.api_key)

OPENAI_ORGANIZATION = "org-5rFbX7p7v2H4Sk1C8xb17aea"
os.environ["OPENAI_ORG"] = OPENAI_ORGANIZATION
openai.organization=os.environ["OPENAI_ORG"]

def check_alias(enum, all_description, new_description):
    # print(enum)
    # print(all_description)
    # print(new_description)
    messages = [
        {
            "role": "system",
            "content": '''The user is going to provide you with the following:
            (1) Existing table columns;
            (2) Detailed description for each existing column;
            (3) Detailed description for the new column to be added;
            '''
            + 
            '''Your task is to check whether there already exists a column in the given table that contains the EXACTLY same information as the column to be added.
                If yes, you should reply with that specific column; if no, you should reply with an empty string.
                In either cases, you should provide the rationale.
                Your output format can ONLY be "True"/"False" + "#" + "{column name}"/"" + "#{rationale}"
                '''
        },
        {
            "role": "user",
            "content": '''Existing table columns: ['text']'''  
            + '''. The detailed description for each existing column: 'text' column contains the posts to be analyzed; '''
            + '''. The detailed description for the new column to be added: 'text_emotion' column provides emotion identified from the 'text' column. IMPORTANT: emotion values of the 'text_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'.'''
        },
        {
            "role": "assistant",
            "content": "False##The description for the new column does not match any of the existing columns.",
        },
        {
            "role": "user",
            "content": '''Existing table columns: ['text', 'text_emotion']'''  
            + '''. The detailed description for each existing column: 'text' column contains the posts to be analyzed; 'text_emotion' column provides emotion identified from the 'text' column. IMPORTANT: emotion values of the 'text_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'; '''
            + '''. The detailed description for the new column to be added: 'text_sentiment' column is the sentiment of the content of the 'text' column. IMPORTANT: sentiment values of 'text_sentiment' column can only be either 'pos', 'neg', or 'other'.'''
        },
        {
            "role": "assistant",
            "content": "False##Although 'emotion' and 'sentiment' seem to be of same meaning, they (1) are not EXACTLY the same, and (2) have different values. Thus, the description for the new column does not match any of the existing columns.",
        },
        {
            "role": "user",
            "content": '''Existing table columns: ['text', 'headline', 'text_emotion']'''  
            + '''. The detailed description for each existing column: 'text' column contains the posts to be analyzed; 'text_emotion' column provides emotion identified from the 'text' column. IMPORTANT: emotion values of the 'text_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'; '''
            + '''. The detailed description for the new column to be added: 'headline_emotion' column provides emotion identified from the 'headline' column. IMPORTANT: emotion values of the 'headline_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'. '''
        },
        {
            "role": "assistant",
            "content": "False##The new column contains emotion from the 'headline' column, while the existing column contains emotion from the 'text' column. Thus, the description for the new column does not match any of the existing columns.",
        },
        {
            "role": "user",
            "content": '''Existing table columns: ['text', 'emotion']'''  
            + '''. The detailed description for each existing column: 'text' column contains the posts to be analyzed; 'emotion' column provides emotion identified from the 'text' column. IMPORTANT: emotion values of the 'emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'; '''
            + '''. The detailed description for the new column to be added: 'text_emotion' column provides emotion identified from the 'text' column. IMPORTANT: emotion values of the 'text_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'. '''
        },
        {
            "role": "assistant",
            "content": "True#emotion#The new column 'text_emotion' to be added contains exactly the same information as the existing 'emotion' column.",
        },
        {
            "role": "user",
            "content": '''Existing table columns: ''' + str(enum) 
            + '''. The detailed description for each existing column: ''' + all_description 
            + '''. The detailed description for the new column to be added: ''' + new_description
        }
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4-0613",
        messages=messages,
    )
    res = response.choices[0].message['content']
    print(res)
    res_ls = res.split("#")
    if res_ls[0] != "True":
        return ""
    return res_ls[1]

def base_table_gen(filename=None): 
    # If no filename is specified, use the packaged data
    if filename is None:
        # Open the file as a file-like object using resources.open_text
        with resources.open_text('autopipeline.data', 'base.csv') as file:
            base_table = pd.read_csv(file)
    else:
        # If a filename is specified, read from that file
        base_table = pd.read_csv(filename)
    enum = base_table.columns.tolist()
    description = "'id' column is the document ID, starts with 0; 'pdf_orig' column is the path to the pdf file of the document file; "
    return base_table, enum, description

def get_hate(table, column, enum, description):
    # if os.path.exists("data/implicit_hate_v1_stg1_posts.tsv"):
    #     df = pd.read_csv("data/implicit_hate_v1_stg1_posts.tsv", delimiter='\t')
    #     table[column+'_hate'] = df['class']
    # else:
    #     table[column+'_hate'] = "Undefined"
    new_description = "'"+column+"_hate' column contains 'explicit_hate', 'implicit_hate', or 'not_hate' as values to indicate whether the '"+column+"' column' contains hate speech - "+"IMPORTANT: both 'implicit_hate' and 'explicit_hate' imply that the '"+column+"' column contains hate speech; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/hate_full.tsv"):
        df = pd.read_csv("data/hate_full.tsv", delimiter='\t')
        table[column+'_hate'] = df['class']
    else:
        table[column+'_hate'] = "Undefined"
    enum.append(column+"_hate")
    description += " " + "'"+column+"_hate' column contains 'explicit_hate', 'implicit_hate', or 'not_hate' as values to indicate whether the '"+column+"' column' contains hate speech - "+"IMPORTANT: both 'implicit_hate' and 'explicit_hate' imply that the '"+column+"' column contains hate speech; "
    return table, enum, description

def get_hate_class(table, column, enum, description):
    # if os.path.exists("data/implicit_hate_v1_stg2_posts.tsv"):
    #     df = pd.read_csv("data/implicit_hate_v1_stg2_posts.tsv", delimiter='\t')
    #     table[column+'_implicit_hate_class'] = df['implicit_class']
    # else:
    #     table[column+'_implicit_hate_class'] = "Undefined"
    new_description = "'"+column+"_implicit_hate_class' column provides implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_class' column can only be one of 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/hate_full.tsv"):
        df = pd.read_csv("data/hate_full.tsv", delimiter='\t')
        table[column+'_implicit_hate_class'] = df['implicit_class']
    else:
        table[column+'_implicit_hate_class'] = "Undefined"
    enum.append(column+"_implicit_hate_class")
    description += " " + "'"+column+"_implicit_hate_class' column provides implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_class' column can only be one of 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'; "
    return table, enum, description

def get_hate_target(table, column, enum, description):
    # if os.path.exists("data/implicit_hate_v1_stg2_posts.tsv"):
    #     df = pd.read_csv("data/implicit_hate_v1_stg2_posts.tsv", delimiter='\t')
    #     table[column+'_implicit_hate_class'] = df['implicit_class']
    # else:
    #     table[column+'_implicit_hate_class'] = "Undefined"
    new_description = "'"+column+"_implicit_hate_target' column provides the target of implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_target' column are free label texts, and thus it's more preferrable to use partial or fuzzy comparisons; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/hate_full.tsv"):
        df = pd.read_csv("data/hate_full.tsv", delimiter='\t')
        table[column+'_implicit_hate_target'] = df['target']
    else:
        table[column+'_implicit_hate_target'] = "Undefined"
    enum.append(column+"_implicit_hate_target")
    description += " " + "'"+column+"_implicit_hate_target' column provides the target of implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_target' column are free label texts, and thus it's more preferrable to use partial or fuzzy comparisons; "
    return table, enum, description

def get_hate_implied(table, column, enum, description):
    # if os.path.exists("data/implicit_hate_v1_stg2_posts.tsv"):
    #     df = pd.read_csv("data/implicit_hate_v1_stg2_posts.tsv", delimiter='\t')
    #     table[column+'_implicit_hate_class'] = df['implicit_class']
    # else:
    #     table[column+'_implicit_hate_class'] = "Undefined"
    new_description = "'"+column+"_implicit_hate_implied' column provides the implied statement of implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_implied' column are free label texts, and thus it's more preferrable to use partial or fuzzy comparisons; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/hate_full.tsv"):
        df = pd.read_csv("data/hate_full.tsv", delimiter='\t')
        table[column+'_implicit_hate_implied'] = df['implied_statement']
    else:
        table[column+'_implicit_hate_implied'] = "Undefined"
    enum.append(column+"_implicit_hate_implied")
    description += " " + "'"+column+"_implicit_hate_implied' column provides the implied statement of implicit hate speech identified from the '"+column+"' column' - "+"IMPORTANT: the values of '" +column+"_implicit_hate_implied' column are free label texts, and thus it's more preferrable to use partial or fuzzy comparisons; "
    return table, enum, description

def get_misinfo(table, column, enum, description):
    def misinfo(document):
        MODEL = "jy46604790/Fake-News-Bert-Detect"
        clf = pipeline("text-classification", model=MODEL, tokenizer=MODEL)
        result = clf(document)
        if result[0]['label'] == 'LABEL_0':
            return 'misinfo'
        else:
            return 'real'
    new_description = "'"+column+"_misinfo' column provides information about whether the '"+column+"' column' contains misinformation (i.e., fake contents) - "+"IMPORTANT: the values of '" +column+"_misinfo' column can only be either 'misinfo' or 'real': 'misinfo' means the '"+column+"' column contains misinformation; 'real' means the content of the '"+column+"' column is real; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/test_annot_all.tsv"):
        df = pd.read_csv("data/test_annot_all.tsv", delimiter='\t')
        table[column+'_misinfo'] = df['gold_label']
    else:
        table[column+'_misinfo'] = table[column].apply(misinfo)
    enum.append(column+"_misinfo")
    description += " " + "'"+column+"_misinfo' column provides information about whether the '"+column+"' column' contains misinformation (i.e., fake contents) - "+"IMPORTANT: the values of '" +column+"_misinfo' column can only be either 'misinfo' or 'real': 'misinfo' means the '"+column+"' column contains misinformation; 'real' means the content of the '"+column+"' column is real; "
    return table, enum, description

def get_emotion(table, column, enum, description):
    def emotion(document):
        # Load the tokenizer and model from Hugging Face Hub
        tokenizer = AutoTokenizer.from_pretrained("nateraw/bert-base-uncased-emotion")
        model = AutoModelForSequenceClassification.from_pretrained("nateraw/bert-base-uncased-emotion")

        # Create a pipeline for emotion classification
        emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

        res = emotion_classifier(document)

        return res['label']
    
    new_description = "'"+column+"_emotion' column provides emotion identified from the '"+column+"' column'."+"IMPORTANT: emotion values of '" +column+"_emotion' column can only be either 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/merged_training.pkl"):
        df = pd.read_pickle("data/merged_training.pkl")
        table[column+'_emotion'] = df['emotions']
    else:
        table[column+'_emotion'] = table[column].apply(emotion)
    description += " " + "'"+column+"_emotion' column provides emotion identified from the '"+column+"' column'."+"IMPORTANT: emotion values of '" +column+"_emotion' column can only be either 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'; "

    # new_description = "'"+column+"_emotion' column provides emotion identified from the '"+column+"' column'."+"IMPORTANT: emotion values of '" +column+"_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'; "
    # col = check_alias(enum, description, new_description)
    # if len(col) > 0:
    #     return table, enum, description
    # if os.path.exists("data/emotion_trigger.tsv"):
    #     df = pd.read_csv("data/emotion_trigger.tsv", delimiter='\t')
    #     table[column+'_emotion'] = df['emotion']
    # else:
    #     table[column+'_emotion'] = table[column].apply(emotion)
    # description += " " + "'"+column+"_emotion' column provides emotion identified from the '"+column+"' column'."+"IMPORTANT: emotion values of '" +column+"_emotion' column can only be either 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'; "
    enum.append(column+"_emotion")
    return table, enum, description

def get_trigger(table, column, emotion, enum, description):
    assert emotion.endswith('emotion')
    new_description = "'"+column+"_trigger' column provides trigger identified from column '"+column+"' that triggers the emotion as described in the '"+emotion+"'."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/emotion_trigger.tsv"):
        df = pd.read_csv("data/emotion_trigger.tsv", delimiter='\t')
        table[column+'_trigger'] = df['trigger']
    else:
        table[column+'_trigger'] = 'Undefined'
    description += " " + "'"+column+"_trigger' column provides trigger identified from column '"+column+"' that triggers the emotion as described in the '"+emotion+"'."
    enum.append(column+"_trigger")
    return table, enum, description

def get_condition(user_query, table, column, enum, description):
    def class_gpt(document):
        messages = [
            {
                "role": "system",
                "content": "Given a text: " + document 
                + ''', Your task is to check whether the text satisfies the condition(s) listed in the user query.
                    If it satisfies, you should output "True"; else, you should output "False".
                    IMPORTANT: No contents other than "True"/"False" are allowed to be output.
                    '''
            },
            {
                "role": "user",
                "content": user_query  # Use the user's query
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="gpt-4-0613",
            messages=messages,
        )
        res = response.choices[0].message['content']
        if res != "True" and res != "False":
            res = "Undefined"
        return res
    
    new_description = "'"+column+"_class' column provides whether the content in the '"+column+"' column satisfies the conditions of the user query ('True'/'False'/'Undefined'): "+ user_query+";"
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description

    table[column+'_class'] = table[column].apply(class_gpt)
    enum.append(column+"_class")
    description += " " + "'"+column+"_class' column provides whether the content in the '"+column+"' column satisfies the conditions of the user query ('True'/'False'/'Undefined'): "+ user_query+";"
    return table, enum, description


def pdf_to_text(table, column, enum, description):
    def ocr(pdf_path):
        # Open the PDF file
        # with resources.path('autopipeline.data', pdf_file_name) as pdf_path:
        #     pdf_document = fitz.open(pdf_path)
        pdf_document = fitz.open(pdf_path)

        # Initialize an empty string to store text
        text = ""

        # Iterate over pages
        for page_number in range(pdf_document.page_count - 4):
            # Get the page
            page = pdf_document[page_number]

            # Convert the page to an image
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            # Perform OCR on the image
            page_text = pytesseract.image_to_string(image, lang='eng')

            ls = page_text.split("\n\n")

            ls = ls[1:]

            ls = [line.replace("\n", " ") for line in ls]

            page_text = '\n'.join(ls)

            # Append the extracted text to the overall text
            text += page_text

        # Close the PDF document
        pdf_document.close()

        # print(text)

        return text
    
    def pdf_extract(pdf_path):
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Initialize an empty string to store text
        text = ""

        # Iterate over pages
        for page_number in range(pdf_document.page_count):
            # Get the page
            page = pdf_document[page_number]

            # Get text from the page
            page_text = page.get_text("text")

            # Append the extracted text to the overall text
            text += page_text

        # Close the PDF document
        pdf_document.close()

        # print(text)

        return text
    
    new_description = "'"+column+"_text' column is the plain text content of the '" + column +"' column; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    table[column+'_text'] = table[column].apply(ocr)
    enum.append(column+'_text')
    description += " "+"'"+column+"_text' column is the plain text content of the '" + column +"' column; "
    return table, enum, description

# break into paragraphs: this might pose challenge in our mapping since every row might have different number
# "I want to know the attitude of MORITZ, Circuit Judge"
def para_sep(table, column, enum, description):
    def sep(row):
        # Tokenize and preprocess the document
        paragraphs = [paragraph.strip() for paragraph in row[column].split('\n') if paragraph.strip()]
        rows = []
        for para_id, paragraph in enumerate(paragraphs):
            new_row = copy.deepcopy(row)
            new_row[column+'_segment'] = paragraph
            new_row[column+'_segmentid'] = para_id
            rows.append(new_row)
        res = pd.DataFrame(rows)
        #print(res)
        return res
    new_description = f"'{column}_segment' column stores the paragraph segments of the '" + column +"column', the original text has empty value; "
    col0 = check_alias(enum, description, new_description)
    if len(col0) == 0:
        # Apply the function to each row and collect the results in a list
        result_df = pd.concat(table.apply(lambda row: sep(row), axis=1).tolist())
        table[column+'_segment'] = ""
        table = pd.concat([table, result_df[column+'_segment']])
        enum.append(column+'_segment')
        description += " "+f"'{column}_segment' column stores the paragraph segments of the '" + column +"column', the original text has empty value; "

    new_description = f"'{column}_segmentid' column stores the paragraph index according to the order of the '" + column +"_segment' column, starts with 0, and the original text has value -1 (should be removed when performing functions related to paragraphs); "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if len(col0) != 0:
        result_df = pd.concat(table.apply(lambda row: sep(row), axis=1).tolist())
    table[column+'_segmentid'] = -1
    # Concatenate the original DataFrame and the result
    table = pd.concat([table, result_df[column+'_segmentid']])
    enum.append(column+'_segmentid')
    description += " "+f"'{column}_segmentid' column stores the paragraph index according to the order of the '" + column +"_segment' column, starts with 0, and the original text has value -1 (should be removed when performing functions related to paragraphs); "

    # # Apply the sep function to the specified column
    # segments = table[column].apply(sep)

    # # Create new columns for each segment
    # for i in range(len(segments[0])):
    #     col_name = f"{column}_segment{i + 1}"
    #     enum.append(column+'_segment'+str(i+1))
    #     description += " "+f"'{column}_segment{i + 1}' column is the {i+1}-th segment of the '" + column +"' column; "
    #     table[col_name] = segments.apply(lambda x: x[i] if i < len(x) else None)

    return table, enum, description

def get_ner(table, column, enum, description):
    def ner(row):
        document = row[column]
        # Load the pre-trained Flair NER model for English
        ner_model = SequenceTagger.load('ner')

        # Create a Flair Sentence
        sentence = Sentence(document)

        # Run NER on the sentence
        ner_model.predict(sentence)

        rows = []

        for entity in sentence.get_spans('ner'):
            new_row = copy.deepcopy(row)
            new_row[column+'_ner_type'] = entity.get_labels()[0].value
            new_row[column+'_ner_val'] = entity.text
            rows.append(new_row)
        res = pd.DataFrame(rows)
        #print(res)
        return res
    
    new_description = "'"+column+"_ner_type' column gives the type of the name entities recognized (NER) in the "+column+" column. IMPORTANT: all the NER in the '" +column+"_ner_type' column are in the form of three letters: 'PER' (person), 'LOC' (location), 'GPE' (geopolitical entities), etc."
    col0 = check_alias(enum, description, new_description)
    if len(col0) == 0:
        # Apply the function to each row and collect the results in a list
        result_df = pd.concat(table.apply(lambda row: ner(row), axis=1).tolist())
        table[column+'_ner_type'] = ""
        table = pd.concat([table, result_df[column+'_ner_type']])
        enum.append(column+'_ner_type')
        description += " "+"'"+column+"_ner_type' column gives the type of the name entities recognized (NER) in the "+column+" column. IMPORTANT: all the NER in the '" +column+"_ner_type' column are in the form of three letters: 'PER' (person), 'LOC' (location), 'GPE' (geopolitical entities), etc."

    new_description = "'"+column+"_ner_val' column gives the value of the name entities recognized (NER) in the "+column+" column. e.g. 'UNITED STATES', 'MOHAMED BAK'."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if len(col0) != 0:
        result_df = pd.concat(table.apply(lambda row: ner(row), axis=1).tolist())
    table[column+'_ner_val'] = ""
    # Concatenate the original DataFrame and the result
    table = pd.concat([table, result_df[column+'_ner_val']])
    enum.append(column+'_ner_val')
    description += " "+"'"+column+"_ner_val' column gives the value of the name entities recognized (NER) in the "+column+" column. e.g. 'UNITED STATES', 'MOHAMED BAK'."
    return table, enum, description

def get_summary(table, column, enum, description):
    def summary(document):
        # Create a BERT Extractive Summarizer
        bertsum_model = Summarizer()
        # Summarize the legal document
        if isinstance(document, list):
            summary = [bertsum_model(doc) for doc in document]
        else:
            summary = bertsum_model(document)
        return summary
    assert column == "story_orig"
    new_description = "'"+column+"_summary' column provides summaries of the '"+column+"' column;"
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    
    if os.path.exists("data/story.csv"):
        df = pd.read_csv('data/story.csv')
        table[column+'_summary'] = df['summary']
    else:
        table[column+'_summary'] = table[column].apply(summary)
    enum.append(column+"_summary")
    description += " " + "'"+column+"_summary' column provides summaries of the '"+column+"' column;"
    return table, enum, description

def get_fk(table, column, enum, description):
    def fk(document):
        return textstat.flesch_kincaid_grade(document)

    table[column+'_fk'] = table[column].apply(fk)
    enum.append(column+"_fk")
    description += " " + "'"+column+"_fk' column calculates the Flesch-Kincaid (F-K) readability score of the '"+column+"' column, with a higher score representing lower readability;"
    return table, enum, description

def get_ttr(table, column, enum, description):
    def ttr(document):
        tokens = re.findall(r'\b\w+\b', document.lower())
        types = set(tokens)
        ttr = len(types) / len(tokens) if tokens else 0
        return ttr

    table[column+'_ttr'] = table[column].apply(ttr)
    enum.append(column+"_ttr")
    description += " " + "'"+column+"_ttr' column calculates the Type-Token Ratio (TTR) of the '"+column+"' column, with a higher score representing greater lexical diversity;"
    return table, enum, description

def get_similarity(table, column, enum, description, primary_id, secondary_id):
    def similarity(doc1):
        # Locate the document in the table using doc_id and para_id
        doc2 = table.loc[(table['id'] == int(primary_id)) & (table[column+'id'] == int(secondary_id)), column].values[0]
        
        # If doc2 is not found or empty, return 0
        if not doc2:
            return 0

        vectorizer = TfidfVectorizer()

        # Vectorize the documents
        tfidf_matrix = vectorizer.fit_transform([doc1, doc2])

        # Calculate cosine similarity
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

        return sim[0][0]

    # Apply the similarity function to each row in the specified column
    table[column + '_similarity_' + str(primary_id) + '_' + str(secondary_id)] = table[column].apply(similarity)

    # Update the enum and description
    enum.append(column + '_similarity_' + str(primary_id) + '_' + str(secondary_id))
    description += f" '{column}_similarity_{primary_id}_{secondary_id}' column calculates the cosine similarity between the '{column}' column of all the documents and the reference document specified by id={primary_id} and {column}_id={secondary_id};"

    return table, enum, description

def get_keyword(table, column, enum, description):
    def lda(document):
        if document == "":
            return ""
        # Preprocessing the document
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in word_tokenize(document.lower()) if word.isalpha() and word not in stop_words]
        
        # Creating a dictionary and corpus for LDA
        dictionary = corpora.Dictionary([tokens])
        corpus = [dictionary.doc2bow(tokens)]

        # Applying LDA model
        lda_model = models.LdaModel(corpus, num_topics=1, id2word=dictionary, passes=10)

        # Extracting keywords from the topic
        topic_words = lda_model.show_topic(0, topn=5)
        keywords = [word for word, _ in topic_words]
        return ', '.join(keywords)
    
    new_description = " '" + column + "_keyword' column provides LDA-based keyword identification of the '" + column + "' column;"
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description

    table[column+'_keyword'] = table[column].apply(lda)
    enum.append(column+"_keyword")
    description += " '" + column + "_keyword' column provides LDA-based keyword identification of the '" + column + "' column;"

    return table, enum, description

def get_sentiment(table, column, enum, description):
    def sentiment(document):
        blob = TextBlob(document)
        polarity = blob.sentiment.polarity
        
        if polarity > 0:
            return 'Positive'
        elif polarity < 0:
            return 'Negative'
        else:
            return 'Neutral'
    new_description = "'"+column+"_sentiment' column is the sentiment of the content of the '" + column +"' column. IMPORTANT: sentiment values of '" +column+"_sentiment' column can only be either 'pos', 'neg', or 'other'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/stance.csv"):
        with open("data/stance.csv", mode='r') as file:
            reader = csv.reader(file)
            data = list(reader)
        df = pd.DataFrame(data[1:], columns=data[0])
        table[column+'_sentiment'] = df['Sentiment']
    else:
        table[column+'_sentiment'] = table[column].apply(sentiment)
    enum.append(column+"_sentiment")
    # description += " "+"'"+column+"_sentiment' column is the sentiment of the content of the '" + column +"' column. IMPORTANT: sentiment values of '" +column+"_sentiment' column can only be either 'Positive', 'Negative', or 'Neutral'; "
    description += " "+"'"+column+"_sentiment' column is the sentiment of the content of the '" + column +"' column. IMPORTANT: sentiment values of '" +column+"_sentiment' column can only be either 'pos', 'neg', or 'other'; "
    #description += " Correct Example: table[table['"+column+"_sentiment'] == 'Positive']; Incorrect Example: table[table['"+column+"_sentiment'] == 'positive']; "
    return table, enum, description

def get_stance(table, column, target, enum, description):   
    assert target == 'Target'
    new_description = "'"+column+"_stance' column describes the stance of the content of the '" + column +"' column towards the target topic in the '"+target+"' column. IMPORTANT: stance values of '" +column+"_stance' column can only be either 'AGAINST', 'FAVOR', or 'NONE'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/stance.csv"):
        with open("data/stance.csv", mode='r') as file:
            reader = csv.reader(file)
            data = list(reader)
        df = pd.DataFrame(data[1:], columns=data[0])
        table[column+'_stance'] = df['Stance']
    else:
        table[column+'_stance'] = "Undefined"
    enum.append(column+"_stance")
    description += " "+"'"+column+"_stance' column describes the stance of the content of the '" + column +"' column towards the target topic in the '"+target+"' column. IMPORTANT: stance values of '" +column+"_stance' column can only be either 'AGAINST', 'FAVOR', or 'NONE'; "
    return table, enum, description

def get_dog_whistle(table, column, enum, description):
    new_description = "'"+column+"_dog_whistle' column is the dog whistle term extracted from the '" + column +"' column."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/dogwhistle.tsv"):
        df = pd.read_csv("data/dogwhistle.tsv", on_bad_lines='skip', delimiter='\t')
        table[column+'_dog_whistle'] = df['Dogwhistle']
    else:
        table[column+'_dog_whistle'] = "Undefined"
    enum.append(column+"_dog_whistle")
    description += " "+"'"+column+"_dog_whistle' column is the dog whistle term extracted from the '" + column +"' column."
    return table, enum, description

def get_dog_whistle_persona_ingroup(table, column, enum, description):
    assert column == 'Linguistic Context_dog_whistle'
    new_description = "'"+column+"_persona_ingroup' contains the persona/in-group of the dog whistle term in the '" + column +"' column."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/dogwhistle.tsv"):
        df = pd.read_csv("data/dogwhistle.tsv", on_bad_lines='skip', delimiter='\t')
        table[column+'_persona_ingroup'] = df['Persona/In-Group']
    else:
        table[column+'_persona_ingroup'] = "Undefined"
    enum.append(column+"_persona_ingroup")
    description += " "+"'"+column+"_persona_ingroup' contains the persona/in-group of the dog whistle term in the '" + column +"' column."
    # description += "IMPORTANT: the persona/in-group value can only be one of 'transphobic', 'white supremacist', 'antisemitic', 'racist', 'anti-Latino', 'climate change denier', 'religious', 'conservative', 'Islamophobic', 'anti-vax', 'anti-Asian', 'anti-liberal', 'homophobic', 'anti-LGBTQ', 'liberal', 'misogynistic', 'xenophobic', or 'anti-GMO'; "
    return table, enum, description

def get_dog_whistle_type(table, column, enum, description):
    assert column == 'Linguistic Context_dog_whistle'
    new_description = "'"+column+"_type' contains the type of the dog whistle term in the '" + column +"' column. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/dogwhistle.tsv"):
        df = pd.read_csv("data/dogwhistle.tsv", on_bad_lines='skip', delimiter='\t')
        table[column+'_type'] = df['Type']
    else:
        table[column+'_type'] = "Undefined"
    enum.append(column+"_type")
    description += " "+"'"+column+"_type' contains the type of the dog whistle term in the '" + column +"' column. "
    #description += "IMPORTANT: the type value can only be one of 'persona signal (shared culture)', 'persona signal (self-referential)', 'persona signal (symbol)', 'arbitrary target group label', 'concept (policy)', 'stereotype-based target group label', 'humor/mockery/sarcasm', 'concept (values)', 'representative (Bogeyman)', 'concept (other)', 'phonetic-based target group label', 'stereotype-based descriptor', 'persona signal (in-group label)'; "
    return table, enum, description

def get_positive_reframing(table, column, enum, description):
    new_description = "'"+column+"_pr' contains the positive reframing version of the '" + column +"' column. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/positive-reframing.csv"):
        df = pd.read_csv('data/positive-reframing.csv')
        table[column+'_pr'] = df['positive_reframing']
    else:
        table[column+'_pr'] = "Undefined"
    enum.append(column+"_pr")
    description += " "+"'"+column+"_pr' contains the positive reframing version of the '" + column +"' column. "
    return table, enum, description

def get_premise(table, column, type, term, enum, description):
    assert type == 'type'
    assert term == 'term'

    new_description = "'"+column+"_premise_entail' contains the premises (literal texts) that entail the hypothesis (figurative texts) contained in the '" + column +"' column. "
    col = check_alias(enum, description, new_description)
    if len(col) == 0:
        if os.path.exists("data/figurative.csv"):
            df = pd.read_csv('data/figurative.csv')
            table[column+'_premise_entail'] = df['premise_e']
        else:
            table[column+'_premise_entail'] = "Undefined"
        enum.append(column+'_premise_entail')
        description += " "+"'"+column+"_premise_entail' contains the premises (literal texts) that entail the hypothesis (figurative texts) contained in the '" + column +"' column. "
    
    new_description = "'"+column+"_premise_contradict' contains the premises (literal texts) that contradict the hypothesis (figurative texts) contained in the '" + column +"' column. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/figurative.csv"):
        df = pd.read_csv('data/figurative.csv')
        table[column+'_premise_contradict'] = df['premise_c']
    else:
        table[column+'_premise_contradict'] = "Undefined"
    enum.append(column+'_premise_contradict')
    description += " "+"'"+column+"_premise_contradict' contains the premises (literal texts) that contradict the hypothesis (figurative texts) contained in the '" + column +"' column. "
    return table, enum, description

def get_premise_explanation(table, column, hypothesis, type, term, label, enum, description):
    assert hypothesis == 'hypothesis'
    assert label in ["contradict", "entail"]
    assert label in column
    assert type == 'type'
    assert term == 'term'

    if label == "contradict":
        new_description = "'"+column+"_explanation' contains the explanation of the premises (literal texts) that contradict the hypothesis (figurative texts) contained in the '" + column +"' column. "
        col = check_alias(enum, description, new_description)
        if len(col) > 0:
            return table, enum, description
        if os.path.exists("data/figurative.csv"):
            df = pd.read_csv('data/figurative.csv')
            table[column+'_explanation'] = df['explanation_c']
        else:
            table[column+'_explanation'] = "Undefined"
        enum.append(column+'_explanation')
        description += " "+"'"+column+"_explanation' contains the explanation of the premises (literal texts) that contradict the hypothesis (figurative texts) contained in the '" + column +"' column. "
    else:
        new_description = "'"+column+"_explanation' contains the explanation of the premises (literal texts) that entail the hypothesis (figurative texts) contained in the '" + column +"' column. "
        col = check_alias(enum, description, new_description)
        if len(col) > 0:
            return table, enum, description
        if os.path.exists("data/figurative.csv"):
            df = pd.read_csv('data/figurative.csv')
            table[column+'_explanation'] = df['explanation_e']
        else:
            table[column+'_explanation'] = "Undefined"
        enum.append(column+'_explanation')
        description += " "+"'"+column+"_explanation' contains the explanation of the premises (literal texts) that entail the hypothesis (figurative texts) contained in the '" + column +"' column. "

    return table, enum, description

def get_change_opinion(table, column, enum, description):
    new_description = "'"+column+"_change_opinion' contains the whether the post in the '" + column +"' column is persuaded and changed their opinion. IMPORTANT: the '"+column+"_change_opinion' column contains boolean values, where True for posts that changed their opinion, False for posts that do not change their opinion."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/persuasive.jsonlist"):
        df = pd.read_json('data/persuasive.jsonlist', lines=True)
        table[column+'_change_opinion'] = df['delta_label']
    else:
        table[column+'_change_opinion'] = "Undefined"
    enum.append(column+'_change_opinion')
    description += " "+"'"+column+"_change_opinion' contains the whether the post in the '" + column +"' column is persuaded and changed their opinion. IMPORTANT: the '"+column+"_change_opinion' column contains boolean values, where True for posts that changed their opinion, False for posts that do not change their opinion."
    return table, enum, description

def get_persuasion_effect(table, column, enum, description):
    new_description = "'"+column+"_persuasion_effect' contains the persuasion effects of the post included in the '" + column +"' column. IMPORTANT: the '"+column+"_persuasion_effect' column contains numerical values ranging from 0.0 to 1.0, where 0.0 stands for the least persuasive, and 1.0 stands for the most persuasive."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/persuasive-17.csv"):
        df = pd.read_csv('data/persuasive-17.csv')
        table[column+'_persuasion_effect'] = df['persuasion_effect']
    else:
        table[column+'_persuasion_effect'] = "Undefined"
    enum.append(column+"_persuasion_effect")
    description += " "+"'"+column+"_persuasion_effect' contains the persuasion effects of the post included in the '" + column +"' column. IMPORTANT: the '"+column+"_persuasion_effect' column contains numerical values ranging from 0.0 to 1.0, where 0.0 stands for the least persuasive, and 1.0 stands for the most persuasive."
    return table, enum, description

def get_intent(table, column, enum, description):
    assert column == 'headline'
    new_description = "'"+column+"_intent' column provides writers' intent for the texts in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/test_annot_all.tsv"):
        df = pd.read_csv("data/test_annot_all.tsv", delimiter='\t')
        table[column+'_intent'] = df['writer_intent']
    else:
        table[column+'_intent'] = "Undefined"
    enum.append(column+"_intent")
    description += " " + "'"+column+"_intent' column provides writers' intent for the texts in the '"+column+"' column'; "
    return table, enum, description

def get_reader_perception(table, column, enum, description):
    assert column == 'headline'
    new_description = "'"+column+"_reader_perception' column provides readers' perceptions for the texts in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/test_annot_all.tsv"):
        df = pd.read_csv("data/test_annot_all.tsv", delimiter='\t')
        table[column+'_reader_perception'] = df['effect_on_reader']
    else:
        table[column+'_reader_perception'] = "Undefined"
    enum.append(column+"_reader_perception")
    description += " " + "'"+column+"_reader_perception' column provides readers' perceptions for the texts in the '"+column+"' column'; "
    return table, enum, description

def get_spread_likelihood(table, column, enum, description):
    assert column.endswith('_reader_perception')
    new_description = "'"+column+"_spread' column contains the (numerical) likelihood to spread based on the reader perceptions provided in the '"+column+"' column'; IMPORTANT: the '"+column+"_spread' column contains numerical values ranging from 0.0 to 5.0, where 0.0 stands for the least likely to spread, and 5.0 stands for the most likely to spread."
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/test_annot_all.tsv"):
        df = pd.read_csv("data/test_annot_all.tsv", delimiter='\t')
        table[column+'_spread'] = df['spread']
    else:
        table[column+'_spread'] = "Undefined"
    enum.append(column+"_spread")
    description += " " + "'"+column+"_spread' column contains the (numerical) likelihood to spread based on the reader perceptions provided in the '"+column+"' column'; IMPORTANT: the '"+column+"_spread' column contains numerical values ranging from 0.0 to 5.0, where 0.0 stands for the least likely to spread, and 5.0 stands for the most likely to spread."
    return table, enum, description

def get_reader_action(table, column, enum, description):
    assert column.endswith('_intent')
    new_description = "'"+column+"_reader_action' column contains the inferred readers' actions based on the writers' intent provided in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/test_annot_all.tsv"):
        df = pd.read_csv("data/test_annot_all.tsv", delimiter='\t')
        table[column+'_reader_action'] = df['reader_action']
    else:
        table[column+'_reader_action'] = "Undefined"
    enum.append(column+"_reader_action")
    description += " " + "'"+column+"_reader_action' column contains the inferred readers' actions based on the writers' intent provided in the '"+column+"' column'; "
    return table, enum, description

def get_dialect(table, column, enum, description):
    new_description = "'"+column+"_dialect' column contains the identified categorical dialect features identified from the sentences in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/dialect.csv'):
        df = pd.read_csv('data/dialect.csv')
        table[column+'_dialect'] = df['dialect']
    else:
        table[column+'_dialect'] = "Undefined"
    enum.append(column+"_dialect")
    description += " " + "'"+column+"_dialect' column contains the identified categorical dialect features identified from the sentences in the '"+column+"' column'; "
    return table, enum, description

def get_disclosure(table, column, enum, description):
    new_description = "'"+column+"_disclosure' column contains the disclosure act types of the sentences in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/disclosure.csv'):
        df = pd.read_csv('data/disclosure.csv')
        table[column+'_disclosure'] = df['disclosure']
    else:
        table[column+'_disclosure'] = "Undefined"
    enum.append(column+"_disclosure")
    description += " " + "'"+column+"_disclosure' column contains the disclosure act types of the sentences in the '"+column+"' column'; "
    return table, enum, description

def get_semantic(table, word, word_type, index, sentence1, sentence2, enum, description):
    assert word == "word"
    assert word_type == "word_type"
    assert index == "index"
    assert sentence1 == "example_1"
    assert sentence2 == "example_2"

    new_description = "'"+word+"_semantic' column contains whether the word in the '"+word+"' column of type in the '"+word_type+" column'  has the same semantic in sentences in the '"+sentence1+"' column and the '"+sentence2+"' column, with indexes in the '"+index+"' column. IMPORTANT: the values in the '"+word+"_semantic' column can either be 'T', meaning that the semantic in the two sentences are the same, or 'F', meaning that the semantic in the two sentences are different. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/semantic.csv'):
        df = pd.read_csv('data/semantic.csv')
        table[word+'_semantic'] = df['semantic_consistency']
    else:
        table[word+'_semantic'] = "Undefined"
    enum.append(word+"_semantic")
    description += " " + "'"+word+"_semantic' column contains whether the word in the '"+word+"' column of type in the '"+word_type+" column'  has the same semantic in sentences in the '"+sentence1+"' column and the '"+sentence2+"' column, with indexes in the '"+index+"' column. IMPORTANT: the values in the '"+word+"_semantic' column can either be 'T', meaning that the semantic in the two sentences are the same, or 'F', meaning that the semantic in the two sentences are different. "
    return table, enum, description

def get_emotional_reaction_level(table, column, column_post, enum, description):
    assert column == "response_post"
    assert column_post == "seeker_post"
    new_description = "'"+column+"_emotional_reaction' column contains the numerical level of communication strength in terms of emotional reaction for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_emotion_reaction' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/empathy.csv'):
        df = pd.read_csv('data/empathy.csv')
        table[column+'_emotional_reaction'] = df['emotional_reactions_level']
    else:
        table[column+'_emotional_reaction'] = "Undefined"
    enum.append(column+"_emotional_reaction")
    description += " " + "'"+column+"_emotional_reaction' column contains the numerical level of communication strength in terms of emotional reaction for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_emotion_reaction' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    return table, enum, description

def get_exploration_level(table, column, column_post, enum, description):
    assert column == "response_post"
    assert column_post == "seeker_post"
    new_description = "'"+column+"_exploration' column contains the numerical level of communication strength in terms of exploration for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_exploration' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/empathy.csv'):
        df = pd.read_csv('data/empathy.csv')
        table[column+'_exploration'] = df['exploration_level']
    else:
        table[column+'_exploration'] = "Undefined"
    enum.append(column+"_exploration")
    description += " " + "'"+column+"_exploration' column contains the numerical level of communication strength in terms of exploration for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_exploration' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    return table, enum, description

def get_intepretation_level(table, column, column_post, enum, description):
    assert column == "response_post"
    assert column_post == "seeker_post"
    new_description = "'"+column+"_intepretation' column contains the numerical level of communication strength in terms of intepretation for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_intepretation' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/empathy.csv'):
        df = pd.read_csv('data/empathy.csv')
        table[column+'_intepretation'] = df['intepretation_level']
    else:
        table[column+'_intepretation'] = "Undefined"
    enum.append(column+"_intepretation")
    description += " " + "'"+column+"_intepretation' column contains the numerical level of communication strength in terms of intepretation for the response post in the '"+column+"' column' towards the sad post in the '"+column_post+"' column. IMPORTANT: the numerical values in the '"+column+"_intepretation' column are integers 0, 1, and 2, with 0 denotes the weakest level of communication, and 2 denotes the strongest level of communication. "
    return table, enum, description

def get_politeness(table, column, enum, description):
    new_description = "'"+column+"_polite' column contains whether the text in the '"+column+"' column' is polite or not. IMPORTANT: the values in the '"+column+"_polite' column can only be either 'T', meaning that the text is polite, or 'F', meaning that the text is not polite. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/politeness.csv'):
        df = pd.read_csv('data/politeness.csv')
        table[column+'_polite'] = df['polite']
    else:
        table[column+'_polite'] = "Undefined"
    enum.append(column+"_polite")
    description += " " + "'"+column+"_polite' column contains whether the text in the '"+column+"' column' is polite or not. IMPORTANT: the values in the '"+column+"_polite' column can only be either 'T', meaning that the text is polite, or 'F', meaning that the text is not polite. "
    return table, enum, description

def get_humor(table, column, enum, description):
    new_description = "'"+column+"_humor' column contains whether the text in the '"+column+"' column' is funny or not. IMPORTANT: the values in the '"+column+"_humor' column can only be either 'T', meaning that the text is funny, or 'F', meaning that the text is not funny. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/humor.csv'):
        df = pd.read_csv('data/humor.csv')
        table[column+'_humor'] = df['humor']
    else:
        table[column+'_humor'] = "Undefined"
    enum.append(column+"_humor")
    description += " " + "'"+column+"_humor' column contains whether the jokes in the '"+column+"' column' is funny or not. IMPORTANT: the values in the '"+column+"_humor' column can only be either 'T', meaning that the joke is funny, or 'F', meaning that the joke is not funny. "
    return table, enum, description

def get_toxic(table, column, enum, description):
    new_description = "'"+column+"_toxic' column contains whether the text in the '"+column+"' column' will become toxic in the future or not. IMPORTANT: the values in the '"+column+"_toxic' column can only be either True, meaning that the text will become toxic in the future, or False, meaning that the text will not become toxic in the future. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/toxic.csv'):
        df = pd.read_csv('data/toxic.csv')
        table[column+'_toxic'] = df['toxic']
    else:
        table[column+'_toxic'] = "Undefined"
    enum.append(column+"_toxic")
    description += " " + "'"+column+"_toxic' column contains whether the text in the '"+column+"' column' will become toxic in the future or not. IMPORTANT: the values in the '"+column+"_toxic' column can only be either True, meaning that the text will become toxic in the future, or False, meaning that the text will not become toxic in the future. "
    return table, enum, description

def get_trope(table, column, enum, description):
    assert column == "Quotes"
    new_description = "'"+column+"_trope' column contains which trope type is the character who has the quotes in the '"+column+"' column'. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/tropes.csv'):
        df = pd.read_csv('data/tropes.csv')
        table[column+'_trope'] = df['TropesHuman']
    else:
        table[column+'_trope'] = "Undefined"
    enum.append(column+"_trope")
    description += " " + "'"+column+"_trope' column contains which trope type is the character who has the quotes in the '"+column+"' column'. "
    return table, enum, description

def get_event_argument(table, column, enum, description):
    new_description = "'"+column+"_event_argument' column contains the event arguments extracted from the text in the '"+column+"' column'; "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/event_argument.csv'):
        df = pd.read_csv('data/event_argument.csv')
        table[column+'_event_argument'] = df['event_argument']
    else:
        table[column+'_event_argument'] = "Undefined"
    enum.append(column+"_event_argument")
    description += " " + "'"+column+"_event_argument' column contains the event arguments extracted from the text in the '"+column+"' column'; "
    return table, enum, description

def get_ideology_doc(table, column, enum, description):
    new_description = "'"+column+"_ideology_doc' column contains the ideology of the document whose link is provided in the '"+column+"' column'; IMPORTANT: the categorical ideology values in the '"+column+"_ideology_doc' column can only be one of 0 (meaning left), 1 (meaning neutral), or 2 (meaning right). "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/ideology_document.tsv'):
        df = pd.read_csv("data/ideology_document.tsv", delimiter='\t')
        table[column+'_ideology_doc'] = df['bias']
    else:
        table[column+'_ideology_doc'] = "Undefined"
    enum.append(column+"_ideology_doc")
    description += " " + "'"+column+"_ideology_doc' column contains the ideology of the document whose link is provided in the '"+column+"' column'; IMPORTANT: the categorical ideology values in the '"+column+"_ideology_doc' column can only be one of 0 (meaning left), 1 (meaning neutral), or 2 (meaning right). "
    return table, enum, description

def get_ideology_sent(table, column, enum, description):
    new_description = "'"+column+"_ideology_sent' column contains the ideology of the sentence in the '"+column+"' column'; IMPORTANT: the categorical ideology values in the '"+column+"_ideology_sent' column can only be one of 'Conservative', 'Liberal', or 'Neutral'. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/ibc.csv'):
        df = pd.read_csv("data/ibc.csv")
        table[column+'_ideology_sent'] = df['leaning']
    else:
        table[column+'_ideology_sent'] = "Undefined"
    enum.append(column+"_ideology_sent")
    description += " " + "'"+column+"_ideology_sent' column contains the ideology of the sentence in the '"+column+"' column'; IMPORTANT: the categorical ideology values in the '"+column+"_ideology_sent' column can only be one of 'Conservative', 'Liberal', or 'Neutral'. "
    return table, enum, description

def story_gen(table, column, enum, description):
    assert column.endswith('_summary')
    new_description = "'"+column+"_new_story' column contains the generated stories based on the summary provided in the '" + column + "' column. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists("data/story.csv"):
        df = pd.read_csv('data/story.csv')
        table[column+'_new_story'] = df['story_gen']
    else:
        table[column+'_new_story'] = "Undefined"
    enum.append(column+"_new_story")
    description += " " + "'"+column+"_new_story' column contains the generated stories based on the summary provided in the '" + column + "' column. "
    return table, enum, description

def get_event(table, column, enum, description):
    assert column == 'sent'
    new_description = "'"+column+"_event_prob' column contains the probability of the text in the '"+column+"' column containing new events. IMPORTANT: the values in the '"+column+"_event_prob' column are floating point values ranging from 0.0 (the least likely to include events) to 1.0 (the most likely to include events). "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/events.csv'):
        df = pd.read_csv('data/events.csv')
        table[column+'_event_prob'] = df['eventOrNot']
    else:
        table[column+'_event_prob'] = "Undefined"
    enum.append(column+"_event_prob")
    description += " " + "'"+column+"_event_prob' column contains the probability of the text in the '"+column+"' column containing new events. IMPORTANT: the values in the '"+column+"_event_prob' column are floating point values ranging from 0.0 (the least likely to include events) to 1.0 (the most likely to include events). "
    return table, enum, description

def get_event_major(table, column, event, enum, description):
    assert event.endswith('_event_prob')
    assert column == 'sent'
    new_description = "'"+column+"_event_major_prob' column contains the probability of events in the text in the '"+column+"' column being major events. IMPORTANT: the values in the '"+column+"_event_major_prob' column are floating point values ranging from 0.0 (the least likely to include events) to the value in the '"+event+"' column (the most likely to include events). "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/events.csv'):
        df = pd.read_csv('data/events.csv')
        table[column+'_event_major_prob'] = df['majorBin']
    else:
        table[column+'_event_major_prob'] = "Undefined"
    enum.append(column+"_event_major_prob")
    description += " " + "'"+column+"_event_major_prob' column contains the probability of events in the text in the '"+column+"' column being major events. IMPORTANT: the values in the '"+column+"_event_major_prob' column are floating point values ranging from 0.0 (the least likely to include events) to the value in the '"+event+"' column (the most likely to include events). "
    return table, enum, description

def get_event_expected(table, column, event, enum, description):
    assert event.endswith('_event_prob')
    assert column == 'sent'
    new_description = "'"+column+"_event_expected_prob' column contains the probability of events in the text in the '"+column+"' column being events as expected. IMPORTANT: the values in the '"+column+"_event_expected_prob' column are floating point values ranging from 0.0 (the least likely to include events) to the value in the '"+event+"' column (the most likely to include events). "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/events.csv'):
        df = pd.read_csv('data/events.csv')
        table[column+'_event_expected_prob'] = df['expectedBin']
    else:
        table[column+'_event_expected_prob'] = "Undefined"
    enum.append(column+"_event_expected_prob")
    description += " " + "'"+column+"_event_expected_prob' column contains the probability of events in the text in the '"+column+"' column being events as expected. IMPORTANT: the values in the '"+column+"_event_expected_prob' column are floating point values ranging from 0.0 (the least likely to include events) to the value in the '"+event+"' column (the most likely to include events). "
    return table, enum, description

def get_story_type(table, column, storyIx, sentIx, event, event_major, event_expected, enum, description):
    assert column == 'sent'
    assert storyIx == 'storyIx'
    assert sentIx == 'sentIx'
    assert event.endswith('_event_prob')
    assert event_major.endswith('_event_major_prob')
    assert event_expected.endswith('_event_expected_prob')

    new_description = "'"+column+"_story_type' column contains the type of story in the text in the '"+column+"' column. IMPORTANT: the values in the '"+column+"_story_type' column are categorical values being one of 'imagined', 'recalled', or 'retold'. "
    col = check_alias(enum, description, new_description)
    if len(col) > 0:
        return table, enum, description
    if os.path.exists('data/events.csv'):
        df = pd.read_csv('data/events.csv')
        table[column+'_story_type'] = df['memType']
    else:
        table[column+'_story_type'] = "Undefined"
    enum.append(column+"_story_type")
    description += " " + "'"+column+"_story_type' column contains the type of story in the text in the '"+column+"' column. IMPORTANT: the values in the '"+column+"_story_type' column are categorical values being one of 'imagined', 'recalled', or 'retold'. "
    return table, enum, description

# using function call APIs
def schema_gpt(user_query, column_description, description):
    # Define the user's query as an argument
    functions = [
        {
            "name": "get_dog_whistle",
            "description": 
            ''' 
            This function takes in one of the columns as input, extract the dog whistle term in that column, and generate an additional column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column to extract dog whistle term, you have to select one in the 'enum' field to summarize based on the description: "+description,
                    "enum": column_description,
                }
                }
            },
            "required": ["column"]
        },
        {
            "name": "get_dog_whistle_persona_ingroup",
            "description": 
            ''' 
            This function takes in one of the columns of dog whistle terms, obtain the target persona/in-group of that dog whistle term, and generate an additional column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column of dog whistle terms to obtain the target persona/in-group, you have to select one in the 'enum' field to summarize based on the description: "+description,
                    "enum": column_description,
                }
                }
            },
            "required": ["column"]
        },
        {
            "name": "get_dog_whistle_type",
            "description": 
            ''' 
            This function takes in one of the columns of dog whistle terms, obtain the type of that dog whistle term, and generate an additional column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column of dog whistle terms to obtain the type, you have to select one in the 'enum' field to summarize based on the description: "+description,
                    "enum": column_description,
                }
                }
            },
            "required": ["column"]
        },
        # {
        #     "name": "para_sep",
        #     "description": "This function takes in one of the columns as input, split the text according to paragraphs, and generates an additional rows and columns to store the list of paragraphs.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "column": {
        #                 "type": "string",
        #                 "description": "The column to apply paragraph split. You have to select one column in the 'enum' field to apply paragraph-level split based on the description: "+description,
        #                 "enum": column_description
        #             }
        #         },
        #         "required": ["column"]
        #     }
        # },
        # {
        #     "name": "pdf_to_text",
        #     "description": 
        #     ''' 
        #     This function takes in one of the columns as input, transforms the pdf in that column into plain text, and generate an additional column to store the plain text. Don't select this if none of the columns match the user query.
        #     ''',
        #     "parameters": {
        #         "type": "object",
        #         "properties": {"column": {
        #             "type": "string",
        #             "description": "the column to apply pdf to text transformation, you have to select one column in the 'enum' field to apply pdf to text transformation based on the description: "+description,
        #             "enum": column_description,

        #         }
        #         }
        #     },
        #     "required": ["column"]
        # },
        # {
        #     "name": "get_summary",
        #     "description": 
        #     ''' 
        #     This function takes in one of the columns as input, summarizes the contents in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
        #     ''',
        #     "parameters": {
        #         "type": "object",
        #         "properties": {"column": {
        #             "type": "string",
        #             "description": "the column to summarize, you have to select one in the 'enum' field to summarize based on the description: "+description,
        #             "enum": column_description,
        #         }
        #         }
        #     },
        #     "required": ["column"]
        # },
        # {
        #     "name": "get_ner",
        #     "description": 
        #     ''' 
        #     This function takes in one of the columns as input, get the name entities recognized in that column, and generate additional rows and columns to include those.
        #     ''',
        #     "parameters": {
        #         "type": "object",
        #         "properties": {"column": {
        #             "type": "string",
        #             "description": "the column to apply NER analysis, you have to select one column in the 'enum' field to apply NER analysis based on the description: "+description,
        #             "enum": column_description,

        #         }
        #         }
        #     },
        #     "required": ["column"]
        # },
        # {
        #     "name": "get_fk",
        #     "description": 
        #     ''' 
        #     This function takes in one of the columns as input, get the Flesch-Kincaid (F-K) readability score of that column, and generate an additional columns to store the score.
        #     ''',
        #     "parameters": {
        #         "type": "object",
        #         "properties": {"column": {
        #             "type": "string",
        #             "description": "the column to calculate Flesch-Kincaid (F-K) readability score, you have to select one column in the 'enum' field to calculate F-K readability score based on the description: "+description,
        #             "enum": column_description,

        #         }
        #         }
        #     },
        #     "required": ["column"]
        # },
        # {
        #     "name": "get_ttr",
        #     "description": 
        #     ''' 
        #     This function takes in one of the columns as input, get the Type-Token Ratio (TTR) of that column, and generate an additional columns to store the score.
        #     ''',
        #     "parameters": {
        #         "type": "object",
        #         "properties": {"column": {
        #             "type": "string",
        #             "description": "the column to calculate Type-Token Ratio (TTR), you have to select one column in the 'enum' field to calculate TTR based on the description: "+description,
        #             "enum": column_description,

        #         }
        #         }
        #     },
        #     "required": ["column"]
        # },
        {
            "name": "get_trigger",
            "description": 
            ''' 
            This function takes in one column of text and one column of emotion class as input, extracts the trigger in the text column that triggers a specific emotion in the emotion class column, and generates a new column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column to extract triggering sentence for a specific emotion, you have to select one column in the 'enum' field based on the description: "+description,
                    "enum": column_description,
                },
                "emotion": {
                    "type": "string",
                    "description": "the column that describes emotion class, you have to select one column in the 'enum' field based on the description: "+description,
                    "enum": column_description,
                },

                }
            },
            "required": ["column", "emotion"]
        },
        {
            "name": "get_stance",
            "description": 
            ''' 
            This function takes in one column of text and one column of target topic as input, extracts the stance in the text column that towards the target topic, and generates a new column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column to identify stance towards the target topic, you have to select one column in the 'enum' field based on the description: "+description,
                    "enum": column_description,
                },
                "target": {
                    "type": "string",
                    "description": "the column that includes the target topic, you have to select one column in the 'enum' field based on the description: "+description,
                    "enum": column_description,
                },

                }
            },
            "required": ["column", "target"]
        },
        {
            "name": "get_keyword",
            "description": 
            ''' 
            This function takes in one of the columns as input, get the top 5 keywords recognized in that column, and generate an additional column to include those.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column to apply keyword recognition, you have to select one column in the 'enum' field to apply keyword recognition based on the description: "+description,
                    "enum": column_description,

                }
                }
            },
            "required": ["column"]
        },
        # {
        #     "name": "get_sentiment",
        #     "description": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'Positive', 'Negative', or 'Neutral'. Don't select this if none of the columns matches the user query.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "column": {
        #                 "type": "string",
        #                 "description": "The column to apply sentiment analysis. You have to select one column in the 'enum' field to apply sentiment analysis based on the description: "+description,
        #                 "enum": column_description
        #             }
        #         },
        #         "required": ["column"]
        #     }
        # },
        {
            "name": "get_sentiment",
            "description": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'pos', 'neg', or 'other'. Don't select this if none of the columns matches the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply sentiment analysis. You have to select one column in the 'enum' field to apply sentiment analysis based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_condition",
            "description": "This function takes in one of the columns as input, checks whether the contents of that column satisfy the conditions provided in the user query, and generates an additional column labeling the content as 'True' or 'False' or 'Undefined'. This function should only be called if all other functions cannot help to support user query. Don't select this if (1) there are other functions that can provide such a condition check or (2) there are no explicit conditions listed in the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to check conditions. You have to select one column in the 'enum' field to apply condition check based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        # {
        #     "name": "get_emotion",
        #     "description": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'. Don't select this if none of the columns matches the user query.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "column": {
        #                 "type": "string",
        #                 "description": "The column to apply emotion detection. You have to select one column in the 'enum' field to apply emotion classification based on the description: "+description,
        #                 "enum": column_description
        #             }
        #         },
        #         "required": ["column"]
        #     }
        # },
        {
            "name": "get_emotion",
            "description": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'. Don't select this if none of the columns matches the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply emotion detection. You have to select one column in the 'enum' field to apply emotion classification based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_misinfo",
            "description": "This function takes in one of the columns as input, applies misinformation detection on the content of that column, and generates an additional column labeling the content as 'misinfo' (misinformation detected) or 'real' (no misinformation detected).",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply misinformation detection. You have to select one column in the 'enum' field to apply misinformation detection based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_hate",
            "description": "This function takes in one of the columns as input, applies (high-level) hate speech detection on the content of that column, and generates an additional column labeling the content as 'implicit_hate', 'explicit_hate', or 'not_hate'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply (high-level) hate speech detection. You have to select one column in the 'enum' field to apply (high-level) hate speech detection based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_hate_class",
            "description": "This function takes in one of the columns as input, applies (fine-grained) implicit hate speech classification on the content of that column, and generates an additional column labeling the content as 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply (fine-grained) implicit hate speech classification. You have to select one column in the 'enum' field to apply (fine-grained) implicit hate speech classification based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_hate_target",
            "description": "This function takes in one of the columns as input, applies implicit hate speech target identification on the content of that column, and generates an additional column of free text labeling the target identified from the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply implicit hate speech target identification. You have to select one column in the 'enum' field to apply implicit hate speech target identification based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "get_hate_implied",
            "description": "This function takes in one of the columns as input, applies implicit hate speech implied statement extraction on the content of that column, and generates an additional column of free text labeling the implied statement extracted from the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply implicit hate speech implied statement extraction. You have to select one column in the 'enum' field to apply implicit hate speech implied statement extraction based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "null",
            "description": "This function should be called when the table already contains all the necessary information to complete the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The placeholder parameter. It can only be 'null'",
                        "enum": ["null"]
                    }
                },
                "required": ["column"]
            }
        }
    ]
    messages = [
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the PDF file in 'pdf_orig', and is not given the plain text of the document, thus the first function to apply is 'pdf_to_text' on the 'pdf_orig' column to get the plain text of the PDF file.",
            "function_call": {
                "name": "pdf_to_text",
                "arguments": "{\n  \"column\": \"pdf_orig\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the plain text of the PDF file in 'pdf_orig_text', and is not given the paragraph-wise segments of the document, thus the first function to apply is 'para_sep' on the 'pdf_orig_text' column to get the paragraph-level splits of the plain text.",
            "function_call": {
                "name": "para_sep",
                "arguments": "{\n  \"column\": \"pdf_orig_text\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the paragraphs of the PDF file in 'pdf_orig_text_segments', and is not given the sentimental analysis for the paragraphs, thus the first function to apply is 'get_sentiment' on the 'pdf_orig_text_segments' column to get the sentiment for the paragraphs.",
            "function_call": {
                "name": "get_sentiment",
                "arguments": "{\n  \"column\": \"pdf_orig_text_segment\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1; 'pdf_orig_text_segment_sentiment' column is the sentiment of the content of the 'pdf_orig_text_segment' column; "
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is already given the paragraph-level sentiment analysis in the 'pdf_orig_text_segment_sentiment' column. Thus the first function to apply is 'null' to end the function chain.",
            "function_call": {
                "name": "null",
                "arguments": "{\n  \"column\": \"null\"\n}"
            }
        },
        {
            "role": "user",
            "content": user_query  # Use the user's query
        }
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages,
        functions = functions,
        function_call = "auto",
    )

    return response.choices[0].message

def tree_path(user_query, columns, description, function_chain, function_list):
    function_tree = '''
    {
        "text_processors" <contains functions that process texts>:
            "para_sep": "This function takes in one of the columns as input, split the text according to paragraphs, and generates an additional rows and columns to store the list of paragraphs."
            "pdf_to_text": "This function takes in one of the columns as input, transforms the pdf in that column into plain text, and generate an additional column to store the plain text." 
        "augmentor" <contains functions that augment texts>:
            "story_gen": "This function takes in one of the columns of story summaries as input, generate a story based on the summaries in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_summary'."
        "summarizer" <contains functions that summarize texts>:
            "get_summary": "This function takes in one of the columns as input, summarizes the contents in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'story_gen'."
            "get_intent": "This function takes in one of the columns as input, retrieve the intent of the writer of text in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'get_reader_action'."
        "calculator" <contains functions that calculate numerical scores from text>:
            "continuous_calculator" <contains functions that calculate continuous numerical scores from text>:
                "get_persuasion_effect": "This function takes in one of the columns as input, calculates the (numerical) persuasion effect score of the contents in that column, and generate an additional column to include those."
                "get_spread_likelihood": "This function takes in one of the columns of readers' perceptions as input, calculates the (numerical) spread likelihood based on readers' perceptions in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_reader_perception'."
                "get_event": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain new events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'get_event_expected', this function has to be executed at least once before calling 'get_event_major', this function has to be executed at least once before calling 'get_story_type'."
                "get_event_major": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain major events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event', this function has to be executed at least once before calling 'get_story_type'."
                "get_event_expected": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain events that are as expected, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event', this function has to be executed at least once before calling 'get_story_type'."
            "discrete_calculator" <contains functions that calculate discrete numerical scores from text>:
                "get_emotional_reaction_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of emotional reaction for the contents in the response post column, and generate an additional column to include the integer level."
                "get_exploration_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of exploration for the contents in the response post column, and generate an additional column to include the integer level."
                "get_intepretation_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of intepretation for the contents in the response post column, and generate an additional column to include the integer level."
        "classifier" <contains functions that classify texts>:
            "binary_classifier" <contains functions that classify texts into binary (+ undefined if any) categories>:
                "get_misinfo": "This function takes in one of the columns as input, applies misinformation detection on the content of that column, and generates an additional column labeling the content as 'misinfo' (misinformation detected) or 'real' (no misinformation detected)."
                "get_change_opinion": "This function takes in one of the columns as input, classifies whether the contents in that column changes opinion, and generate an additional column to include those."
                "get_condition": "This function takes in one of the columns as input, checks whether the contents of that column satisfy the user query, and generates an additional column labeling the content as 'True' or 'False' or 'Undefined'."
                "get_semantic": "This function takes in a word, the type of the word, two sentences, and the indexes in the sentences as input, classifies whether the word in the two sentences has the same semantic, and generates an additional column that includes 'T' or 'F' accordingly."
                "get_humor": "This function takes in one of the columns as input, classifies whether the contents in that column is funny, and generate an additional column to include those."
                "get_polite": "This function takes in one of the columns as input, classifies whether the contents in that column is polite, and generate an additional column to include those."
                "get_toxic": "This function takes in one of the columns as input, classifies whether the contents in that column will become toxic in the future, and generate an additional column to include those."
            "ternary_classifier" <contains functions that classify texts into binary + neutral categories>:
                "get_stance": "This function takes in one column of text and one column of target topic as input, extracts the stance of 'AGAINST', 'FAVOR', or 'NONE' in the text column that towards the target topic, and generates a new column to include those."
                "get_sentiment": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'Positive', 'Negative', and/or 'Neutral'."
                "get_ideology_doc": "This function takes in one of the columns that contains the links to documents as input, applies document-level ideology classification on that column, and generates an additional column labeling the content as 0 (meaning left), 1 (meaning neutral), or 2 (meaning right)."
                "get_ideology_sent": "This function takes in one of the columns that contains texts as input, applies sentence-level ideology classification on that column, and generates an additional column labeling the content as 'Conservative', 'Liberal', or 'Neutral'."
            "multiple_classifier" <contains functions that classify texts into multiple (larger or equal to three meaningful) categories>:
                "get_dialect": "This function takes in one of the columns as input, classifies the dialect features identified from the content of that column, and generate an additional column to include those."
                "get_disclosure": "This function takes in one of the columns as input, classifies the content of that column into different disclosure acts, and generate an additional column to include those."
                "get_emotion": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'."
                "get_hate": "This function takes in one of the columns as input, applies (high-level) hate speech detection on the content of that column, and generates an additional column labeling the content as 'implicit_hate', 'explicit_hate', or 'not_hate'."
                "get_hate_class": "This function takes in one of the columns as input, applies (fine-grained) implicit hate speech classification on the content of that column, and generates an additional column labeling the content as 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'."
                "get_dog_whistle_persona_ingroup": "This function takes in one of the columns of dog whistle terms, obtain the target persona/in-group of that dog whistle term, and generate an additional column to include those."
                "get_dog_whistle_type": "This function takes in one of the columns of dog whistle terms, obtain the type of that dog whistle term, and generate an additional column to include those."
                "get_story_type": "This function takes in one column of sentence, one column of story index of where the sentence belong, one column of sentence index of that sentence, one column of the probability of the sentence containing new events, one column of probability of the sentence containing major new events, and one column of probabiliy of the sentence containing new events as expected as input, classifies the story type of the sentence into 'imagined', 'recalled', or 'retold', and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event', this function has to be executed after at least one call of 'get_event_major', this function has to be executed after at least one call of 'get_event_expected'."
                "get_trope": "This function takes in one of the columns that contains the quotes of a character as input, applies trope classification based on the content of the quotes, and generates an additional column to include those."
        "extractor" <contains functions that extract messages from text>:
            {
                "text_extractor" <contains functions that extract messages of text level, i.e., extracted messages are part (e.g. words/phrases/sentences/...) of the original words.>:
                    "get_ner": "This function takes in one of the columns as input, get the name entities recognized in that column, and generate additional rows and columns to include those.",
                    "get_keyword": "This function takes in one of the columns as input, get the top 5 keywords recognized in that column, and generate an additional column to include those.",
                    "get_trigger": "This function takes in one column of text and one column of emotion class as input, extracts the trigger in the text column that triggers a specific emotion in the emotion class column, and generates a new column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_emotion'."
                    "get_dog_whistle": "This function takes in one of the columns as input, extract the dog whistle term in that column, and generate an additional column to include those."
                    "get_event_argument": "This function takes in one of the columns as input, get the event arguments recognized in that column, and generate additional rows and columns to include those."
                "information_extractor" <contains functions that extract high-level messages based on actual conveyed information>:
                    "get_hate_target": "This function takes in one of the columns as input, applies implicit hate speech target identification on the content of that column, and generates an additional column of free text labeling the target identified from the content."
                    "get_hate_implied": "This function takes in one of the columns as input, applies implicit hate speech implied statement extraction on the content of that column, and generates an additional column of free text labeling the implied statement extracted from the content."
                    "get_positive_reframing": "This function takes in one of the columns as input, extract the positive aspects of the content of that column and transforms it into a positive reframing version, and generates an additional column of positive reframing version of the content."
                    "get_premise": "This function takes in one column of figurative text, one column of figurative type, and one column of figurative term as input, extracts the literal text, i.e., the premise, of the figurative text column, and generates a new column to include those."
                    "get_premise_explanation": "This function takes in one column of premise of figurative text, one column of the original figurative text, one column of figurative type, one column of figurative term as input, and one parameter labelling whether the premises entail or contract original figurative texts as input, extracts the explanations of literal texts, i.e., the premises, of the figurative text column, and generates a new column to include those."
                "causal_extractor" <contains functions that extract the causal relationships inferred from text>:
                    "get_reader_action": "This function takes in one of the columns of writers' intent as input, get the reader action inferred from the writers' intent of that column, and generate additional an column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_intent'."
                    "get_reader_perception": "This function takes in one of the columns as input, infers readers' perceptions of text in that column, and generates an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'get_spread_likelihood'."
            }
    }
    '''
    messages = [
        {
            "role": "system",
            "content": "Given a table with columns: " + str(columns) 
            + " where " + description 
            + " You are also given the function tree to be applied to different columns: " + function_tree 
            + '''Your task is:
                if there are function(s) needed to be applied, you should first identify which function to apply next, and then return the path of the group where the function to be applied next belongs;
                else, return an empty dictionary ({})

                Your output format can ONLY be a dictionary of two key elements: {"function": "{name of the function to be applied}", "path": {LIST of function tree path to the function in order}}.

                You should NOT include the function name as part of the path.
                '''
            + '''When selecting functions, you HAVE TO take the function chain and logic generated in the forward planning phase into consideration. '''
            #+function_chain+'''". Here are the functions that's already applied: '''+str(function_list)
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; The function chain I have is ['pdf_to_text', 'para_sep', 'get_sentiment'], current executed function chain is []."
        },
        {
            "role": "assistant",
            "content": "{'function': 'pdf_to_text', 'path': ['text_processors']}",
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; The function chain I have is ['pdf_to_text', 'para_sep', 'get_sentiment'], current executed function chain is ['pdf_to_text']."
        },
        {
            "role": "assistant",
            "content": "{'function': 'para_sep', 'path': ['text_processors']}",
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1; The function chain I have is ['pdf_to_text', 'para_sep', 'get_sentiment'], current executed function chain is ['pdf_to_text', 'para_sep']."
        },
        {
            "role": "assistant",
            "content": "{'function': 'get_sentiment', 'path': ['classifier']}",
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1; 'pdf_orig_text_segment_sentiment' column is the sentiment of the content of the 'pdf_orig_text_segment' column; The function chain I have is ['pdf_to_text', 'para_sep', 'get_sentiment'], current executed function chain is ['pdf_to_text', 'para_sep', 'get_sentiment']."
        },
        {
            "role": "assistant",
            "content": "{}",
        },
        {
            "role": "user",
            "content": "I want to get the top 5 keywords of texts in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; The function chain I have is ['pdf_to_text', 'para_sep', 'get_keyword'], current executed function chain is ['pdf_to_text', 'para_sep']."
        },
        {
            "role": "assistant",
            "content": "{'function': 'get_keyword', 'path': ['extractor', 'information_extractor']}",
        },
        {
            "role": "user",
            "content": user_query  # Use the user's query
        }
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages,
    )

    return response.choices[0].message['content']

def schema_gpt_tree(user_query, column_description, description, function_chain, function_list):
    tree = {
        "text_processor": [
            # {
            #     "name": "para_sep",
            #     "description": "This function takes in one of the columns as input, split the text according to paragraphs, and generates an additional rows and columns to store the list of paragraphs.",
            #     "parameters": {
            #         "type": "object",
            #         "properties": {
            #             "column": {
            #                 "type": "string",
            #                 "description": "The column to apply paragraph split. You have to select one column in the 'enum' field to apply paragraph-level split based on the description: "+description,
            #                 "enum": column_description
            #             }
            #         },
            #         "required": ["column"]
            #     }
            # },
            # {
            #     "name": "pdf_to_text",
            #     "description": 
            #     ''' 
            #     This function takes in one of the columns as input, transforms the pdf in that column into plain text, and generate an additional column to store the plain text. Don't select this if none of the columns match the user query.
            #     ''',
            #     "parameters": {
            #         "type": "object",
            #         "properties": {"column": {
            #             "type": "string",
            #             "description": "the column to apply pdf to text transformation, you have to select one column in the 'enum' field to apply pdf to text transformation based on the description: "+description,
            #             "enum": column_description,

            #         }
            #         }
            #     },
            #     "required": ["column"]
            # },
        ],
        "summarizer": [
            {
                "name": "get_summary",
                "description": 
                ''' 
                This function takes in one of the columns as input, summarizes the contents in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'story_gen'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to summarize, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_intent",
                "description": 
                ''' 
                This function takes in one of the columns that contain the text to be analyzed as input, retrieve the intent of the writer of text in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'get_reader_action'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column of text based on which writers' intents are ANALYZED from, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
        ],
        "augmentor": [
            {
                "name": "story_gen",
                "description": 
                ''' 
                This function takes in one of the columns of story summaries as input, generate a story based on the summaries in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_summary'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column that contains story summaries, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
        ],
        "calculator": {
        "continuous_calculator": [
            {
                "name": "get_event",
                "description": 
                ''' 
                This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain new events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'get_event_expected'; this function has to be executed at least once before calling 'get_event_major'; this function has to be executed at least once before calling 'get_story_type'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to calculate the probability of containing new events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_event_major",
                "description": 
                ''' 
                This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain major events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed at least once before calling 'get_story_type'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to calculate the probability of containing new major events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "event": {
                        "type": "string",
                        "description": "the column that contains the probability of containing new events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column", "event"]
            },
            {
                "name": "get_event_expected",
                "description": 
                ''' 
                This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain events that are as expected, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed at least once before calling 'get_story_type'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to calculate the probability of containing new events that are as expected, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "event": {
                        "type": "string",
                        "description": "the column that contains the probability of containing new events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column", "event"]
            },
            {
                "name": "get_persuasion_effect",
                "description": 
                ''' 
                This function takes in one of the columns as input, calculates the (numerical) persuasion effect score of the contents in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to calculate persuasion effect score, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_spread_likelihood",
                "description": 
                ''' 
                This function takes in one of the columns of readers' perceptions as input, calculates the (numerical) spread likelihood based on readers' perceptions in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. If there is no column denoting readers' perceptions, this function should not be selected. IMPORTANT: this function has to be executed after at least one call of 'get_reader_perception'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column that contains readers' perceptions to calculate the spread likelihood, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
        ],
        "discrete_calculator": [
            {
                "name": "get_emotional_reaction_level",
                "description": 
                ''' 
                This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of emotional reaction for the contents in the response post column, and generate an additional column to include the integer level. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {
                    "column_post": {
                        "type": "string",
                        "description": "the column that includes the original sad post, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "column": {
                        "type": "string",
                        "description": "the column that includes the reponse, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column", "column_post"]
            },
            {
                "name": "get_exploration_level",
                "description": 
                ''' 
                This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of exploration for the contents in the response post column, and generate an additional column to include the integer level. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {
                    "column_post": {
                        "type": "string",
                        "description": "the column that includes the original sad post, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "column": {
                        "type": "string",
                        "description": "the column that includes the reponse, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column", "column_post"]
            },
            {
                "name": "get_intepretation_level",
                "description": 
                ''' 
                This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of intepretation for the contents in the response post column, and generate an additional column to include the integer level. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {
                    "column_post": {
                        "type": "string",
                        "description": "the column that includes the original sad post, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "column": {
                        "type": "string",
                        "description": "the column that includes the reponse, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column", "column_post"]
            },
        ]
        },
        "classifier": {
        "binary_classifier": [
            {
                "name": "get_semantic",
                "description": 
                ''' 
                This function takes in a word, the type of the word, two sentences, and the indexes in the sentences as input, classifies whether the word in the two sentences has the same semantic, and generates an additional column that includes 'T' or 'F' accordingly. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {
                    "word": {
                        "type": "string",
                        "description": "the column that includes the word to classify semantic, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "word_type": {
                        "type": "string",
                        "description": "the column that includes the type of the word, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "sentence1": {
                        "type": "string",
                        "description": "the column that includes the first sentence to inspect semantics, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "sentence2": {
                        "type": "string",
                        "description": "the column that includes the second sentence to inspect semantics, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "index": {
                        "type": "string",
                        "description": "the column that includes indexes of the word in the two sentences, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["word", "word_type", "sentence1", "sentence2", "index"]
            },
            {
                "name": "get_change_opinion",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies whether the contents in that column changes opinion, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify whether the content would change their opinion, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_humor",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies whether the contents in that column is funny, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify whether the content is funny, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_politeness",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies whether the contents in that column is polite, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify whether the content is polite, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_toxic",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies whether the contents in that column will become toxic in the future, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify whether the content will become toxic in the future, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            # {
            #     "name": "get_sentiment",
            #     "description": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'pos', 'neg', or 'other'. Don't select this if none of the columns matches the user query.",
            #     "parameters": {
            #         "type": "object",
            #         "properties": {
            #             "column": {
            #                 "type": "string",
            #                 "description": "The column to apply sentiment analysis. You have to select one column in the 'enum' field to apply sentiment analysis based on the description: "+description,
            #                 "enum": column_description
            #             }
            #         },
            #         "required": ["column"]
            #     }
            # },
            {
                "name": "get_condition",
                "description": "This function takes in one of the columns as input, checks whether the contents of that column satisfy the conditions provided in the user query, and generates an additional column labeling the content as 'True' or 'False' or 'Undefined'. This function should only be called if all other functions cannot help to support user query. Don't select this if (1) there are other functions that can provide such a condition check or (2) there are no explicit conditions listed in the user query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to check conditions. You have to select one column in the 'enum' field to apply condition check based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_misinfo",
                "description": "This function takes in one of the columns as input, applies misinformation detection on the content of that column, and generates an additional column labeling the content as 'misinfo' (misinformation detected) or 'real' (no misinformation detected).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to apply misinformation detection. You have to select one column in the 'enum' field to apply misinformation detection based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
        ],
        "ternary_classifier": [
            {
                "name": "get_stance",
                "description": 
                ''' 
                This function takes in one column of text and one column of target topic as input, extracts the stance in the text column that towards the target topic, and generates a new column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to identify stance towards the target topic, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "target": {
                        "type": "string",
                        "description": "the column that includes the target topic, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },

                    }
                },
                "required": ["column", "target"]
            },
            {
                "name": "get_ideology_doc",
                "description": "This function takes in one of the columns that contains the links to documents as input, applies document-level ideology classification on that column, and generates an additional column labeling the content as 0 (meaning left), 1 (meaning neutral), or 2 (meaning right).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column that contains the links to documents to apply document-level ideology classification. You have to select one column in the 'enum' field based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_ideology_sent",
                "description": "This function takes in one of the columns that contains texts as input, applies sentence-level ideology classification on that column, and generates an additional column labeling the content as 'Conservative', 'Liberal', or 'Neutral'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column that contains the texts to apply sentence-level ideology classification. You have to select one column in the 'enum' field based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
        ],
        "multiple_classifier": [
            {
                "name": "get_story_type",
                "description": 
                ''' 
                This function takes in one column of sentence, one column of story index of where the sentence belong, one column of sentence index of that sentence, one column of the probability of the sentence containing new events, one column of probability of the sentence containing major new events, and one column of probabiliy of the sentence containing new events as expected as input, classifies the story type of the sentence into 'imagined', 'recalled', or 'retold', and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed after at least one call of 'get_event_major'; this function has to be executed after at least one call of 'get_event_expected'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify story type, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "storyIx": {
                        "type": "string",
                        "description": "the column that contains the story index of the sentence, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "sentIx": {
                        "type": "string",
                        "description": "the column that contains the sentence index of the sentence, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "event": {
                        "type": "string",
                        "description": "the column that contains the probability of the sentence containing new events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "event_major": {
                        "type": "string",
                        "description": "the column that contains the probability of the sentence containing new major events, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "event_expected": {
                        "type": "string",
                        "description": "the column that contains the probability of the sentence containing new events that are expected, you have to select one in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    }
                },
                "required": ["column", "storyIx", "sentIx", "event", "event_major", "event_expected"]
            },
            {
                "name": "get_dialect",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies the dialect features identified from the content of that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify the dialect features, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_disclosure",
                "description": 
                ''' 
                This function takes in one of the columns as input, classifies the content of that column into different disclosure acts, and generate an additional column to include those. Don't select this if none of the columns matches the user query.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to classify the disclosure acts, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
   
            # {
            #     "name": "get_emotion",
            #     "description": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'get_trigger'.",
            #     "parameters": {
            #         "type": "object",
            #         "properties": {
            #             "column": {
            #                 "type": "string",
            #                 "description": "The column to apply emotion detection. You have to select one column in the 'enum' field to apply emotion classification based on the description: "+description,
            #                 "enum": column_description
            #             }
            #         },
            #         "required": ["column"]
            #     }
            # },
            {
                "name": "get_emotion",
                "description": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'. Don't select this if none of the columns matches the user query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to apply emotion detection. You have to select one column in the 'enum' field to apply emotion classification based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_trope",
                "description": "This function takes in one of the columns that contains the quotes of a character as input, applies trope classification based on the content of the quotes, and generates an additional column to include those.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column that contains the quotes of a character. You have to select one column in the 'enum' field based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_hate",
                "description": "This function takes in one of the columns as input, applies (high-level) hate speech detection on the content of that column, and generates an additional column labeling the content as 'implicit_hate', 'explicit_hate', or 'not_hate'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to apply (high-level) hate speech detection. You have to select one column in the 'enum' field to apply (high-level) hate speech detection based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_hate_class",
                "description": "This function takes in one of the columns as input, applies (fine-grained) implicit hate speech classification on the content of that column, and generates an additional column labeling the content as 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to apply (fine-grained) implicit hate speech classification. You have to select one column in the 'enum' field to apply (fine-grained) implicit hate speech classification based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
                "name": "get_dog_whistle_persona_ingroup",
                "description": 
                ''' 
                This function takes in one of the columns of dog whistle terms, obtain the target persona/in-group of that dog whistle term, and generate an additional column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column of dog whistle terms to obtain the target persona/in-group, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_dog_whistle_type",
                "description": 
                ''' 
                This function takes in one of the columns of dog whistle terms, obtain the type of that dog whistle term, and generate an additional column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column of dog whistle terms to obtain the type, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
        ]
        },
        "extractor": {
            "text_extractor": [
            {
                "name": "get_event_argument",
                "description": 
                ''' 
                This function takes in one of the columns as input, get the event arguments recognized in that column, and generate additional rows and columns to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to apply event argument extraction, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,

                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_ner",
                "description": 
                ''' 
                This function takes in one of the columns as input, get the name entities recognized in that column, and generate additional rows and columns to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to apply NER analysis, you have to select one column in the 'enum' field to apply NER analysis based on the description: "+description,
                        "enum": column_description,

                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_keyword",
                "description": 
                ''' 
                This function takes in one of the columns as input, get the top 5 keywords recognized in that column, and generate an additional column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to apply keyword recognition, you have to select one column in the 'enum' field to apply keyword recognition based on the description: "+description,
                        "enum": column_description,

                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_trigger",
                "description": 
                ''' 
                This function takes in one column of text and one column of emotion class as input, extracts the trigger in the text column that triggers a specific emotion in the emotion class column, and generates a new column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_emotion'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to extract triggering sentence for a specific emotion, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "emotion": {
                        "type": "string",
                        "description": "the column that describes emotion class, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },

                    }
                },
                "required": ["column", "emotion"]
            },
            {
                "name": "get_dog_whistle",
                "description": 
                ''' 
                This function takes in one of the columns as input, extract the dog whistle term in that column, and generate an additional column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column to extract dog whistle term, you have to select one in the 'enum' field to summarize based on the description: "+description,
                        "enum": column_description,
                    }
                    }
                },
                "required": ["column"]
            },
            ],
            "information_extractor": [
            {
                "name": "get_hate_target",
                "description": "This function takes in one of the columns as input, applies implicit hate speech target identification on the content of that column, and generates an additional column of free text labeling the target identified from the content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "The column to apply implicit hate speech target identification. You have to select one column in the 'enum' field to apply implicit hate speech target identification based on the description: "+description,
                            "enum": column_description
                        }
                    },
                    "required": ["column"]
                }
            },
            {
            "name": "get_hate_implied",
            "description": "This function takes in one of the columns as input, applies implicit hate speech implied statement extraction on the content of that column, and generates an additional column of free text labeling the implied statement extracted from the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply implicit hate speech implied statement extraction. You have to select one column in the 'enum' field to apply implicit hate speech implied statement extraction based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
            },
            {
            "name": "get_positive_reframing",
            "description": "This function takes in one of the columns as input, extract the positive aspects of the content of that column and transforms it into a positive reframing version, and generates an additional column of positive reframing version of the content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply positive reframing. You have to select one column in the 'enum' field to apply positive reframing based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
            },
            {
                "name": "get_premise",
                "description": 
                ''' 
                This function takes in one column of figurative text, one column of figurative type, and one column of figurative term as input, extracts the literal text, i.e., the premise, of the figurative text column, and generates a new column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column of figurative texts to extract premises from, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "type": {
                        "type": "string",
                        "description": "the column that contains the figurative types of the figurative texts, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "term": {
                        "type": "string",
                        "description": "the column that contains the figurative terms of the figurative texts, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    }
                },
                "required": ["column", "type", "term"]
            },
            {
                "name": "get_premise_explanation",
                "description": 
                ''' 
                This function takes in one column of premise of figurative text, one column of the original figurative text, one column of figurative type, one column of figurative term as input, and one parameter labelling whether the premises entail or contract original figurative texts as input, extracts the explanations of literal texts, i.e., the premises, of the figurative text column, and generates a new column to include those.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column of premises of figurative texts to extract explanation from, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "hypothesis": {
                        "type": "string",
                        "description": "the column of original figurative texts, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "type": {
                        "type": "string",
                        "description": "the column that contains the figurative types of the figurative texts, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "term": {
                        "type": "string",
                        "description": "the column that contains the figurative terms of the figurative texts, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,
                    },
                    "label": {
                        "type": "string",
                        "description": "parameter defining whether the explanation is retrieved from premises that entail or contraduct figurative texts, you have to select one value in the 'enum' field.",
                        "enum": ["entail", "contradict"],
                    },
                    }
                },
                "required": ["column", "hypothesis", "type", "term", "label"]
            },
            ],
            "causal_extractor": [
            {
                "name": "get_reader_action",
                "description": 
                ''' 
                This function takes in one of the columns that contains writers' intent as input, get the reader action inferred from the writers' intent of that column, and generate an additional column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_intent'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column that contains writers' intent to infer readers' action from, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,

                    }
                    }
                },
                "required": ["column"]
            },
            {
                "name": "get_reader_perception",
                "description": 
                ''' 
                This function takes in one of the columns of text as input, infers readers' perceptions of text in that column, and generates an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'get_spread_likelihood'.
                ''',
                "parameters": {
                    "type": "object",
                    "properties": {"column": {
                        "type": "string",
                        "description": "the column that contains text to infer readers' perceptions from, you have to select one column in the 'enum' field based on the description: "+description,
                        "enum": column_description,

                    }
                    }
                },
                "required": ["column"]
            },
            ]
        }
    }
    functions = [  
    {
            "name": "para_sep",
            "description": "This function takes in one of the columns as input, split the text according to paragraphs, and generates an additional rows and columns to store the list of paragraphs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply paragraph split. You have to select one column in the 'enum' field to apply paragraph-level split based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },
        {
            "name": "pdf_to_text",
            "description": 
            ''' 
            This function takes in one of the columns as input, transforms the pdf in that column into plain text, and generate an additional column to store the plain text. Don't select this if none of the columns match the user query.
            ''',
            "parameters": {
                "type": "object",
                "properties": {"column": {
                    "type": "string",
                    "description": "the column to apply pdf to text transformation, you have to select one column in the 'enum' field to apply pdf to text transformation based on the description: "+description,
                    "enum": column_description,

                }
                }
            },
            "required": ["column"]
        },  
        {
            "name": "get_sentiment",
            "description": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'pos', 'neg', or 'other'. Don't select this if none of the columns matches the user query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The column to apply sentiment analysis. You have to select one column in the 'enum' field to apply sentiment analysis based on the description: "+description,
                        "enum": column_description
                    }
                },
                "required": ["column"]
            }
        },    
        {
            "name": "null",
            "description": "This function should be called when the table already contains all the necessary information to complete the user query. IMPORTANT: filter conditions related to numerical (such as range/percentile/etc.) doesn't require additional function calls, so this function should be called in cases when numerical value filters are the only operations to be applied.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "The placeholder parameter. It can only be 'null'",
                        "enum": ["null"]
                    }
                },
                "required": ["column"]
            }
        } 
    ]
    path = tree_path(user_query + "The function chain I have is " + function_chain+ ", current executed function chain is "+str(function_list), column_description, description, function_chain, function_list)
    print(path)
    path = path.replace("'", '"')
    path = json.loads(path)
    if len(path) > 0:
        path = path["path"]
        ls = tree
        for item in path:
            ls = ls[item]
    else:
        ls = []
    functions.extend(ls)
    
    messages = [
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the PDF file in 'pdf_orig', and is not given the plain text of the document, thus the first function to apply is 'pdf_to_text' on the 'pdf_orig' column to get the plain text of the PDF file.",
            "function_call": {
                "name": "pdf_to_text",
                "arguments": "{\n  \"column\": \"pdf_orig\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the plain text of the PDF file in 'pdf_orig_text', and is not given the paragraph-wise segments of the document, thus the first function to apply is 'para_sep' on the 'pdf_orig_text' column to get the paragraph-level splits of the plain text.",
            "function_call": {
                "name": "para_sep",
                "arguments": "{\n  \"column\": \"pdf_orig_text\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1;"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is given the paragraphs of the PDF file in 'pdf_orig_text_segments', and is not given the sentimental analysis for the paragraphs, thus the first function to apply is 'get_sentiment' on the 'pdf_orig_text_segments' column to get the sentiment for the paragraphs.",
            "function_call": {
                "name": "get_sentiment",
                "arguments": "{\n  \"column\": \"pdf_orig_text_segment\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1; 'pdf_orig_text_segment_sentiment' column is the sentiment of the content of the 'pdf_orig_text_segment' column; "
        },
        {
            "role": "assistant",
            "content": "To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Among all the columns, the user is already given the paragraph-level sentiment analysis in the 'pdf_orig_text_segment_sentiment' column. Thus the first function to apply is 'null' to end the function chain.",
            "function_call": {
                "name": "null",
                "arguments": "{\n  \"column\": \"null\"\n}"
            }
        },
        {
            "role": "user",
            "content": user_query + "The function chain I have is " + function_chain+ ", current executed function chain is "+str(function_list)  # Use the user's query
        }
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages,
        functions = functions,
        function_call = "auto",
    )

    return response.choices[0].message


def table_gen_pd(user_query, table, enum, description, status, function_chain):
    function_list = []
    while True:
        response = schema_gpt_tree(user_query + " I am given a table with the following columns: " + description, enum, description, function_chain, function_list)
        # print(response)
        if "function_call" not in response:
            if "content" in response:
                feedback = response["content"]
            else:
                feedback = ""
            return table, enum, description, True, feedback
        func = response["function_call"]
        f = func["name"]
        function_list.append(f)
        if f == "null":
            break
        function_dict = json.loads(func["arguments"])
        if f != "get_semantic":
            col = function_dict["column"]
            if col == "null":
                break
        # if f == "get_similarity":
        #     primary_id = function_dict["primary_id"]
        #     secondary_id = function_dict["secondary_id"]
        #     table, enum, description = globals()[f](table, col, enum, description, primary_id, secondary_id)
        if f == "get_trigger":
            emotion = function_dict["emotion"]
            table, enum, description = globals()[f](table, col, emotion, enum, description)
        elif f == "get_stance":
            target = function_dict["target"]
            table, enum, description = globals()[f](table, col, target, enum, description)
        elif f == "get_class":
            table, enum, description = globals()[f](user_query, table, col, enum, description)
        elif f == "get_premise_explanation":
            hypothesis = function_dict["hypothesis"]
            type = function_dict["type"]
            term = function_dict["term"]
            label = function_dict["label"]
            table, enum, description = globals()[f](table, col, hypothesis, type, term, label, enum, description)
        elif f == "get_premise":
            type = function_dict["type"]
            term = function_dict["term"]
            table, enum, description = globals()[f](table, col, type, term, enum, description)
        elif f == "get_semantic":
            word = function_dict["word"]
            word_type = function_dict["word_type"]
            index = function_dict["index"]
            sentence1 = function_dict["sentence1"]
            sentence2 = function_dict["sentence2"]
            table, enum, description = globals()[f](table, word, word_type, index, sentence1, sentence2, enum, description)
        elif f == "get_story_type":
            storyIx = function_dict["storyIx"]
            sentIx = function_dict["sentIx"]
            event = function_dict["event"]
            event_major = function_dict["event_major"]
            event_expected = function_dict["event_expected"]
            table, enum, description = globals()[f](table, col, storyIx, sentIx, event, event_major, event_expected, enum, description)
        elif f in ["get_emotional_reaction_level", "get_exploration_level", "get_intepretation_level"]:
            column_post = function_dict["column_post"]
            table, enum, description = globals()[f](table, col, column_post, enum, description)
        elif f in ["get_event_major", "get_event_expected"]:
            event = function_dict["event"]
            table, enum, description = globals()[f](table, col, event, enum, description)
        else:
            table, enum, description = globals()[f](table, col, enum, description)
    print(table)
    # print(description)
    status.append("table augmented")
    return table, enum, description, status, False, ""

# def table_gen_pd(user_query, table, enum, description, status):
#     while True:
#         response = schema_gpt(user_query + " I am given a table with the following columns: " + description, enum, description)
#         # print(response)
#         if "function_call" not in response:
#             if "content" in response:
#                 feedback = response["content"]
#             else:
#                 feedback = ""
#             return table, enum, description, True, feedback
#         func = response["function_call"]
#         f = func["name"]
#         if f == "null":
#             break
#         function_dict = json.loads(func["arguments"])
#         col = function_dict["column"]
#         if col == "null":
#             break
#         # if f == "get_similarity":
#         #     primary_id = function_dict["primary_id"]
#         #     secondary_id = function_dict["secondary_id"]
#         #     table, enum, description = globals()[f](table, col, enum, description, primary_id, secondary_id)
#         if f == "get_trigger":
#             emotion = function_dict["emotion"]
#             table, enum, description = globals()[f](table, col, emotion, enum, description)
#         elif f == "get_stance":
#             target = function_dict["target"]
#             table, enum, description = globals()[f](table, col, target, enum, description)
#         elif f == "get_class":
#             table, enum, description = globals()[f](user_query, table, col, enum, description)
#         else:
#             table, enum, description = globals()[f](table, col, enum, description)
#     print(table)
#     # print(description)
#     status.append("table augmented")
#     return table, enum, description, status, False, ""

if __name__ == "__main__":
    query = "I want to remove biases."
    table, enum, description = base_table_gen()
    status = []
    table, enum, description, _, __ = table_gen_pd(query, table, enum, description, status)
    # print(table)
    # print(enum)
    # # # print(description)
    # table, enum, description = pdf_to_text(table, 'pdf_orig', enum, description)
    # table, enum, description = get_keyword(table, 'pdf_orig_text', enum, description)
    # print(table)
    # # print(table)
    # print(enum)
    # # print(description)
    # table, enum, description = para_sep(table, 'pdf_orig_text', enum, description)
    # print(table)
    # print(enum)
    # # print(description)
    # # table, enum, description = get_summary(table, 'pdf_orig_text_segment1', enum, description)
    # # print(table)
    # # print(enum)
    # # print(description)



