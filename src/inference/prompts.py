import pandas as pd

def prompt_context():
    return """
    You are given a JSON path to an observation in a social media data download. Please summarise in 100 words, what the data will be about.
    
    JSON path:
    {data_field_1}

    Answer format:
    [{{ 'summary': 'text of summary'}}]
   
"""


def prompt_classification():
    
    return """
        You are given a path consisting of a filepath and a JSON path and a list of IDs. Please choose the correct ID for the path
        
        path:
        {data_1}

        List of IDs:
        {data_2}

        Answer format:
        [{{ 'estimated_id': 'text of summary'}}]
    
    """

