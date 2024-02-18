import openai
import pandas as pd
import os

OPENAI_ORGANIZATION = "org-5rFbX7p7v2H4Sk1C8xb17aea"
os.environ["OPENAI_ORG"] = OPENAI_ORGANIZATION
openai.organization=os.environ["OPENAI_ORG"]
#"get_emotion": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'."
#"get_emotion": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'anticipation', 'anger', 'fear', 'sadness', 'joy', 'trust', or 'disgust'. IMPORTANT: this function has to be executed at least once before calling 'get_trigger'."
def check_vague(user_query, columns, description):
    functions = '''
    "para_sep": "This function takes in one of the columns as input, split the text according to paragraphs, and generates an additional rows and columns to store the list of paragraphs.",
    "pdf_to_text": "This function takes in one of the columns as input, transforms the pdf in that column into plain text, and generate an additional column to store the plain text.",
    "get_summary": "This function takes in one of the columns as input, summarizes the contents in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'story_gen'."
    "get_ner": "This function takes in one of the columns as input, get the name entities recognized in that column, and generate additional rows and columns to include those.",
    "get_keyword": "This function takes in one of the columns as input, get the top 5 keywords recognized in that column, and generate an additional column to include those.",
    "get_sentiment": "This function takes in one of the columns as input, applies sentiment analysis on the content of that column, and generates an additional column labeling the content as 'Positive', 'Negative', and/or 'Neutral'."
    "get_condition": "This function takes in one of the columns as input, checks whether the contents of that column satisfy the user query, and generates an additional column labeling the content as 'True' or 'False' or 'Undefined'."
    "get_emotion": "This function takes in one of the columns as input, applies emotion classification on the content of that column, and generates an additional column labeling the content as 'sadness', 'joy', 'love', 'anger', 'fear', or 'surprise'."
    "get_misinfo": "This function takes in one of the columns as input, applies misinformation detection on the content of that column, and generates an additional column labeling the content as 'misinfo' (misinformation detected) or 'real' (no misinformation detected)."
    "get_hate": "This function takes in one of the columns as input, applies (high-level) hate speech detection on the content of that column, and generates an additional column labeling the content as 'implicit_hate', 'explicit_hate', or 'not_hate'."
    "get_hate_class": "This function takes in one of the columns as input, applies (fine-grained) implicit hate speech classification on the content of that column, and generates an additional column labeling the content as 'white_grievance', 'incitement', 'inferiority', 'irony', 'stereotypical', 'threatening', or 'other'."
    "get_hate_target": "This function takes in one of the columns as input, applies implicit hate speech target identification on the content of that column, and generates an additional column of free text labeling the target identified from the content."
    "get_hate_implied": "This function takes in one of the columns as input, applies implicit hate speech implied statement extraction on the content of that column, and generates an additional column of free text labeling the implied statement extracted from the content."
    "get_trigger": "This function takes in one column of text and one column of emotion class as input, extracts the trigger in the text column that triggers a specific emotion in the emotion class column, and generates a new column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_emotion'."
    "get_stance": "This function takes in one column of text and one column of target topic as input, extracts the stance of 'AGAINST', 'FAVOR', or 'NONE' in the text column that towards the target topic, and generates a new column to include those."
    "get_dog_whistle": "This function takes in one of the columns as input, extract the dog whistle term in that column, and generate an additional column to include those."
    "get_dog_whistle_persona_ingroup": "This function takes in one of the columns of dog whistle terms, obtain the target persona/in-group of that dog whistle term, and generate an additional column to include those."
    "get_dog_whistle_type": "This function takes in one of the columns of dog whistle terms, obtain the type of that dog whistle term, and generate an additional column to include those."
    "get_positive_reframing": "This function takes in one of the columns as input, extract the positive aspects of the content of that column and transforms it into a positive reframing version, and generates an additional column of positive reframing version of the content."
    "get_premise": "This function takes in one column of figurative text, one column of figurative type, and one column of figurative term as input, extracts the literal text, i.e., the premise, of the figurative text column, and generates a new column to include those."
    "get_premise_explanation": "This function takes in one column of premise of figurative text, one column of the original figurative text, one column of figurative type, one column of figurative term as input, and one parameter labelling whether the premises entail or contract original figurative texts as input, extracts the explanations of literal texts, i.e., the premises, of the figurative text column, and generates a new column to include those."
    "get_persuasion_effect": "This function takes in one of the columns as input, calculates the (numerical) persuasion effect score of the contents in that column, and generate an additional column to include those."
    "get_change_opinion": "This function takes in one of the columns as input, classifies whether the contents in that column changes opinion, and generate an additional column to include those."
    "get_reader_action": "This function takes in one of the columns of writers' intent as input, get the reader action inferred from the writers' intent of that column, and generate additional an column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_intent'."
    "get_reader_perception": "This function takes in one of the columns as input, infers readers' perceptions of text in that column, and generates an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'get_spread_likelihood'."
    "get_intent": "This function takes in one of the columns as input, retrieve the intent of the writer of text in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed at least once before calling 'get_reader_action'."
    "get_spread_likelihood": "This function takes in one of the columns of readers' perceptions as input, calculates the (numerical) spread likelihood based on readers' perceptions in that column, and generate an additional column to include those. IMPORTANT: this function has to be executed after at least one call of 'get_reader_perception'."
    "get_dialect": "This function takes in one of the columns as input, classifies the dialect features identified from the content of that column, and generate an additional column to include those."
    "get_disclosure": "This function takes in one of the columns as input, classifies the content of that column into different disclosure acts, and generate an additional column to include those."
    "get_semantic": "This function takes in a word, the type of the word, two sentences, and the indexes in the sentences as input, classifies whether the word in the two sentences has the same semantic, and generates an additional column that includes 'T' or 'F' accordingly."
    "get_emotional_reaction_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of emotional reaction for the contents in the response post column, and generate an additional column to include the integer level."
    "get_exploration_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of exploration for the contents in the response post column, and generate an additional column to include the integer level."
    "get_intepretation_level": "This function takes in one column of original sad post and one column of response post as input, calculates the (numerical) level of communication strength in terms of intepretation for the contents in the response post column, and generate an additional column to include the integer level."
    "get_humor": "This function takes in one of the columns as input, classifies whether the contents in that column is funny, and generate an additional column to include those."
    "get_polite": "This function takes in one of the columns as input, classifies whether the contents in that column is polite, and generate an additional column to include those."
    "get_toxic": "This function takes in one of the columns as input, classifies whether the contents in that column will become toxic in the future, and generate an additional column to include those."
    "story_gen": "This function takes in one of the columns of story summaries as input, generate a story based on the summaries in that column, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_summary'."
    "get_event": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain new events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed at least once before calling 'get_event_expected'; this function has to be executed at least once before calling 'get_event_major'; this function has to be executed at least once before calling 'get_story_type'."
    "get_event_major": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain major events, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed at least once before calling 'get_story_type'."
    "get_event_expected": "This function takes in one of the columns as input, calculates the (numerical) probability that the contents in that column contain events that are as expected, and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed at least once before calling 'get_story_type'."
    "get_story_type": "This function takes in one column of sentence, one column of story index of where the sentence belong, one column of sentence index of that sentence, one column of the probability of the sentence containing new events, one column of probability of the sentence containing major new events, and one column of probabiliy of the sentence containing new events as expected as input, classifies the story type of the sentence into 'imagined', 'recalled', or 'retold', and generate an additional column to include those. Don't select this if none of the columns matches the user query. IMPORTANT: this function has to be executed after at least one call of 'get_event'; this function has to be executed after at least one call of 'get_event_major'; this function has to be executed after at least one call of 'get_event_expected'."
    "get_event_argument": "This function takes in one of the columns as input, get the event arguments recognized in that column, and generate additional rows and columns to include those."
    "get_ideology_doc": "This function takes in one of the columns that contains the links to documents as input, applies document-level ideology classification on that column, and generates an additional column labeling the content as 0 (meaning left), 1 (meaning neutral), or 2 (meaning right)."
    "get_ideology_sent": "This function takes in one of the columns that contains texts as input, applies sentence-level ideology classification on that column, and generates an additional column labeling the content as 'Conservative', 'Liberal', or 'Neutral'."
    "get_trope": "This function takes in one of the columns that contains the quotes of a character as input, applies trope classification based on the content of the quotes, and generates an additional column to include those."
    '''
    messages = [
        {
            "role": "system",
            "content": "Given a table with columns: " + columns 
            + " where " + description 
            + " You are also given functions to be applied to different columns: " + functions 
            + '''Your task is 
                (1) Check if user query is specific enough; 
                (2) If it is specific (True), provide the function chain to be performed to generate the table required to answer users' query; NOTE: if the given table already has all necessary columns, the function chain should be an empty list;
                If it is not specific (False), provide alternative queries that are specific enough to be answered with a function chain of provided function.
            
                (3) If the generated function chain includes functions that generate columns of numerical values, but the user query doesn't include specific numbers, you should append a warning to the END of your generated message that says "WARNING: what you query for involves numerical values, are you sure you want to process without specifying a value or percentile? " 

                Your output format can ONLY be "True"/"False" + "#" + "{function chain}"/"{alternative queries}"
                '''
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "True#To count the number of positive paragraphs in the PDF document, the user should first transform the PDF file into plain text, break the text into paragraphs, and then get the sentiment of these paragraphs. Thus the function call chain should be ['pdf_to_text', 'para_sep', 'get_sentiment']",
        },
        {
            "role": "user",
            "content": "I want to find paragraph(s) dictating a specific outcome or reasoning. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "False#Your query is too vague. Alternatively, you can ask 'I want to get the summary for each paragraph in the pdf file.'",
        },
        {
            "role": "user",
            "content": "I want to find paragraph(s) with low persuasion effects score. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "True#To find paragraph(s) with low persuasion effects score, the user should first transform the PDF file into plain text, break the text into paragraphs, and then calculate the persuasion effects scores of these paragraphs. Thus the function call chain should be ['pdf_to_text', 'para_sep', 'get_persuasion_effect'] WARNING: what you query for involves numerical values, are you sure you want to process without specifying a value or percentile?",
        },
        {
            "role": "user",
            "content": "I want to find paragraph(s) with persuasion effects score < 0.5. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file;"
        },
        {
            "role": "assistant",
            "content": "True#To find paragraph(s) with low persuasion effects score, the user should first transform the PDF file into plain text, break the text into paragraphs, and then calculate the persuasion effects scores of these paragraphs. Thus the function call chain should be ['pdf_to_text', 'para_sep', 'get_persuasion_effect']",
        },
        {
            "role": "user",
            "content": "I want to count the number of positive paragraphs in the PDF document. 'id' column is the document ID; 'pdf_orig' column is the path to the pdf file of the document file; 'pdf_orig_text' column is the plain text content of the 'pdf_orig' column; 'pdf_orig_text_segment' stores the paragraph segments of the 'pdf_orig_text' column, the original text has empty value; 'pdf_orig_text_segmentid' column stores the paragraph index according to the order of the 'pdf_orig_text_segment' column, starts with 0, and the original text has value -1; 'pdf_orig_text_segment_sentiment' column is the sentiment of the content of the 'pdf_orig_text_segment' column; "
        },
        {
            "role": "assistant",
            "content": "True#Since the provided table already contains all necessary information to answer users' query, the function chain should be [].",
        },
        {
            "role": "user",
            "content": user_query + " " + description  # Use the user's query
        }
    ]

    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-16k",
        model="gpt-4-0613",
        messages=messages,
    )

    return response.choices[0].message, functions

if __name__ == "__main__":
    # query = "I want to remove biases."
    table = pd.read_csv("./data/base.csv")
    columns = str(table.columns.tolist())
    description = "'id' column is the document ID, starts with 0; 'pdf_orig' column is the path to the pdf file of the document file; "
    user_query = "I want to retrieve paragraphs that prevents geopolitical power shifts."
    # user_query = "Hi."
    #user_query = "I want to count the number of positive, negative, and neutral paragraphs for each document."
    response = check_vague(user_query, columns, description)
    print(response)
    