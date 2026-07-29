


#----------------------------------------------------------------
# RUN CLASSIFICATION
#----------------------------------------------------------------

#ONLY FOR DEV PURPOSES!! USE WITH run_servers.sh in interactive node
MODEL_CONFIG_CLASS=gpt-oss-20b.yaml
PYTHON_SCRIPT_CLASS=scripts/2.01_rnv_run_classification.py

classification:
	MODEL_CONFIG=$(MODEL_CONFIG_CLASS) \
	PYTHON_SCRIPT=$(PYTHON_SCRIPT_CLASS) \
	bash launchers/run_llm_on_server.sh
