#!/usr/bin/env python

import logging
import json
import subprocess


########################################################################################################################


def az_cmd(vault_name, record_types, path=""):
    """creates and invokes the 'az keyvault' shell subprocess commands

    Parameters
    ----------
    vault_name : str
        The name of the Key Vault
    record_types : list
        'certificate', 'key' or 'secret'
        The shell subprocess command will be generated based on the record_type, e.g.:
            'az keyvault secret list --vault-name NAME-OF-THE-KEY-VAULT'
            'az keyvault key list --vault-name NAME-OF-THE-KEY-VAULT'
            'az keyvault certificate list --vault-name NAME-OF-THE-KEY-VAULT'
    path : str
        Option to set path to where az is found. If az is not located in default PATH.

    Returns
    -------
    list
        A list of dicts. Each dict contains
          - the vault_name
          - the record_type
          - and the output from the az keyvault cmd

        If no results or other error, None is returned
    """

    # Default valid record types for the az keyvault cmd
    valid_record_types = ["certificate", "key", "secret"]
    results = []

    if not isinstance(path, str):
        logging.error(f"Not a valid path: '{str(path)}'")
        return

    if isinstance(record_types, str):
        record_types = record_types.split()

    if not isinstance(record_types, list):
        logging.error(f"'record_types' must be provided as list or string. Not {type(record_types)} - '{str(record_types)}'")
        return

    for k in record_types:
        if k not in valid_record_types:
            logging.error(f"Not a valid record_type: '{str(k)}'. Must be either 'certificate', 'key' or 'secret'.")
            continue

        cmd = f"az keyvault {k} list --vault-name {vault_name}"

        # If path provided, add it to cmd and ensure no double //
        if path:
            cmd = f"{path.rstrip('/')}/{cmd}"

        az = subprocess.run(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        az_stdout = az.stdout.decode("utf-8")
        if az_stdout:
            res = json.loads(az_stdout)
            results.append({"vault_name": vault_name,
                            "record_type": k,
                            "out": res})
            continue

        # Try to read stderr from cmd, but only if not stdout.
        logging.error(f"{cmd} returned with an error.")
        if az.stderr:
            try:
                az_stderr = az.stderr.decode("utf-8").rstrip()
            except:
                az_stderr = az.stderr.rstrip()
        else:
            continue
        logging.error(f"Error output: '{az_stderr}'")

    return results
