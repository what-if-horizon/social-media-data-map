def prompt_context():
    return """
    You are given a JSON path to an observation in a social media data download. Please summarise in 100 words, what the data will be about.
    
    JSON path:
    {data_field_1}

    Answer format:
    [{{ 'summary': 'text of summary'}}]
   
"""