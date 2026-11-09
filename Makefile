# ---- load .env (MODEL_DIR, ROOT_DIR, DATA_DIR, ...; see .env.example) ----
# Optional here; targets that need it check the variables themselves.
-include .env
export

.DEFAULT_GOAL := help

.PHONY: help
help:  ## List the targets
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-24s %s\n", $$1, $$2}'
	@echo "  taxonomy-<platform>      Classify one platform (facebook|instagram|tiktok|youtube|x)"


#----------------------------------------------------------------------------------
# RUN SERVERS FOR DEVELOPMENT
#----------------------------------------------------------------------------------
MODEL ?= gpt-oss-20b_2agent

.PHONY: start_servers

#To ask for an interative node srun --partition=gpu_h100 --gpus=2 --time=01:00:00 --pty bash

start_servers: ## Start vLLM servers for development (MODEL=...)
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
ingest_dd: ## Ingest data donation structures
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

flatten_dd: ## Flatten all platform JSON exports to CSV
	bash launchers/run_basic_snellius.sh src/ingest/FB_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/IG_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/TT_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/X_json_to_csv.py
	bash launchers/run_basic_snellius.sh src/ingest/YT_json_to_csv.py


get_unique_paths: ## Get unique paths
	bash launchers/run_basic_snellius.sh scripts/0.01_rnv_get_unique_paths.py

find_largest_donation: ## Find the largest donation
	bash launchers/run_basic_snellius.sh scripts/0.02_rnv_find_largest_donation.py

merge_csv: ## Merge structures
	bash launchers/run_basic_snellius.sh scripts/0.03_rnv_merge_structures.py

sample: ## Sample for inference
	bash launchers/run_basic_snellius.sh scripts/0.04_rnv_sample_for_inference.py

annotation_sample: ## Sample for annotation
	bash launchers/run_basic_snellius.sh scripts/0.05_rnv_sample_annotation.py


#----------------------------------------------------------------------------------
# TAXONOMY CLASSIFICATION
#----------------------------------------------------------------------------------
#make taxonomy-youtube                                   # one platform with its configured resources
#make taxonomy                                           # submit all five as separate jobs
#make taxonomy-run SUB=tiktok NODES=2 TIME=00:45:00      # one-off override

# ---- shared settings ----
MODULE_PATH  := scripts/2.01_rnv_run_data_classification.py
MODEL_CONFIG := gpt-oss-20b_tp1x4tp.yaml
# DATA_TAX must be a key in PROMPTS in the classification script; both go into the output file name
# (no inline comments after these: make would keep the trailing spaces in the value)
DATA_TAX     := kmetty2026
COUNTRIES    := ES_NL
LAUNCHER     := launchers/parallel_llm.sh
SOURCE_ROOT  := $(ROOT_DIR)/$(DATA_DIR)/00_ingest/005_merged_structures
OUTPUT_ROOT  := $(ROOT_DIR)/$(DATA_DIR)/02_path_classification/021_classified_paths

# ---- Snellius settings ----
# SURF budget account (check with: accinfo)
ACCOUNT       := vusei17670
# gpu_a100 or gpu_h100
PARTITION     := gpu_a100
# matches tp1x4 (4 GPUs per node)
GPUS_PER_NODE := 4
# gpu_a100/h100 have 18 cores per GPU; 16 leaves headroom
CPUS_PER_GPU  := 16

# ---- per-platform resources: edit these ----
PLATFORMS := facebook instagram tiktok youtube x

NODES_facebook  := 2
TIME_facebook   := 00:30:00
NODES_instagram := 2
TIME_instagram  := 00:30:00
NODES_tiktok    := 1
TIME_tiktok     := 00:15:00
NODES_youtube   := 1
TIME_youtube    := 00:15:00
NODES_x         := 1
TIME_x          := 00:15:00

.PHONY: taxonomy-run
taxonomy-run:
	@test -n "$(MODEL_DIR)" && test -n "$(ROOT_DIR)" && test -n "$(DATA_DIR)" || (echo "ERROR: MODEL_DIR, ROOT_DIR and DATA_DIR must be set in .env (see .env.example)" && exit 1)
	@test -n "$(SUB)"   || (echo "ERROR: SUB is required" && exit 1)
	@test -n "$(NODES)" || (echo "ERROR: NODES is required" && exit 1)
	@test -n "$(TIME)"  || (echo "ERROR: TIME is required" && exit 1)
	@echo ">>> [$(SUB)] nodes=$(NODES) time=$(TIME) partition=$(PARTITION)"
	@echo ">>> Input:  $(SOURCE_ROOT)/$(SUB)"
	@echo ">>> Output: $(OUTPUT_ROOT)/$(SUB)"
	@mkdir -p "$(OUTPUT_ROOT)/$(SUB)" logs
	sbatch -A $(ACCOUNT) -p $(PARTITION) --time=$(TIME) \
		--job-name=taxonomy_$(SUB) \
		--nodes=$(NODES) --ntasks-per-node=1 \
		--gpus-per-node=$(GPUS_PER_NODE) \
		--cpus-per-task=$$(( $(GPUS_PER_NODE) * $(CPUS_PER_GPU) )) \
		--output="logs/taxonomy_$(SUB)_%j.out" \
		--error="logs/taxonomy_$(SUB)_%j.err" \
		--export=ALL,MODEL_DIR=$(MODEL_DIR),MODEL_CONFIG=$(MODEL_CONFIG),SOURCE_FOLDER=$(SOURCE_ROOT)/$(SUB),OUTPUT_FOLDER=$(OUTPUT_ROOT)/$(SUB),MODULE_PATH=$(MODULE_PATH),DATA_TAX=$(DATA_TAX),COUNTRIES=$(COUNTRIES),GPUS_PER_NODE=$(GPUS_PER_NODE) \
		$(LAUNCHER)

define TAXONOMY_RULE
.PHONY: taxonomy-$(1)
taxonomy-$(1):
	@$$(MAKE) --no-print-directory taxonomy-run SUB=$(1) NODES=$$(NODES_$(1)) TIME=$$(TIME_$(1))
endef
$(foreach p,$(PLATFORMS),$(eval $(call TAXONOMY_RULE,$(p))))

.PHONY: taxonomy
taxonomy: $(addprefix taxonomy-,$(PLATFORMS)) ## Submit taxonomy classification for all platforms


.PHONY: test
test: ## Run unit tests
	python -m unittest discover -s tests -v


#----------------------------------------------------------------------------------
# VALIDATION AND VISUALISATION (CPU only)
#----------------------------------------------------------------------------------
id_std_val: ## Validate the id standardisation test run
	bash launchers/run_basic_snellius.sh scripts/1.01.01_rnv_validate_test_id_standardisation.py

id_std_viz: ## Visualise id standardisation validation
	bash launchers/run_basic_snellius.sh scripts/1.01.02_rnv_visualisation_validation_id_standardisation.py

data_class_split: ## Split classification data
	bash launchers/run_basic_snellius.sh scripts/2.03_rnv_split_data_data_classification.py

data_class_test_val: ## Validate the classification test run
	bash launchers/run_basic_snellius.sh scripts/2.04_rnv_test_validate_data_classification.py

data_class_viz: ## Visualise classification results
	bash launchers/run_basic_snellius.sh scripts/2.05_rnv_visualisation_results_data_classification.py
