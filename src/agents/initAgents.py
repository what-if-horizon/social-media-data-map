#--------------------------------------------------------------------
# Libraries
#--------------------------------------------------------------------

import yaml                               # Read YAML configuration files
from openai import OpenAI                 # OpenAI-compatible API client
from transformers import AutoTokenizer    # HuggingFace tokenizer loader
import os


#--------------------------------------------------------------------
# VLLMAgent()
#--------------------------------------------------------------------

class VLLMAgent:

    #--------------------------------------------------------
    # Constructor
    #--------------------------------------------------------

    def __init__(self, base_url, model_name, tokenizer, default_params):

        # OpenAI-compatible client pointing to local vLLM server
        self.client = OpenAI(
            base_url=base_url,
            api_key="x"                   # vLLM ignores API key by default
        )

        # Name exposed by the vLLM server
        self.model = model_name

        # HuggingFace tokenizer associated with the model
        self.tokenizer = tokenizer

        # Default generation parameters
        self.default_params = default_params


    #--------------------------------------------------------
    # generate()
    #--------------------------------------------------------

    def generate(self, messages, **overrides):

        # Merge default parameters with runtime overrides
        # Runtime arguments take priority
        params = {
            **self.default_params,
            **overrides
        }

        # OpenAI chat completion request
        response = self.client.chat.completions.create(

            # Model served by vLLM
            model=self.model,

            # OpenAI-format messages
            messages=messages,

            # Sampling / generation parameters
            **params
        )

        # Return generated text
        # Wrapped in list for compatibility with multi-generation pipelines
        return [response.choices[0].message.content]


#--------------------------------------------------------------------
# init_models_api()
#--------------------------------------------------------------------

def init_models_api(
    model_dir,
    model_name,
    base_url,
    temperature,
    presence_penalty,
    max_tokens,
    top_p
):

    #--------------------------------------------------------
    # Load tokenizer
    #--------------------------------------------------------
    model_path = f'{model_dir}/{model_name}'
    tokenizer = AutoTokenizer.from_pretrained(

        # Full model path
        model_path,

        # Allow custom tokenizer code
        trust_remote_code=True
    )

    #--------------------------------------------------------
    # Default generation parameters
    #--------------------------------------------------------

    default_params = dict(

        # Sampling temperature
        temperature=temperature,

        # Presence penalty
        presence_penalty=presence_penalty,

        # Maximum generated tokens
        max_tokens=max_tokens,

        # Top-p nucleus sampling
        top_p=top_p,
    )

    #--------------------------------------------------------
    # Create agent
    #--------------------------------------------------------

    return VLLMAgent(

        # vLLM OpenAI endpoint
        base_url=base_url,

        # Served model name
        model_name=model_name,

        # Associated tokenizer
        tokenizer=tokenizer,

        # Default inference parameters
        default_params=default_params
    )


#--------------------------------------------------------------------
# AgentManager (YAML VERSION)
#--------------------------------------------------------------------

class AgentManager:

    #--------------------------------------------------------
    # Constructor
    #--------------------------------------------------------

    def __init__(
        self,
        model_config_path = None,
        model_dir=None
    ):
        
        if model_config_path is None:
            model_config_path = os.environ["MODEL_YAML"]

        if model_dir is None:
            model_dir = os.environ["MODEL_DIR"]

        # Root directory containing all models
        self.model_dir = model_dir

        # Dictionary storing all initialized agents
        self.agents = {}

        # Initialize agents from YAML configs
        self._init_agents(
            model_config_path,

        )


    #--------------------------------------------------------
    # _init_agents()
    #--------------------------------------------------------

    def _init_agents(
        self,
        model_config_path,
    ):

        #--------------------------------------------------------
        # Load model configuration
        #--------------------------------------------------------

        with open(model_config_path, "r") as f:
            model_config = yaml.safe_load(f)

        
        #--------------------------------------------------------
        # Initialize one agent per model
        #--------------------------------------------------------

        for entry in model_config["models"]:

            # Model name from YAML
            model_name = entry["name"]

            model_num = entry["model_num"]

            temperature = entry['temperature']

            presence_penalty = entry['presence_penalty']

            max_tokens = entry['max_tokens']

            top_p = entry['top_p']

            # Load port from yaml and create url
            port = entry["port"]
        
            base_url = f"http://localhost:{port}/v1"


            #--------------------------------------------------------
            # Create and store agent
            #--------------------------------------------------------

            self.agents[model_num] = init_models_api(

                # Root model directory
                self.model_dir,

                # Model name
                model_name=model_name,

                base_url=base_url,

                temperature=temperature,

                presence_penalty=presence_penalty,

                max_tokens=max_tokens,

                top_p=top_p
            )


    #--------------------------------------------------------
    # get()
    #--------------------------------------------------------

    def get(self, model_num):

        # Return initialized agent by name
        return self.agents[model_num]