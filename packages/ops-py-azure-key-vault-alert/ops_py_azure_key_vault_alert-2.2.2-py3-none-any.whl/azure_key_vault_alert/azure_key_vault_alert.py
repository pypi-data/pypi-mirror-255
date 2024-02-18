#!/usr/bin/env python

import os
import logging
import argparse
from azure_key_vault_report import azure_key_vault_report
from azure_key_vault_report import az_cmd
from message_handler import message_handler


def teams_alert(title, kv, max_chars):
    """post a payload to the url set in the WEBHOOK_REPORT variable

    Parameters
    ----------
    title : str
        The title of the message
    kv : azure_key_vault_report object
        An azure_key_vault_report object
    max_chars : int
        The max length of the report. To handle Slack message limit.
    22854
    Returns
    -------
    True
        If response from the POST has return code 200
    """

    if not WEBHOOK_REPORT:
        logging.warning("'WEBHOOK_REPORT' not provided. Report will not be posted to message handler.")
        return

    payload = kv.get_teams_payload(title)
    if len(payload) > max_chars:
        warning_msg = f"The {title} length is above the character limit count of {max_chars}"
        logging.warning(warning_msg)
        title = f"WARNING! {warning_msg}"
        text = "The html report have been omitted from the report due to size limits."
        payload = kv.get_teams_payload(title, text=text)

    logging.info(f"Using payload: {payload}")
    a = message_handler.MessageHandler(WEBHOOK_REPORT)
    a.set_payload(payload)
    a.post_payload()
    response_code = a.get_response_code()

    if isinstance(response_code, int) and response_code == 200:
        return True


def slack_alert(title, report, max_chars):
    """generates a json payload from 'title' and 'report' and then post the payload
     the url set in the WEBHOOK_REPORT variable

    Parameters
    ----------
    title : str
        The title of the message
    report : str
        The report part of the message
    max_chars : int
        The max length of the report. To handle Slack message limit.

    Returns
    -------
    True
        If response from the POST has return code 200
    """

    if not WEBHOOK_REPORT:
        logging.warning("'WEBHOOK_REPORT' not provided. Report will not be posted to message handler.")
        return

    if not isinstance(report, str):
        logging.warning("No report")
        return

    if len(report) > max_chars:
        warning_msg = f"The {title} length is above the character limit count of {max_chars}"
        logging.warning(warning_msg)
        summary = report.split("\n\n")[-1]
        title = f"WARNING! {warning_msg}"
        report = ("The report details have been omitted from the report. Only report summary is included:\n"
                  f"{summary}")

    logging.info("Building payload..")
    a = message_handler.MessageHandler(WEBHOOK_REPORT)
    a.build_payload(Title=title, Text=report)
    a.post_payload()
    response_code = a.get_response_code()

    if isinstance(response_code, int) and response_code == 200:
        return True


