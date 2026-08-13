

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

#----------------------------------------------------------------------------------
# DATA INGEST
#----------------------------------------------------------------------------------
ingest_dd:
	bash launchers/run_basic_snellius.sh scripts/1.01_rnv_ingest_dd_structures.py

merge_dd_fb:
	bash launchers/run_basic_snellius.sh src/ingest/FB_json_to_csv.py

merge_dd_ig:
	bash launchers/run_basic_snellius.sh src/ingest/IG_json_to_csv.py

merge_dd_tt:
	bash launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py

merge_dd_x:
	bash launchers/run_basic_snellius.sh src/ingest/X_json_to_csv.py

merge_dd_yt:
	bash launchers/run_basic_snellius.sh src/ingest/YT_json_to_csv.py

merge_dd:
	sbatch launchers/run_basic_snellius.sh src/ingest/FB_json_to_csv.py
	sbatch launchers/run_basic_snellius.sh src/ingest/IG_json_to_csv.py
	sbatch launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py
	sbatch launchers/run_basic_snellius.sh src/ingest/X_json_to_csv.py
	sbatch launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py



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



id_std_chain:
	JOB_ID=$$(sbatch --parsable \
		--time=$(TIME_STD) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_STD),PYTHON_SCRIPT=$(PYTHON_SCRIPT_STD) \
		launchers/run_llm.sh); \
	echo "Waiting for job $$JOB_ID..."; \
	squeue --job $$JOB_ID --start; \
	while squeue -h -j $$JOB_ID | grep -q $$JOB_ID; do sleep 10; done; \
	echo "id_std finished"; \
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

TIME_CLASS=04:00:00

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

TIME_CLASS_TEST=04:00:00

data_class_test:
	sbatch \
		--time=$(TIME_CLASS_TEST) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
		launchers/run_llm.sh



# To execute the test when the inference is finished
data_class_chain:
	JOB_ID=$$(sbatch --parsable \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm.sh); \
	sbatch \
		--dependency=afterok:$$JOB_ID \
		--time=$(TIME_CLASS_TEST) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS_TEST),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS_TEST) \
		launchers/run_llm.sh