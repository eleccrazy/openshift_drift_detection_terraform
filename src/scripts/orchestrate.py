"""
file: src/scripts/orchestrate.py
description: Orchestrate the drift detection process by running the necessary Terraform commands and processing their outputs
author: Gizachew Kassa
Date: 01-04-2026
"""

import json
import os
import shlex
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file if present


def execute_command(command):
    """Execute a shell command and return its output."""
    cmd_args = shlex.split(command)
    try:
        result = subprocess.run(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def login_to_cluster():
    """Login to the OpenShift cluster using the credentials from environment variables."""
    print("Logging in to the OpenShift cluster...")

    # Get the variables
    osv_login = os.getenv("OSV_LOGIN")
    osv_username = os.getenv("OSV_USERNAME")
    osv_password = os.getenv("OSV_PASSWORD")

    # Check if the variables are set
    if not all([osv_login, osv_username, osv_password]):
        print(
            "Error: OSV_LOGIN, OSV_USERNAME, and OSV_PASSWORD environment variables must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create the oc login command using environment variables
    command = f"/usr/local/bin/oc login -u {osv_username} -p {osv_password} {osv_login}"
    execute_command(command)
    # If we reach here, it means the login was successful
    print("Successfully logged in to the OpenShift cluster.")

    # Get the cluster info and extract the cluster name and pint it from the output.
    cluster_info = execute_command("/usr/local/bin/oc cluster-info")
    for line in cluster_info.splitlines():
        if "Kubernetes control plane" in line:
            api_url = line.split(" ")[-1].strip()
            cluster_name = api_url.split(".")[1]
            print(f"API URL: {api_url}")
            print(f"Connected to Cluster: {cluster_name}")
            break


def run_terraform_commands():
    """ """
    # Assume terraform is initialized and we are in the correct directory /src with the configuration files.
    # Run the terraform plan command to detect drift and save the output to a file.
    print("Running terraform plan to detect drift...")
    pass


def main():
    """Main function to orchestrate the drift detection process."""
    print("\nStarting the OpenShift drift detection process...\n")
    print("\n")
    login_to_cluster()
    print("\n")
    run_terraform_commands()


if __name__ == "__main__":
    main()
