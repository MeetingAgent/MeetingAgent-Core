MESSAGE_BUDDY_MAIN_PROMPT = """
<!-->IMPORTANT CONTEXT<--!>
An answer should be coherent and include some point form arguments.
<!-->IMPORTANT CONTEXT<--!>

Given a question, answer it in the best way possible.
"""

EXTRACT_QUERY_PROMPT = """
Given some input text, extract a query from the text. 
If no query exists, interpret the text as is and see if a question can be captured from it.
"""