"""
file: src/scripts/paths.py
description: Define and manage file paths used in the OpenShift drift detection process
author: Gizachew Kassa
Date: 01-04-2026
"""

import os

# Define the base directory for the project (assuming this script is in src/scripts/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths for Terraform configuration and output files
TERRAFORM_DIR = os.path.join(BASE_DIR, "terraform")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Define terraform output directory
TFOUPUT_PATH = os.path.join(OUTPUTS_DIR, "terraform")
TFPLAN_BIN_PATH = os.path.join(TFOUPUT_PATH, "tfplan.bin")

# Define path for the drift report
DRIFT_REPORT_PATH = os.path.join(OUTPUTS_DIR, "report")
DRIFT_REPORT_PATH_JSON = os.path.join(DRIFT_REPORT_PATH, "drift_report.json")
DRIFT_REPORT_PATH_CSV = os.path.join(DRIFT_REPORT_PATH, "drift_report.csv")
