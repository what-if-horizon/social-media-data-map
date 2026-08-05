


#----------------------------------------------------------------
# RUN CLASSIFICATION
#----------------------------------------------------------------

#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_CLASS=gpt-oss-20b.yaml
PYTHON_SCRIPT_CLASS=scripts/3.01_rnv_run_classification.py

classification_dev:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
	bash launchers/run_llm_on_server.sh

TIME_CLASS=02:00:00

classification:
	sbatch \
		--time=$(TIME_CLASS) \
		--export=ALL,MODEL_CONFIG=$(MODEL_CONFIG_CLASS),PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
		launchers/run_llm.sh

classification_test:
	bash launchers/run_basic.sh scripts/3.02_rnv_test_classification.py 