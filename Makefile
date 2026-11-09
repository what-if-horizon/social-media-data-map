# ---- load .env (MODEL_DIR, ROOT_DIR, DATA_DIR, ...; see .env.example) ----
# Optional here; targets that need it check the variables themselves.
-include .env
export

.DEFAULT_GOAL := help

.PHONY: help
help:  ## List the targets
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-24s %s\n", $$1, $$2}'
	@echo "  <job>-<platform>         Per platform: taxonomy-, path_std-, taxonomy-eval- (facebook|instagram|tiktok|youtube|x)"
	@echo "  CPU jobs: override CPU_TIME, CPU_CPUS, CPU_PARTITION, or LOCAL=1 to run in this shell"


#----------------------------------------------------------------------------------
# SNELLIUS SETTINGS AND CPU JOBS
#----------------------------------------------------------------------------------
# SURF budget account (check with: accinfo)
ACCOUNT       := vusei17670

# CPU jobs (no GPU): launchers/cpu_job.sh, submitted with sbatch.
#   make get_unique_paths                              # submit with the defaults below
#   make merge_csv CPU_TIME=02:00:00 CPU_CPUS=32       # per-run override
#   make sample LOCAL=1                                # no sbatch: run in this shell (interactive node)
# Leave CPU_PARTITION empty for the default CPU partition.
CPU_TIME      ?= 01:00:00
CPU_CPUS      ?= 16
CPU_PARTITION ?=
LOCAL         ?=
CPU = @mkdir -p logs && $(if $(LOCAL),bash launchers/cpu_job.sh $(1),sbatch -A $(ACCOUNT) $(if $(CPU_PARTITION),-p $(CPU_PARTITION)) --time=$(CPU_TIME) --cpus-per-task=$(CPU_CPUS) --job-name=$(basename $(notdir $(1))) --output=logs/%x_%j.out --error=logs/%x_%j.err launchers/cpu_job.sh $(1))


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
	$(call CPU,scripts/0_ingest/0.00_rnv_ingest_dd_structures.py)

flatten_dd_fb:
	$(call CPU,src/ingest/FB_json_to_csv.py)

flatten_dd_ig:
	$(call CPU,src/ingest/IG_json_to_csv.py)

flatten_dd_tt:
	$(call CPU,src/ingest/TT_json_to_csv.py)

flatten_dd_x:
	$(call CPU,src/ingest/X_json_to_csv.py)

flatten_dd_yt:
	$(call CPU,src/ingest/YT_json_to_csv.py)

flatten_dd: ## Flatten all platform JSON exports to CSV
	$(call CPU,src/ingest/FB_json_to_csv.py)
	$(call CPU,src/ingest/IG_json_to_csv.py)
	$(call CPU,src/ingest/TT_json_to_csv.py)
	$(call CPU,src/ingest/X_json_to_csv.py)
	$(call CPU,src/ingest/YT_json_to_csv.py)


get_unique_paths: ## Get unique paths
	$(call CPU,scripts/0_ingest/0.01_rnv_get_unique_paths.py)

find_largest_donation: ## Find the largest donation
	$(call CPU,scripts/0_ingest/0.02_rnv_find_largest_donation.py)

merge_csv: ## Merge structures
	$(call CPU,scripts/0_ingest/0.03_rnv_merge_structures.py)

sample: ## Sample for inference
	$(call CPU,scripts/0_ingest/0.04_rnv_sample_for_inference.py)

annotation_sample: ## Sample for annotation
	$(call CPU,scripts/0_ingest/0.05_rnv_sample_annotation.py)


#----------------------------------------------------------------------------------
# LLM JOBS (parallel_llm.sh: vLLM servers on N nodes, one job per platform)
#----------------------------------------------------------------------------------
#make taxonomy-youtube                                   # one platform with its configured resources
#make taxonomy                                           # submit all five as separate jobs
#make path_std-youtube / make path_std                   # path standardisation (1.02)
#make taxonomy-eval-youtube SPLIT=test                   # classify the annotation sample (test|validation)
# Any job can be overridden on the command line, e.g. make taxonomy-youtube NODES=2 TIME=01:00:00

# ---- shared settings ----
MODEL_CONFIG := gpt-oss-20b_tp1x4tp.yaml
MODEL_NAME   := $(basename $(MODEL_CONFIG))
# DATA_TAX must be a key in PROMPTS in scripts/2_classification/2.01_rnv_run_data_classification.py; both go into output file names
# (no inline comments after these: make would keep the trailing spaces in the value)
DATA_TAX     := kmetty2026
COUNTRIES    := ES_NL
LAUNCHER     := launchers/parallel_llm.sh
SOURCE_ROOT  := $(ROOT_DIR)/$(DATA_DIR)/00_ingest/005_merged_structures
REF_DIR      := $(ROOT_DIR)/$(DATA_DIR)/00_ingest/004_largest_donation
ANNOTATION_ROOT := $(ROOT_DIR)/ddd_annotation
SPLIT        ?= validation

