from .Mapping import table_gen_pd, base_table_gen
from .NL2SQL import query_pd, query_sql
from .PipelineExec import query_pd_exec, query_sql_exec, display

import openai
from pandasql import sqldf

import argparse
import os
import json
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")
# print(openai.api_key)

input_var = {"table_gen_pd": ["query", "table", "columns", "desc", "status", "function_chain"], "query_pd": ["query", "columns", "desc", "status"], "query_pd_exec": ["legal_cases", "code", "status"], "query_sql": ["query", "columns", "desc", "status"], "query_sql_exec": ["legal_cases", "code", "status"], "display": ["result", "status"]}
res_var = {"table_gen_pd": ["legal_cases", "columns", "desc", "status", "require_new", "feedback"], "query_pd": ["code", "status"], "query_pd_exec": ["result", "status", "require_new", "feedback"], "query_sql": ["code", "status", "require_new"], "query_sql_exec": ["result", "status", "require_new"], "display": ["status"]}

def pipeline_gen(query, table, desc, function_chain, table_type): 
    # if isinstance(table, pd.DataFrame):
    if table_type == "pd":
        return pipeline_gen_pd(query, table, function_chain, desc)
    else:
        return pipeline_gen_sql(query, table, function_chain, desc)

def pipeline_gen_pd(query, table, function_chain, desc):
    status = []
    columns = table.columns.tolist()
    value_dict = {"query": query, "legal_cases": table, "table": table, "desc": desc, "columns": columns, "status": status, "function_chain":function_chain}
    while 'displayed' not in status:
        columns = value_dict["columns"]
        desc = value_dict["desc"]
        status = value_dict["status"]
        response = pipeline_gpt_pd(query, columns, desc, status)
        # print(response)
        if "function_call" not in response:
            if "content" in response:
                feedback = response["content"]
            else:
                feedback = ""
            return True, feedback, None
        func = response["function_call"]
        f = func["name"]
        print("********** function called: ", f)
        # combined_dict = globals().copy()
        # combined_dict.update(locals())
        input_vars = [value_dict[v] for v in input_var[f]]
        # print("input_var: ", input_vars)
        # print("desc: ", desc)
        values = globals()[f](*input_vars)
        # print(values)
        if "require_new" in res_var[f] and values[-2]:
            return True, values[-1], None
        # values = globals()[f](query, table, columns, desc, status)
        for name, value in zip(res_var[f], values):
            value_dict[name] = value
        if len(status) >= 3 and status[-1] == status[-2] == status[-3]: # keep looping
            return True, values[-1], None
    return False, "", value_dict["result"]
            # print(value)
        # print(status)
        
def pipeline_gen_sql(query, table, desc):
    status = []
    columns = table.columns.tolist()
    require_new = False
    while 'displayed' not in status:
        response = pipeline_gpt_sql(query, columns, desc, status)
        if "function_call" not in response:
            return True
        func = response["function_call"]
        f = func["name"]
        print("***********function called: ", f)
        combined_dict = globals().copy()
        combined_dict.update(locals())
        input_vars = [combined_dict[v] for v in input_var[f]]
        values = globals()[f](*input_vars)
        # values = globals()[f](query, table, columns, desc, status)
        for name, value in zip(res_var[f], values):
            locals()[name] = value
        if require_new:
            return True
    return False

