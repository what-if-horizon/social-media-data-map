

#----------------------------------------------------------------------------------
# RUN SERVERS FOR DEVELOPMENT
#----------------------------------------------------------------------------------
MODEL ?= gpt-oss-20b

.PHONY: start_servers

#To ask for an interative node srun --partition=gpu_h100 --gpus=2 --time=01:00:00 --pty bash

start_servers:
	MODEL_YAML=$(PWD)/configs/$(MODEL).yaml bash launchers/run_servers_snellius.sh


# Uses the default model  (gpt-oss-20b)
#make start_servers

# Specify another model
#make start_servers MODEL=Qwen3-30B-A3B
#make start_servers MODEL=DeepSeek-R1
#make start_servers MODEL=Moonlight-16B-A3B-Instruct

#----------------------------------------------------------------------------------
# DATA INGEST
#----------------------------------------------------------------------------------
ingest_dd:
	bash launchers/run_basic_snellius.sh scripts/0.00_rnv_ingest_dd_structures.py

flatten_dd_fb:
	bash launchers/run_basic_snellius.sh src/ingest/FB_json_to_csv.py

flatten_dd_ig:
	bash launchers/run_basic_snellius.sh src/ingest/IG_json_to_csv.py

flatten_dd_tt:
	bash launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py

flatten_dd_x:
	bash launchers/run_basic_snellius.sh src/ingest/X_json_to_csv.py

flatten_dd_yt:
	bash launchers/run_basic_snellius.sh src/ingest/YT_json_to_csv.py

flatten_dd:
	bash launchers/run_basic_snellius.sh src/ingest/FB_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/IG_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/X_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py



get_unique_paths: 
	bash launchers/run_basic_snellius.sh scripts/0.01_rnv_get_unique_paths.py

find_largest_donation:
	bash launchers/run_basic_snellius.sh scripts/0.02_rnv_find_largest_donation.py

merge_csv:
	bash launchers/run_basic_snellius.sh scripts/0.03_rnv_merge_structures.py






#----------------------------------------------------------------
# ID STANDARDISATION
#----------------------------------------------------------------


#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_STD=gpt-oss-20b.yaml
PYTHON_SCRIPT_STD=scripts/1.01_rnv_test_id_standardisation.py

id_std_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_STD) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
	bash launchers/run_llm_on_server_snellius.sh

TIME_STD=02:00:00

id_std:
	sbatch \
		--time=$(TIME_STD) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_STD),PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
		launchers/run_llm_snellius.sh


MODEL_CONFIG_STD=gpt-oss-20b_4gpu.yaml
PYTHON_SCRIPT_STD=scripts/1.02_rnv_run_path_standardisation.py

path_std_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_STD) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
	bash launchers/run_llm_on_server_snellius.sh
	
TIME_STD=02:00:00

path_std:
	sbatch \
		--time=$(TIME_STD) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_STD),PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
		launchers/run_llm_snellius.sh


#----------------------------------------------------------------
# DATA CLASSIFICATION
#----------------------------------------------------------------

#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_CLASS=gpt-oss-20b.yaml
PYTHON_SCRIPT_CLASS=scripts/2.01_rnv_run_data_classification.py

data_class_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
	bash launchers/run_llm_on_server_snellius.sh

TIME_CLASS=04:00:00

data_class:
	sbatch \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm_snellius.sh



MODEL_CONFIG_CLASS_TEST=Qwen3-30B-A3B.yaml
PYTHON_SCRIPT_CLASS_TEST=scripts/2.02_rnv_test_data_classification.py

data_class_test_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
	bash launchers/run_llm_on_server_snellius.sh

TIME_CLASS_TEST=04:00:00

data_class_test:
	sbatch \
		--time=$(TIME_CLASS_TEST) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
		launchers/run_llm_snellius.sh



# To execute the test when the inference is finished
data_class_chain:
	JOB_ID=$$(sbatch --parsable \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm_snellius.sh); \
	sbatch \
		--dependency=afterok:$$JOB_ID \
		--time=$(TIME_CLASS_TEST) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
		launchers/run_llm_snellius.sh