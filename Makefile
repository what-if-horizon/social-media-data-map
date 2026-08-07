
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

id std_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
	bash launchers/run_llm_on_server.sh

TIME_CLASS=02:00:00

id_std:
	sbatch \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm.sh