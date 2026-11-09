
import pandas as pd
import re
import json
import csv
import os
from typing import List, Dict, Any
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import ast


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

    return prompt



# --------------------------------------------------------
# run_llm()                              
#--------------------------------------------------------
# ---> Function to easyly make a call
def run_llm(prompt: str, agent) -> str:
    try:
        messages = [{"role": "user", "content": prompt}]
        out = agent.generate(messages, temperature=0.0, seed=42, top_p=1.0)
        return out[0]
    except Exception as e:
        return json.dumps({"error": str(e), "raw_text": prompt[:400]})





#--------------------------------------------------------
# safe_eval()                              
#--------------------------------------------------------


def safe_eval(x):


    # NaN / None
    if pd.isna(x):
        return []

    # Already parsed
    if isinstance(x, list):
        return x

    # String input
    if isinstance(x, str):

        x = x.strip()

        if not x:
            return []

        # Try JSON first
        try:
            return json.loads(x)
        except Exception:
            pass

        # Fallback to Python literal syntax
        try:
            return ast.literal_eval(x)
        except Exception:
            print(f"Could not parse: {repr(x)}")
            return []

    # Any other type
    return []
 


# ---> Parser for the output of the model
def extract_json(text: str) -> Dict:
    parts = text.split("</think>", 1)
    if len(parts) > 1:
        clean_text = parts[1]
    else:
        clean_text = text

    # Step 2: find first JSON array
    match = re.search(r"\[[\s\S]*?\]", clean_text)
    if not match:
        return []

    json_str = match.group(0)

    json_str = safe_eval(json_str)   
    return json_str