# using function call APIs
def pipeline_gpt_pd(user_query, column_description, description, status):
    # Define the user's query as an argument
    functions = [
        {
            "name": "table_gen_pd", 
            "description": "This function should be called when the given table does not include all the columns required to answer users' query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The base table.",
                    }
                },
                "required": ["table"]
            }
        },
        {
            "name": "query_pd",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), but the code for answering the queries are not yet provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The augmented table.",
                    }
                },
                "required": ["table"]
            }
        },
        {
            "name": "query_pd_exec",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), the code for answering the queries are also provided ('code generated'), however, the execution results are not available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The augmented table.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The execution code.",
                    },
                },
                "required": ["table", "code"]
            }
        },
        {
            "name": "display",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), the code for answering the queries are also provided ('code generated'), and the execution results are available ('code executed'), but the results have not been displayed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "The result to be displayed.",
                    }
                },
                "required": ["table"]
            }
        }
    ]
    messages = [
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: ['id', 'name', 'name_abbreviation', 'decision_date', 'case'], where 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury. The current completed tasks are []"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive summaries on the cases, the user should first get the summaries on the cases, and then get the sentiment of these summaries. However, the provided table does not provide information about these two properties. The table should be augmented using the 'table_gen_pd' function.",
            "function_call": {
                "name": "table_gen_pd",
                "arguments": "{\n  \"table\": \"table\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented']"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive summaries on the cases, the user should first get the summaries on the cases, and then get the sentiment of these summaries. The table already contains all the information, and 'table augmented' is also included in the completed tasks. However, the code has not been yet generated. Thus, the code should be generated using the 'query_pd' function.",
            "function_call": {
                "name": "query_pd",
                "arguments": "{\n  \"table\": \"table\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented', 'code generated']"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive summaries on the cases, the user should first get the summaries on the cases, and then get the sentiment of these summaries. The table already contains all the information, and 'table augmented' and 'code generated' are also included in the completed tasks. However, the code has not been yet executed. Thus, the code should be executed using the 'query_pd_exec' function.",
            "function_call": {
                "name": "query_pd_exec",
                "arguments": "{\n  \"table\": \"table\"\n, \"code\": \"code\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented', 'code generated', 'code executed']"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive summaries on the cases, the user should first get the summaries on the cases, and then get the sentiment of these summaries. The table already contains all the information, and 'table augmented', 'code generated', and 'code executed' are also included in the completed tasks. However, the result has not been yet displayed. Thus, the code should be executed using the 'display' function.",
            "function_call": {
                "name": "display",
                "arguments": "{\n  \"result\": \"result\"\n}"
            }
        },
        {
            "role": "user",
            "content": user_query  + " I am given a table with the following columns: " + str(column_description)+ " where " + description + "The current completed tasks are " + str(status)
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        # model="gpt-3.5-turbo-16k",
        messages=messages,
        functions = functions,
        function_call = "auto",
    )

    return response.choices[0].message


# using function call APIs
def pipeline_gpt_sql(user_query, column_description, description, status):
    # Define the user's query as an argument
    functions = [
        {
            "name": "table_gen_pd", 
            "description": "This function should be called when the given table does not include all the columns required to answer users' query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The base table.",
                    }
                },
                "required": ["table"]
            }
        },
        {
            "name": "query_sql",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), but the code for answering the queries are not yet provided.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The augmented table.",
                    }
                },
                "required": ["table"]
            }
        },
        {
            "name": "query_sql_exec",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), the code for answering the queries are also provided ('code generated'), however, the execution results are not available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "The augmented table.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The execution code.",
                    },
                },
                "required": ["table", "code"]
            }
        },
        {
            "name": "display",
            "description": "This function should be called when the given table already includes all the information required to answer users' query ('table augmented'), the code for answering the queries are also provided ('code generated'), and the execution results are available ('code executed'), but the results have not been displayed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "The result to be displayed.",
                    }
                },
                "required": ["table"]
            }
        }
    ]
    messages = [
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: ['id', 'name', 'name_abbreviation', 'decision_date', 'case'], where 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury. The current completed tasks are []"
        },
        {
            "role": "assistant",
            "content": "To count the number of positive summaries on the cases, the user should first get the summaries on the cases, and then get the sentiment of these summaries. However, the provided table does not provide information about these two properties. The table should be augmented using the 'table_gen_pd' function.",
            "function_call": {
                "name": "table_gen_pd",
                "arguments": "{\n  \"table\": \"table\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented']"
        },
        {
            "role": "assistant",
            "content": "'table augmented' is included in the completed tasks. However, the code has not been yet generated. Thus, the code should be generated using the 'query_pd' function.",
            "function_call": {
                "name": "query_sql",
                "arguments": "{\n  \"table\": \"table\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented', 'code generated']"
        },
        {
            "role": "assistant",
            "content": "'table augmented' and 'code generated' are included in the completed tasks. However, the code has not been yet executed. Thus, the code should be executed using the 'query_pd_exec' function.",
            "function_call": {
                "name": "query_sql_exec",
                "arguments": "{\n  \"table\": \"table\"\n, \"code\": \"code\"\n}"
            }
        },
        {
            "role": "user",
            "content": "I want to count the number of positive summaries on the cases. I am given a table with the following columns: 'id' is the case ID; 'name' is in the format of A v. B, where A and B are the accuser and the defendent on the court, and 'name_abbreviation' is the same as 'name', except that their names are in abbreviations (when querying a case with name, you should check both their whole name and their abbreviates); 'decision_date' is the date of the court, e.g., '1987-11-09'; 'case' is the sentence/description of the jury; 'case_summary' column provides summaries of the 'case' column; 'case_summary_sentiment' is the sentiment of the content of the 'case_summary' column being one of 'Positive', 'Negative', or 'Neutral'; The current completed tasks are ['table augmented', 'code generated', 'code executed']"
        },
        {
            "role": "assistant",
            "content": "'table augmented', 'code generated', and 'code executed' are included in the completed tasks. However, the result has not been yet displayed. Thus, the code should be executed using the 'display' function.",
            "function_call": {
                "name": "display",
                "arguments": "{\n  \"result\": \"result\"\n}"
            }
        },
        {
            "role": "user",
            "content": user_query  + " I am given a table with the following columns: " + str(column_description)+ " where " + description + "The current completed tasks are " + str(status)
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        # model="gpt-3.5-turbo-16k",
        messages=messages,
        functions = functions,
        function_call = "auto",
    )

    return response.choices[0].message

if __name__ == "__main__":
    table, enum, description = base_table_gen()
    query = "I want to get the summary for each paragraph in the pdf file."
    pipeline_gen(query, table, description, table_type="pd")