########################################################################################################################


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    # The list of key vaults to check passed as command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vaults", nargs='+',
                        help="List of key vaults to check. E.g. kv-dev kv-test")

    parser.add_argument("-e", "--expire_threshold", type=int,
                        help="If a value (int) is set. The days to the record's Expiration Date must be above "
                             "this threshold (Default: not set)")

    parser.add_argument("-a", "--include_all", action='store_true',
                        help="Include all records in output (verbose) if provided.")

    parser.add_argument("-i", "--include_no_expiration", action='store_false',
                        help="Also include records which has no Expiration Date set.")

    parser.add_argument("-t", "--teams_output", action='store_true',
                        help="Generate a MS Teams json object.")

    parser.add_argument("-H", "--report_if_no_html", action='store_true',
                        help="Will post the facts (summary report) to MS Teams even though no records "
                             "in the html report")

    parser.add_argument("-T", "--title", type=str, default="Azure Key Vault report",
                        help="The title of the message posted in Slack or MS Teams")

    parser.add_argument("-r", "--record_types", nargs='+',
                        help="List of record types to check for. E.g. certificate secret\n"
                             "Valid types are: certificate secret key\n"
                             "Default is all: certificate secret key",
                        default="certificate secret key")

    parser.add_argument("-L", "--slack_max_chars", type=int, default=13081,
                        help="The max characters the report can have due to the Slack Workflow message limits")

    parser.add_argument("-C", "--teams_max_chars", type=int, default=17367,
                        help="The max characters the report can have due to the MS Teams payload size limits")

    parser.add_argument("-S", "--stdout_only", action='store_true',
                        help="Only print report to stdout. No post to messagehandler (Slack or MS Teams")

    args = parser.parse_args()
    vaults = args.vaults
    expire_threshold = args.expire_threshold
    include_all = args.include_all
    ignore_no_expiration = args.include_no_expiration
    teams_output = args.teams_output
    report_if_no_html = args.report_if_no_html
    title = args.title
    record_types = args.record_types
    slack_max_chars = args.slack_max_chars
    teams_max_chars = args.teams_max_chars
    stdout_only = args.stdout_only

    logging.info(f"vaults: {vaults}")
    logging.info(f"expire_threshold: {expire_threshold}")
    logging.info(f"include_all: {include_all}")
    logging.info(f"ignore_no_expiration: {ignore_no_expiration}")
    logging.info(f"teams_output: {teams_output}")
    logging.info(f"report_if_no_html: {report_if_no_html}")
    logging.info(f"title: {title}")
    logging.info(f"record_types: {record_types}")
    logging.info(f"slack_max_chars: {slack_max_chars}")
    logging.info(f"teams_max_chars: {teams_max_chars}")
    logging.info(f"stdout_only: {stdout_only}")

    # Success initially set to False. Will be changed to True when a report has been posted.
    success = False

    if not vaults:
        logging.error("No vaults specified.")
        exit(2)

    # If only one key vault to check, it is ensured that it is treated as a list
    if isinstance(vaults, str):
        vaults = [vaults]

    if not WEBHOOK_REPORT:
        logging.warning("'WEBHOOK_REPORT' not provided. Report will not be posted to message handler.")

    # Runs all the az key vaults commands and add the results to the 'az_results' list
    az_results = []
    for vault in vaults:
        az_results += az_cmd.az_cmd(vault, record_types)

    # The report is generated by using the pip package ops-py-azure-key-vault-report
    # If argument 'include_no_expiration' is not provided,
    # the variable 'ignore_no_expiration' is then set to True
    kv_report = azure_key_vault_report.AzureKeyVaultReport(az_results)
    kv_report.parse_results()
    kv_report.add_summary()
    kv_report.add_report(expire_threshold=expire_threshold,
                         ignore_no_expiration=ignore_no_expiration,
                         include_all=include_all,
                         teams_json=teams_output)

    # If 'teams_output' is set to 'True' it will override the default messaging to Slack.
    # In case of Teams messaging a custom payload will be generated.
    # The payload will consist of:
    # - 'facts' which is a summary at the top
    # - 'html' which is a table with the report
    # The html report may be empty, in cases where there is nothing to report.
    #
    # It is optional, if an empty html report, to only post the 'facts'.
    # This is handled by the 'report_if_no_html' argument.
    if teams_output:
        if stdout_only:
            payload = kv_report.get_teams_payload(title)
            print(payload)
        else:
            success = teams_alert(title, kv_report, teams_max_chars)
    else:
        report = kv_report.get_markdown_report()
        if stdout_only:
            print(title)
            print(report)
        else:
            success = slack_alert(title, report, slack_max_chars)

    # If success and 'WEBHOOK_NOTIFY' is provided
    # an additional notify will be posted to the 'WEBHOOK_NOTIFY' webhook
    if success and WEBHOOK_NOTIFY:
        logging.info(f"Trigger additional alert about new report message(s)...")
        alert = message_handler.MessageHandler(WEBHOOK_NOTIFY)
        alert.post_payload()


########################################################################################################################


if __name__ == '__main__':
    # The actual report will be posted to the webhook exported in
    # the following environment variable
    WEBHOOK_REPORT = os.getenv("WEBHOOK_REPORT")

    # When all the reports have been posted, an additional POST is performed
    # to the webhook exported in following environment variable:
    WEBHOOK_NOTIFY = os.getenv("WEBHOOK_NOTIFY")

    main()
