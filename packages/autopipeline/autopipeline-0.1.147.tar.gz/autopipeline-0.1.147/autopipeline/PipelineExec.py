import pandas as pd
from pandasql import sqldf

def query_pd_exec(table, code, status, verbose):
    print(code)
    print("\n")
    namespace = {'res': 0, 'table': table}
    try:
        exec(code, namespace)
    except:
        feedback = "error occurred during execution" # maybe the error message?
        return namespace['res'], status, True, feedback
    status.append('code executed')
    return namespace['res'], status, False, ""

def query_sql_exec(table, code, status):
    # print(code)
    try:
        result = sqldf(code)
    except:
        return result, status, True
    status.append('code executed')
    return result, status, False

def display(result, status, verbose):
    print(result)
    status.append('displayed')
    return status