# ---- GPU settings ----
# gpu_a100 or gpu_h100
PARTITION     := gpu_a100
# matches tp1x4 (4 GPUs per node)
GPUS_PER_NODE := 4
# gpu_a100/h100 have 18 cores per GPU; 16 leaves headroom
CPUS_PER_GPU  := 16

# ---- per-job, per-platform resources: edit these ----
# Variables are <job>_NODES_<platform> and <job>_TIME_<platform>.
PLATFORMS := facebook instagram tiktok youtube x

# Taxonomy classification (production)
taxonomy_NODES_facebook  := 2
taxonomy_TIME_facebook   := 00:30:00
taxonomy_NODES_instagram := 2
taxonomy_TIME_instagram  := 00:30:00
taxonomy_NODES_tiktok    := 1
taxonomy_TIME_tiktok     := 00:15:00
taxonomy_NODES_youtube   := 1
taxonomy_TIME_youtube    := 00:15:00
taxonomy_NODES_x         := 1
taxonomy_TIME_x          := 00:15:00

# Path standardisation: every prompt carries the whole reference catalogue, so it is slower per row.
# TODO: guesses (same nodes, double the time); adjust after the first run.
path_std_NODES_facebook  := 2
path_std_TIME_facebook   := 01:00:00
path_std_NODES_instagram := 2
path_std_TIME_instagram  := 01:00:00
path_std_NODES_tiktok    := 1
path_std_TIME_tiktok     := 00:30:00
path_std_NODES_youtube   := 1
path_std_TIME_youtube    := 00:30:00
path_std_NODES_x         := 1
path_std_TIME_x          := 00:30:00

# Taxonomy classification of the annotation sample (small)
taxonomy_eval_NODES_facebook  := 1
taxonomy_eval_TIME_facebook   := 00:15:00
taxonomy_eval_NODES_instagram := 1
taxonomy_eval_TIME_instagram  := 00:15:00
taxonomy_eval_NODES_tiktok    := 1
taxonomy_eval_TIME_tiktok     := 00:15:00
taxonomy_eval_NODES_youtube   := 1
taxonomy_eval_TIME_youtube    := 00:15:00
taxonomy_eval_NODES_x         := 1
taxonomy_eval_TIME_x          := 00:15:00

# ---- jobs: arguments for llm-run; @P@ is replaced by the platform ----
# Output name placeholders: {platform} {n} {stem} (see src/inference/parallel.py)
taxonomy_ARGS = MODULE_PATH=scripts/2_classification/2.01_rnv_run_data_classification.py \
	SOURCE_FOLDER=$(SOURCE_ROOT)/@P@ \
	OUTPUT_FOLDER=$(ROOT_DIR)/$(DATA_DIR)/02_path_classification/021_classified_paths/@P@ \
	OUTPUT_PATTERN='{platform}_{n}_class_ids_$(DATA_TAX)_$(COUNTRIES)_$(MODEL_NAME).json' \
	EXTRA_EXPORT=',DATA_TAX=$(DATA_TAX)'

path_std_ARGS = MODULE_PATH=scripts/1_path_standardisation/1.02_rnv_run_path_standardisation.py \
	SOURCE_FOLDER=$(SOURCE_ROOT)/@P@ \
	OUTPUT_FOLDER=$(ROOT_DIR)/$(DATA_DIR)/01_path_standardisation/011_classified_paths/@P@ \
	OUTPUT_PATTERN='{platform}_{n}_std_ids_$(COUNTRIES)_$(MODEL_NAME).json' \
	EXTRA_EXPORT=',REF_DIR=$(REF_DIR)'

taxonomy_eval_ARGS = MODULE_PATH=scripts/2_classification/2.01_rnv_run_data_classification.py \
	SOURCE_FOLDER=$(ANNOTATION_ROOT)/sample/$(SPLIT)/@P@ \
	OUTPUT_FOLDER=$(ANNOTATION_ROOT)/inference/02_path_classification/$(SPLIT)/@P@ \
	OUTPUT_PATTERN='{platform}_{n}_class_ids_$(DATA_TAX)_$(COUNTRIES)_$(MODEL_NAME).json' \
	EXTRA_EXPORT=',DATA_TAX=$(DATA_TAX)'

