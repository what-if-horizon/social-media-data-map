import pandas as pd

def prompt_context():
    return """
    You are given a JSON path to an observation in a social media data download. Please summarise in 100 words, what the data will be about.
    
    JSON path:
    {data_field_1}

    Answer format:
    [{{ "summary": "text of summary"}}]
   
"""


def prompt_std_ids_test():
    
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

def prompt_std_ids_retry_test():
    
    return """
        You are given a path consisting of a filepath and a JSON path and a list of IDs.
        You are also given the wrong answer by the previous LLM as it choose an ID that was not in the list of IDs.
        From the list of IDs, choose the ID that explains best the JSON path. 
        ONLY choose IDs from the list of IDs, do NOT invent them yourself. 
        If you cannot find an appropriate ID in the list of IDs, return 'NA'
        
        path:
        {data_1}

        List of IDs:
        {data_2}

        Wrong answer by previous LLM:
        {data_3}

        Answer format:
        [{{ "estimated_id": "estimated id choosen from the list of IDs"}}]
    
    """

def prompt_std_ids():
    
    return """
        You are given a path consisting of a filepath and a JSON path and a catalogue of paths.
        From the catalogue of paths, choose the path that explains best the given path. 
        The goal is to match paths that actually hold the same data but that are constructed or named differently. 
        ONLY choose paths from the catalogue of paths, do NOT invent them yourself. 
        If you cannot find an appropriate path in the catalogue of paths, return 'NA'
        
        path:
        {data_1}

        Catalogue of paths:
        {data_2}

        Answer format:
        [{{ "estimated_path": "estimated path choosen from the cataloque of paths"}}]
    
    """


def prompt_std_ids_retry():
    
    return """
        You are given a path consisting of a filepath and a JSON path and a catalogue of paths.
        You are also given the wrong answer by the previous LLM as it choose a path that was not in the catalogue of paths.
        From the list of IDs, choose the ID that explains best the JSON path. 
        ONLY choose paths from the catalogue of paths, do NOT invent them yourself. 
        If you cannot find an appropriate path in the catalogue of paths, return 'NA'
        
        path:
        {data_1}

        Catalogue of paths:
        {data_2}

        Wrong answer by previous LLM:
        {data_3}

        Answer format:
        [{{ "estimated_id": "estimated path choosen from the catalogue of paths"}}]
    
    """

def prompt_dt_schneider_2010():
    return """
    You are given five categories from a taxonomy of social networking data 
    Use these categories to classify the data entry (path consisting of a filepath and a JSON path) from a social media takeout
    Provide a rationale for choosing the categorie in 50 words
    
    Taxonomy of social networking data:
    1. Service data:  User-supplied data before it can access the service. These data are known as identifiable data, because they uniquely identify users on the system. 
    2. Disclosed data: Data that the user posts in his own page. These data are also known to form the user profile.
    3. Entrusted data: Data that the user posts the page to other network members. It is similar to Disclosed data, but the difference is that in some cases, after posting the content the user has no control over the data. 
    4. Incidental data: Data that other network members post about you. It is also similar to Disclosed data, but the difference is that it was not you who originally created the data and in some cases you have no control over them. 
    5. Behavioral data: Data that the site collects about the user's activities during its use. 
    6. Derived data: derived data from the data aforementioned. The derived data can be generated using various techniques, such as data mining.

    Path to data entry:
    {data_1}

    Answer format:
        [{{ "category": "Name of the chosen data category",
            "rationale": "Reason for choosing the category in 50 words}}]
    """

def prompt_dt_wu_2010():
    return """
    You are given five categories from a taxonomy of social networking data 
    Use these categories to classify the data entry (path consisting of a filepath and a JSON path) from a social media takeout
    Provide a rationale for choosing the categorie in 50 words
        
    Taxonomy of social networking data:
    1. Registration: This layer consists of the information required to identify the data provider uniquely among all the other users of the social network. 
    2. Networking: This layer consists of the information solicited by the social network to be released to its other users, in order to construct a network of contacts for the data provider.
    3. Content: This layer consists of the actual content with which the data provider actually participates in the social network.
    4. Activity: This data consists of web server logs, information from cookies, as well as other means of gathering information about the data provider’s activities on the social networking service.
   
    Path to data entry:
        {data_1}
    
    Answer format:
        [{{ "categorie": "Name of the chosen data category",
            "rationale": "Reason for choosing the categorie in 50 words}}]
     
    """

def prompt_judge_dt_schneider_2010():
    return"""
    Read the description of the taxonmy of social media networking data, the data entry (path consisting of a filepath and a JSON path) from a social media takeout, the classification and rationale done by another LLM and judge whether this LLM generated teh correct answer
    
    Taxonomy of social networking data:
        1. Service data:  User-supplied data before it can access the service. These data are known as identifiable data, because they uniquely identify users on the system. 
        2. Disclosed data: Data that the user posts in his own page. These data are also known to form the user profile.
        3. Entrusted data: Data that the user posts the page to other network members. It is similar to Disclosed data, but the difference is that in some cases, after posting the content the user has no control over the data. 
        4. Incidental data: Data that other network members post about you. It is also similar to Disclosed data, but the difference is that it was not you who originally created the data and in some cases you have no control over them. 
        5. Behavioral data: Data that the site collects about the user's activities during its use. 
        6. Derived data: derived data from the data aforementioned. The derived data can be generated using various techniques, such as data mining.
    
    Answer from previous LLM:
    {data_1}
    
    Answer format when incorrect:
    [{{ "judgement": "CORRECT"}}]

    Answer format when incorrect:
    [{{ "judgement": "INCORRECT",
    "rationale": "Reason why answer is judged as incorrect}}]

    """


def prompt_judge_dt_wu_2010():
    return"""
    Read the description of the taxonmy of social media networking data, the data entry (path consisting of a filepath and a JSON path) from a social media takeout, the classification and rationale done by another LLM and judge whether this LLM generated teh correct answer
    
    Taxonomy of social networking data:
        1. Registration: This layer consists of the information required to identify the data provider uniquely among all the other users of the social network. 
        2. Networking: This layer consists of the information solicited by the social network to be released to its other users, in order to construct a network of contacts for the data provider.
        3. Content: This layer consists of the actual content with which the data provider actually participates in the social network.
        4. Activity: This data consists of web server logs, information from cookies, as well as other means of gathering information about the data provider’s activities on the social networking service.
       
    Answer from previous LLM:
    {data_1}
    
    Answer format when incorrect:
    {{"judgement": "CORRECT"}}

    Answer format when incorrect:
    {{"judgement": "INCORRECT",
    "rationale": "Reason why answer is judged as incorrect}}

    """


# --------------------------------------------------------
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
