#----------------------------------------------------------------------------------
# RUN SERVERS FOR DEVELOPMENT
#----------------------------------------------------------------------------------
MODEL ?= gpt-oss-20b

.PHONY: start_servers

start_servers:
	MODEL_YAML=$(PWD)/configs/$(MODEL).yaml bash launchers/run_servers.sh


# Uses the default model  (gpt-oss-20b)
#make start_servers

# Specify another model
#make start_servers MODEL=Qwen3-30B-A3B
#make start_servers MODEL=DeepSeek-R1
#make start_servers MODEL=Moonlight-16B-A3B-Instruct



#----------------------------------------------------------------
# ID STANDARDISATION
#----------------------------------------------------------------

#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_STD=gpt-oss-20b.yaml
PYTHON_SCRIPT_STD=scripts/3.01_rnv_run_id_standardisation.py

id std_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_STD) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
	bash launchers/run_llm_on_server.sh

TIME_STD=02:00:00

id_std:
	sbatch \
		--time=$(TIME_STD) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_STD),PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
		launchers/run_llm.sh

id_std_test:
	bash launchers/run_basic.sh scripts/3.02_rnv_test_id_standardisation.py



#----------------------------------------------------------------
# DATA CLASSIFICATION
#----------------------------------------------------------------

#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_CLASS=gpt-oss-20b.yaml
PYTHON_SCRIPT_CLASS=scripts/3.03_rnv_run_data_classification.py

data_class_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
	bash launchers/run_llm_on_server.sh

TIME_CLASS=02:00:00

data_class:
	sbatch \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm.sh



MODEL_CONFIG_CLASS_TEST=Qwen3-30B-A3B.yaml
PYTHON_SCRIPT_CLASS_TEST=scripts/3.04_rnv_test_data_classification.py

data_class_test_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
	bash launchers/run_llm_on_server.sh

TIME_CLASS=02:00:00

data_class_test:
	sbatch \
		--time=$(TIME_CLASS_TEST) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
		launchers/run_llm.sh