import pandas as pd

def prompt_context():
    return """
    You are given a JSON path to an observation in a social media data download. Please summarise in 100 words, what the data will be about.
    
    JSON path:
    {data_field_1}

    Answer format:
    [{{ "summary": "text of summary"}}]
   
"""


def prompt_classification():
    
    return """
        You are given a path consisting of a filepath and a JSON path and a list of IDs.
        From the list of IDs, choose the ID that explains best the JSON path. 
        ONLY choose IDs from the list of IDs, do NOT invent them yourself. 
        If you cannot find an appropriate ID in the list of IDs, return 'NA'
        
        path:
        {data_1}

        List of IDs:
        {data_2}

        Answer format:
        [{{ "estimated_id": "estimated id choosen from the list of IDs"}}]
    
    """

#--------------------------------------------------------
# prepare_prompt()                                 
#--------------------------------------------------------
def prepare_prompt(data_1, template,  data_2 = None, data_3 = None, data_4 = None):

    
    prompt = template.format(
        data_1 = data_1,
        data_2 = data_2,
        data_3 = data_3,
        data_4 = data_4
    )

    messages = [
        {"role": "system", "content": (
            "You are an expert on Spanish legal text.\n"
            "Reasoning: low"
        )},
        {"role": "user", "content": prompt}
    ]

    return messages
