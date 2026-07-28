from src.inference import prompts as p
from src.agents.initAgents import AgentManager
import re
import json


def returnAgent():
    manager = AgentManager()
    return manager

manager = returnAgent()


def generate_output(data_1, template,  max_retries = 3, data_2 = None, data_3 = None, data_4 = None):
    
    #Load the agent
    agent = next(iter(manager.agents.keys()))
    model = manager.get(agent)


    for attempt in range(max_retries):
        try:
    
            # Do the inference
            
            prompt = p.prepare_prompt(data_1, data_2, data_3, data_4, template)
            
            answer = model.generate(prompt)   
            
            raw_text = answer[0]
            
    
            # Extract JSON
            
            parts = raw_text.split("</think>", 1)
            if len(parts) > 1:
                clean_text = parts[1]
            else:
                clean_text = raw_text

            # Step 2: find first JSON array
            match = re.search(r"\{[\s\S]*?\}", clean_text)
            if not match:
                return []

            json_str = match.group(0)
       
            #json_str = u.safe_eval(json_str)   
            return json_str
        

        except Exception as e:

            print(f"Attempt {attempt + 1} failed: {e}")

    return []
