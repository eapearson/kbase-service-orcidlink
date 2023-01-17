SERVICE = orcidlink
SERVICE_CAPS = ORCIDLink
SPEC_FILE = ORCIDLink.spec
# URL = https://kbase.us/services/orcidlink
DIR = $(shell pwd)
LIB_DIR = lib
SCRIPTS_DIR = scripts
TEST_DIR = test
LBIN_DIR = bin
WORK_DIR = /kb/module/work/tmp
EXECUTABLE_SCRIPT_NAME = run_$(SERVICE_CAPS)_async_job.sh
STARTUP_SCRIPT_NAME = start_server.sh
TEST_SCRIPT_NAME = run_tests.sh

.PHONY: test

default: compile

all: compile build # build-startup-script build-executable-script build-test-script

compile:
	# kb-sdk compile $(SPEC_FILE) \
	#		--out $(LIB_DIR) \
	#		--pysrvname $(SERVICE_CAPS).$(SERVICE_CAPS)Server \
	#		--pyimplname $(SERVICE_CAPS).$(SERVICE_CAPS)Impl;