# ---- generic submit: needs JOB SUB NODES TIME MODULE_PATH SOURCE_FOLDER OUTPUT_FOLDER OUTPUT_PATTERN ----
.PHONY: llm-run
llm-run:
	@test -n "$(MODEL_DIR)" && test -n "$(ROOT_DIR)" && test -n "$(DATA_DIR)" || (echo "ERROR: MODEL_DIR, ROOT_DIR and DATA_DIR must be set in .env (see .env.example)" && exit 1)
	@test -n "$(SUB)"   || (echo "ERROR: SUB is required" && exit 1)
	@test -n "$(NODES)" || (echo "ERROR: NODES is required" && exit 1)
	@test -n "$(TIME)"  || (echo "ERROR: TIME is required" && exit 1)
	@echo ">>> [$(JOB) $(SUB)] nodes=$(NODES) time=$(TIME) partition=$(PARTITION)"
	@echo ">>> Input:  $(SOURCE_FOLDER)"
	@echo ">>> Output: $(OUTPUT_FOLDER)/$(OUTPUT_PATTERN)"
	@mkdir -p "$(OUTPUT_FOLDER)" logs
	sbatch -A $(ACCOUNT) -p $(PARTITION) --time=$(TIME) \
		--job-name=$(JOB)_$(SUB) \
		--nodes=$(NODES) --ntasks-per-node=1 \
		--gpus-per-node=$(GPUS_PER_NODE) \
		--cpus-per-task=$$(( $(GPUS_PER_NODE) * $(CPUS_PER_GPU) )) \
		--output="logs/$(JOB)_$(SUB)_%j.out" \
		--error="logs/$(JOB)_$(SUB)_%j.err" \
		--export="ALL,MODEL_DIR=$(MODEL_DIR),MODEL_CONFIG=$(MODEL_CONFIG),SOURCE_FOLDER=$(SOURCE_FOLDER),OUTPUT_FOLDER=$(OUTPUT_FOLDER),MODULE_PATH=$(MODULE_PATH),OUTPUT_PATTERN=$(OUTPUT_PATTERN),GPUS_PER_NODE=$(GPUS_PER_NODE)$(EXTRA_EXPORT)" \
		$(LAUNCHER)

# $(1) = target prefix (e.g. taxonomy-eval), $(2) = variable prefix (e.g. taxonomy_eval), $(3) = platform
define LLM_RULE
.PHONY: $(1)-$(3)
$(1)-$(3):
	@$$(MAKE) --no-print-directory llm-run JOB=$(1) SUB=$(3) NODES=$$(or $$(NODES),$$($(2)_NODES_$(3))) TIME=$$(or $$(TIME),$$($(2)_TIME_$(3))) $$(subst @P@,$(3),$$($(2)_ARGS))
endef
$(foreach p,$(PLATFORMS),$(eval $(call LLM_RULE,taxonomy,taxonomy,$(p))))
$(foreach p,$(PLATFORMS),$(eval $(call LLM_RULE,path_std,path_std,$(p))))
$(foreach p,$(PLATFORMS),$(eval $(call LLM_RULE,taxonomy-eval,taxonomy_eval,$(p))))

.PHONY: taxonomy path_std taxonomy-eval
taxonomy: $(addprefix taxonomy-,$(PLATFORMS)) ## Submit taxonomy classification for all platforms
path_std: $(addprefix path_std-,$(PLATFORMS)) ## Submit path standardisation (1.02) for all platforms
taxonomy-eval: $(addprefix taxonomy-eval-,$(PLATFORMS)) ## Classify the annotation sample (SPLIT=test|validation)


#----------------------------------------------------------------------------------
# JOB CONTROL
#----------------------------------------------------------------------------------
.PHONY: jobs cancel
jobs: ## Show your queued and running jobs
	squeue -u $(USER) -o "%.10i %.22j %.9P %.8T %.10M %.10l %.6D %R"

# make cancel                      cancels ALL your jobs
# make cancel NAME=taxonomy_tiktok cancels only jobs with that name
cancel: ## Cancel all your jobs (NAME=<job name> for one job only)
	scancel -u $(USER) $(if $(NAME),--name=$(NAME))
	@echo "Cancelled $(if $(NAME),jobs named $(NAME),all jobs of $(USER))"


.PHONY: test
test: ## Run unit tests
	python -m unittest discover -s tests -v


#----------------------------------------------------------------------------------
# VALIDATION AND VISUALISATION (CPU only)
#----------------------------------------------------------------------------------
id_std_val: ## Validate the id standardisation test run
	$(call CPU,scripts/1_path_standardisation/1.01.01_rnv_validate_test_id_standardisation.py)

id_std_viz: ## Visualise id standardisation validation
	$(call CPU,scripts/1_path_standardisation/1.01.02_rnv_visualisation_validation_id_standardisation.py)

data_class_split: ## Split classification data
	$(call CPU,scripts/2_classification/2.03_rnv_split_data_data_classification.py)

data_class_test_val: ## Validate the classification test run
	$(call CPU,scripts/2_classification/2.04_rnv_test_validate_data_classification.py)

data_class_viz: ## Visualise classification results
	$(call CPU,scripts/2_classification/2.05_rnv_visualisation_results_data_classification.py)
