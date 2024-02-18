#!/usr/bin/env python

import logging

try:
    from .html_table import HTMLTable
except:
    from html_table import HTMLTable
try:
    from .ms_teams_json import MSTeamsPayload
except:
    from ms_teams_json import MSTeamsPayload
try:
    from .set_timestamp import set_timestamp, now
except:
    from set_timestamp import set_timestamp, now
try:
    from .markdown import Summary
except:
    from markdown import Summary
try:
    from .config import *
except:
    from config import *


########################################################################################################################


class AzureKeyVaultReport(object):
    """generates a report from the results of 'az keyvault' commands

    The values of 'updated', 'created' and 'expires' are converted to date object
    and the age (in days) is calculated.

    Then a table is generated and sorted by (from top to bottom):
    the oldest 'Expiration' date, then by
    the oldest 'Last Updated' date


    Attributes
    ----------

    results : list
        The list of results from the 'az keyvault' commands, enriched with 'vault_name' and 'record_type'
    table_columns : list
        The list of table columns: a tuple of width and name for each column.
        Used in html and plain text report
    items : list
        The list of items.
        Items are enriched with more data, e.g. age of each date element, vault_name, record_type, record_name
    header : str
        The report header
    body : str
        The report body. Generated based on arguments passed to generate_report method and outcome of the az cli cmd
    footer : str
        The report footer, containing a summary.
    facts : list
        The list of facts used in MS Teams output
    html_table :
        The html table used in MS Teams output
    vaults : list
         The unique list of vaults processed


    Methods
    -------

    parse_results()
        Parse through the provided 'results' from the azure cli keyvault cmd outputs.
        For each result in the results new item is created and added to the items list.
        Each item contains the following data:
        - Date objects, created from the 'updated', 'created' and 'expires' values and stored as values
          in new X_ts keys.
        - The age (in days) is calculated from each of the date objects and stored as values in new X_age keys.
        - 'vault_name' and 'record_type
    generate_report()
        Creates a plain text report and initiates ms team report generation if specified.
        The 'Comment' column created is generated according to the age of 'updated', 'created' and 'expires'.
        If missing 'expires' then a comment concerning that is also added.
    sort_item():
        Returns a sorted list of all the records
    add_html_row()
        Add row of record to html table
    get_json_facts()
        Returns the facts (if any) to be used in the MS Teams JSON payload
    get_report()
        Returns the plain text report. Full report or summary only (the footer)
    """

    def __init__(self, results):
        """
        Parameters
        ----------
        results : list
            The list of results from the 'az keyvault' commands, enriched with 'vault_name' and 'record_type'
        """

        self.results = results
        self.items = []
        self.body = []
        self.this_year = 0      # Updated this year
        self.one_year = 0       # One year and older, but less than two years
        self.two_years = 0      # Two year and older, but less than three years
        self.three_years = 0    # Three years and older
        self.facts = []         # Facts to be used in an MS Teams payload
        self.html_table = None  # HTML table object. Used for MS Teams
        self.vaults = []        # The unique list of vaults processed
        self.summary_values = config.get("summary")

    def get_report(self):
        """return the plain text report"""

        # If a body has been generated, then the header is also included in the output.
        if self.body:
            return [self.header] + self.body
            #return self.header + self.body + self.footer

        # Only the summary footer is output when a body has not been generated.
        return "self.summary"

    def sort_items(self, expired_days=7, will_expire_days=14):
        """Sort the list of dict items by days to expiration

        If no parameters provided, this method will return a sorted list of all the records.
        The list will be sorted from top and down, by the oldest 'Expiration' date and then followed
        by the oldest 'Last Updated' date and then returns the sorted list.

        If any of the parameters provided, it will first create and sort an 'expired' list and then the same with
        a 'will_expire' list, and the finally a list with the other records.
        Each list will be sorted from top and down, by the oldest 'Expiration' date and then followed
        by the oldest 'Last Updated' date and then returns a combined list.

        Parameters
        ----------
        expired_days : int
            If provided, the record will be added to a separate list (expired),
            if the expires_age (days since expiration) of the record
            is between 0 the days provided in the expired_days argument.

        will_expire_days : int
            If provided, the record will be added to a separate list (will_expire),
            if the expires_age (days to expiration) of the record
            is between 0 the days provided in the will_expire_days argument,
            and the record is not already added to the expired list.
        """

        if not isinstance(expired_days, int):
            return sorted(self.items, key=lambda x: (str(x.get('expires')), x.get('updated', ' ')), reverse=False)

        expired = []
        will_expire = []
        others = []
        for item in self.items:
            expires_age = item.get("expires_age")
            if isinstance(expires_age, int) and expires_age <= 0 and abs(expires_age) <= expired_days:
                expired.append(item)
                continue

            if isinstance(expires_age, int) and 0 <= expires_age <= will_expire_days:
                will_expire.append(item)
                continue

            others.append(item)

        sorted_list = sorted(expired, key=lambda x: (str(x.get('expires')), x.get('updated', ' ')), reverse=False)
        sorted_list += sorted(will_expire, key=lambda x: (str(x.get('expires')), x.get('updated', ' ')), reverse=False)
        sorted_list += sorted(others, key=lambda x: (str(x.get('expires')), x.get('updated', ' ')), reverse=False)

        return sorted_list

    def parse_results(self):
        """parse through the result from the azure cli keyvault cmd output"""
        if not isinstance(self.results, list):
            return

        for r in self.results:
            for o in r.get("out"):
                item = {}
                if isinstance(o, dict):
                    vault_name = r.get("vault_name")
                    if vault_name not in self.vaults:
                        self.vaults.append(vault_name)

                    item["vault_name"] = vault_name
                    item["record_type"] = r.get("record_type")
                    item["record_name"] = o.get("name")

                    a = o.get("attributes")
                    if isinstance(a, dict):
                        for k, v in a.items():

                            if "enabled" in k:
                                item["enabled"] = v

                            if "updated" in k or "created" in k or "expires" in k and v:
                                value = v.split("T")[0]
                                item[k] = value
                                ts = set_timestamp(value)
                                item[f"{k}_ts"] = ts
                                age = (now() - ts).days
                                item[f"{k}_age"] = age

                                # Update the update age counters:
                                # One year and older, but less than two years
                                if "updated" in k and age < 365:
                                    self.summary_values["this_year"]["value"] += 1

                                # One year and older, but less than two years
                                if "updated" in k and (365 <= age < 365 * 2):
                                    self.summary_values["one_year"]["value"] += 1

                                # Two year and older, but less than three years
                                elif "updated" in k and (365 * 2 <= age < 365 * 3):
                                    self.summary_values["two_years"]["value"] += 1

                                # Three years and older
                                elif "updated" in k and age >= 365 * 3:
                                    self.summary_values["three_years"]["value"] += 1

                self.items.append(item)

    def report_summary(self):
        rows = []
        for k, v in self.summary_values.items():
            print(k, v)

    def generate_report(self, expire_threshold=None, ignore_no_expiration=True, include_all=False, teams_json=False):
        """creates a plain text report and initiates ms team report generation if specified.
        returns the plain text report.

        Parameters
        ----------
        expire_threshold : int
            Ignore to report the record if days till the secret will expire are more than this 'expire_threshold' value
            NOTE: Secrets expiring today or already expired will always be reported.
        ignore_no_expiration : bool
            Report all records if set to False. If set to True only secrets with Expiration Date set will be reported.
        include_all : bool
            If set to True all records are included in the output.
        teams_json : bool
            If set to True then a report in json format containing a html table will also be generated.
        """
        if not isinstance(self.results, list):
            return

        if teams_json:
            self.html_table = HTMLTable([x[1] for x in self.table_columns])
            self.html_table.init_html_table()

        # Ensure empty body
        self.body = []

        # Sort the items from top and down
        # First sort by the oldest 'Expiration' date
        # Then sort by the oldest 'Last Updated' date
        items = self.sort_items()

        logging.info(f"expire_threshold: {expire_threshold} {type(expire_threshold)} - "
                     f"ignore_no_expiration: {ignore_no_expiration} ({type(ignore_no_expiration)}) - "
                     f"include_all: {include_all} {type(include_all)}")
        for item in items:

            # Get name of the record. If no name, we skip to next item in the list
            record_name = item.get("record_name")
            if not record_name:
                continue

            # Only list disabled entries if set to include_all
            enabled = item.get("enabled")
            if not include_all and not enabled:
                continue

            # Get the record type
            record_type = item.get("record_type", "")

            # Get the Vault Name
            vault_name = item.get("vault_name", "")

            # Get the expires and update values
            expires = item.get("expires", "")
            expires_age = item.get("expires_age")
            updated = item.get("updated")
            updated_age = item.get("updated_age")

            # Skip records with no Expiration Date set, only if 'ignore_no_expiration' and not 'include_all'
            if not expires:
                self.summary_values["missing"]["value"] += 1
                if ignore_no_expiration and not include_all:
                    continue

            # Handle those with Expiration Date
            if isinstance(expires_age, int):

                # Handle those which has not expired yet
                if expires_age < 0:
                    logging.info(f"'{record_name}' has not expired yet. "
                                 f"It will expire in {abs(expires_age)} days ({expires}).")

                    # Handle those within valid 'expire_threshold'
                    if isinstance(expire_threshold, int) and expire_threshold < abs(expires_age):
                        logging.info(f"'{record_name}' Expiration Date is within the valid specified threshold of "
                                     f"{expire_threshold} days. This record will start to be "
                                     f"reported in {abs(expires_age) - expire_threshold} days.")

                        # Only skipped if 'include_all' is not specified.
                        if not include_all:
                            continue

            # First column added is 'Record Name'. Second column is 'Last Updated'
            row = [record_name, record_type, vault_name, updated]

            # Third column added is 'Expiration'. If 'Expiration' value is empty, blank spaces are added instead.
            if expires:
                row.append(expires)
            else:
                row.append(" ")

            # The last column 'Comment' has to be created before added to the row.
            # The value of 'Comment' is dependent of the info from the expires and update values
            comment = ""
            if not enabled:
                comment += "Disabled. "

            if isinstance(expires_age, int):
                if expires_age <= 0:
                    comment += f"Will expire in {abs(expires_age)} days. "
                if expires_age > 0:
                    comment += f"Expired {expires_age} days ago. "

            if not expires:
                comment += f"Has no expiration date. "

            if isinstance(updated_age, int):
                comment += f"Updated {updated_age} days ago. "

            # Finally the 'Comment' column is added to the row, along with a linebreak for the row
            row.append(comment)

            # A little cosmetic touch to avoid plural where it should not be used
            comment = comment.replace(" 1 days", " 1 day")
            self.body.append(row)

            # Generate json with html table to be used in Teams
            if self.html_table:
                self.html_table.add_html_row(record_name, record_type, vault_name, updated, expires, comment)

        logging.info("report generated.")

    def get_teams_payload(self, title, text=""):
        if not isinstance(self.results, list):
            return

        if len(self.items) == 0:
            return

        if not text:
            text = self.get_html_table()

        ms_teams_payload = MSTeamsPayload(title, text,
                                          len(self.vaults),
                                          len(self.items),
                                          self.summary_values["missing"]["value"],
                                          self.summary_values["this_year"]["value"],
                                          self.summary_values["one_year"]["value"],
                                          self.summary_values["two_year"]["value"],
                                          self.summary_values["three_year"]["value"]
                                          )
        ms_teams_payload.set_json_facts()
        return ms_teams_payload.get_json_output()

    def get_html_table(self):
        if self.html_table:
            return self.html_table.get_table()


res = [{'vault_name': 'robim-kv-prod', 'record_type': 'certificate', 'out': [{'attributes': {'created': '2023-11-02T13:33:30+00:00', 'enabled': True, 'expires': '2024-11-01T23:59:59+00:00', 'notBefore': '2023-11-02T00:00:00+00:00', 'recoveryLevel': None, 'updated': '2023-11-02T13:33:30+00:00'}, 'id': 'https://robim-kv-prod.vault.azure.net/certificates/robim-beta', 'name': 'robim-beta', 'subject': '', 'tags': {}, 'x509Thumbprint': 'awhUALiOtIp1G5Om6vBqwkvD8O8=', 'x509ThumbprintHex': '6B085400B88EB48A751B93A6EAF06AC24BC3F0EF'}, {'attributes': {'created': '2023-05-12T11:31:56+00:00', 'enabled': True, 'expires': '2024-05-14T23:59:59+00:00', 'notBefore': '2023-05-12T00:00:00+00:00', 'recoveryLevel': None, 'updated': '2023-05-12T11:31:56+00:00'}, 'id': 'https://robim-kv-prod.vault.azure.net/certificates/robim-equinor-com', 'name': 'robim-equinor-com', 'subject': '', 'tags': {}, 'x509Thumbprint': 'S9Gn0+h4IJXP51MVbw/5ATF1FbA=', 'x509ThumbprintHex': '4BD1A7D3E8782095CFE753156F0FF901317515B0'}, {'attributes': {'created': '2023-10-13T08:36:40+00:00', 'enabled': True, 'expires': '2024-10-13T08:36:40+00:00', 'notBefore': '2023-10-13T08:26:40+00:00', 'recoveryLevel': None, 'updated': '2023-10-13T08:36:40+00:00'}, 'id': 'https://robim-kv-prod.vault.azure.net/certificates/robim-old-equinor-com', 'name': 'robim-old-equinor-com', 'subject': '', 'tags': {}, 'x509Thumbprint': 'MDdQL9gar1FzPaJTPLRnJAGIcz8=', 'x509ThumbprintHex': '3037502FD81AAF51733DA2533CB467240188733F'}]}, {'vault_name': 'robim-kv-prod', 'record_type': 'secret', 'out': [{'attributes': {'created': '2023-11-23T13:16:25+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-23T13:16:25+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/AccessItUri', 'managed': None, 'name': 'AccessItUri', 'tags': {}}, {'attributes': {'created': '2019-08-21T13:14:10+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T13:14:10+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/api-management-key', 'managed': None, 'name': 'api-management-key', 'tags': None}, {'attributes': {'created': '2023-08-21T10:22:39+00:00', 'enabled': True, 'expires': '2024-08-21T08:28:11+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-08-21T10:22:39+00:00'}, 'contentType': 'client secret', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/cams-api-client-secret', 'managed': None, 'name': 'cams-api-client-secret', 'tags': {}}, {'attributes': {'created': '2022-09-20T09:11:12+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2022-09-20T09:11:12+00:00'}, 'contentType': 'subscription key', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/cams-api-subscription-key', 'managed': None, 'name': 'cams-api-subscription-key', 'tags': {}}, {'attributes': {'created': '2023-08-21T10:23:36+00:00', 'enabled': True, 'expires': '2024-08-21T08:28:11+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-08-21T10:23:36+00:00'}, 'contentType': 'client secret', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/cams-roles-api-client-secret', 'managed': None, 'name': 'cams-roles-api-client-secret', 'tags': {}}, {'attributes': {'created': '2023-02-13T09:23:58+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-02-13T09:23:58+00:00'}, 'contentType': 'Subscription key', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/cams-roles-api-subscription-key', 'managed': None, 'name': 'cams-roles-api-subscription-key', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:25:50+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:25:50+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/DispensationBaseUri', 'managed': None, 'name': 'DispensationBaseUri', 'tags': {}}, {'attributes': {'created': '2023-10-10T08:52:05+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-10-10T08:52:05+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/DocmapBaseUri', 'managed': None, 'name': 'DocmapBaseUri', 'tags': {}}, {'attributes': {'created': '2023-11-17T13:40:38+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-17T13:40:38+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/EchoMapsUri', 'managed': None, 'name': 'EchoMapsUri', 'tags': {}}, {'attributes': {'created': '2023-11-17T13:42:38+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-17T13:42:38+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/EchoUri', 'managed': None, 'name': 'EchoUri', 'tags': {}}, {'attributes': {'created': '2023-02-23T15:09:08+00:00', 'enabled': True, 'expires': '2024-02-22T15:07:47+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-02-23T15:09:08+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/employeeapi-client-secret', 'managed': None, 'name': 'employeeapi-client-secret', 'tags': {}}, {'attributes': {'created': '2020-02-24T17:20:21+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2020-02-24T17:20:21+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/employeeapi-subscription-key', 'managed': None, 'name': 'employeeapi-subscription-key', 'tags': None}, {'attributes': {'created': '2023-04-19T08:22:51+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-04-19T08:22:51+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/enterprise-subscription-key', 'managed': None, 'name': 'enterprise-subscription-key', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:16:42+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:16:42+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/GisPlatformQueryBaseUri', 'managed': None, 'name': 'GisPlatformQueryBaseUri', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:17:02+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:17:02+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/GisQueryBaseUri', 'managed': None, 'name': 'GisQueryBaseUri', 'tags': {}}, {'attributes': {'created': '2019-08-21T13:18:19+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T13:18:19+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/influxdb-password', 'managed': None, 'name': 'influxdb-password', 'tags': None}, {'attributes': {'created': '2019-08-21T13:19:04+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T13:19:04+00:00'}, 'contentType': 'Username', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/influxdb-username', 'managed': None, 'name': 'influxdb-username', 'tags': None}, {'attributes': {'created': '2023-11-07T13:23:06+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:23:06+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/IwitBaseUri', 'managed': None, 'name': 'IwitBaseUri', 'tags': {}}, {'attributes': {'created': '2019-08-21T13:20:04+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T13:20:04+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/ksat-password', 'managed': None, 'name': 'ksat-password', 'tags': None}, {'attributes': {'created': '2019-08-21T13:21:58+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T13:21:58+00:00'}, 'contentType': 'Username', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/ksat-username', 'managed': None, 'name': 'ksat-username', 'tags': None}, {'attributes': {'created': '2023-11-07T13:28:26+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:28:26+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/MaintenanceNotificationBaseUrl', 'managed': None, 'name': 'MaintenanceNotificationBaseUrl', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:28:48+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:28:48+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/MaintenanceWorkOrderBaseUrl', 'managed': None, 'name': 'MaintenanceWorkOrderBaseUrl', 'tags': {}}, {'attributes': {'created': '2023-11-17T13:43:25+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-17T13:43:25+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/OptDashboardUri', 'managed': None, 'name': 'OptDashboardUri', 'tags': {}}, {'attributes': {'created': '2023-02-23T15:11:25+00:00', 'enabled': True, 'expires': '2024-02-22T15:09:15+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-02-23T15:11:25+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/organizationapi-client-secret', 'managed': None, 'name': 'organizationapi-client-secret', 'tags': {}}, {'attributes': {'created': '2020-02-24T17:19:36+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2020-02-24T17:19:36+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/organizationapi-subscription-key', 'managed': None, 'name': 'organizationapi-subscription-key', 'tags': None}, {'attributes': {'created': '2023-07-04T07:46:47+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-07-04T07:46:47+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/robim-client-secret', 'managed': None, 'name': 'robim-client-secret', 'tags': {}}, {'attributes': {'created': '2022-11-14T13:30:21+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2022-11-14T13:30:21+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/robim-cs', 'managed': None, 'name': 'robim-cs', 'tags': {}}, {'attributes': {'created': '2021-11-18T13:31:03+00:00', 'enabled': True, 'expires': '2022-11-18T13:28:58+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2021-11-18T13:31:03+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/robim-db-password', 'managed': None, 'name': 'robim-db-password', 'tags': {}}, {'attributes': {'created': '2021-11-18T13:31:33+00:00', 'enabled': True, 'expires': '2022-11-18T13:28:58+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2021-11-18T13:31:33+00:00'}, 'contentType': 'Username', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/robim-db-username', 'managed': None, 'name': 'robim-db-username', 'tags': {}}, {'attributes': {'created': '2024-02-06T11:53:43+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2024-02-06T11:53:43+00:00'}, 'contentType': '', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/RobimFrontendUri', 'managed': None, 'name': 'RobimFrontendUri', 'tags': {}}, {'attributes': {'created': '2019-08-21T16:35:48+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2019-08-21T16:35:48+00:00'}, 'contentType': 'Connectionstring', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/robimweb-as-cs', 'managed': None, 'name': 'robimweb-as-cs', 'tags': None}, {'attributes': {'created': '2023-04-26T08:43:30+00:00', 'enabled': True, 'expires': '2024-04-25T08:28:57+00:00', 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-04-26T08:43:30+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/smda-robim-client-secret', 'managed': None, 'name': 'smda-robim-client-secret', 'tags': {}}, {'attributes': {'created': '2021-05-03T11:19:17+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2021-05-03T11:19:17+00:00'}, 'contentType': 'Password', 'id': 'https://robim-kv-prod.vault.azure.net/secrets/smda-subscription-key', 'managed': None, 'name': 'smda-subscription-key', 'tags': None}, {'attributes': {'created': '2023-11-07T13:19:47+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:19:47+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/StidBaseUri', 'managed': None, 'name': 'StidBaseUri', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:25:16+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:25:16+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/SynergiCaseBaseUrl', 'managed': None, 'name': 'SynergiCaseBaseUrl', 'tags': {}}, {'attributes': {'created': '2023-11-23T13:15:17+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-23T13:15:17+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/SynergiRobimHelpdeskUri', 'managed': None, 'name': 'SynergiRobimHelpdeskUri', 'tags': {}}, {'attributes': {'created': '2023-09-05T09:11:08+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-09-05T09:11:08+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/timeseriesapi-robim-client-secret', 'managed': None, 'name': 'timeseriesapi-robim-client-secret', 'tags': {}}, {'attributes': {'created': '2023-11-07T13:24:48+00:00', 'enabled': True, 'expires': None, 'notBefore': None, 'recoverableDays': 90, 'recoveryLevel': 'Recoverable', 'updated': '2023-11-07T13:24:48+00:00'}, 'contentType': None, 'id': 'https://robim-kv-prod.vault.azure.net/secrets/WellcomBaseUri', 'managed': None, 'name': 'WellcomBaseUri', 'tags': {}}]}, {'vault_name': 'robim-kv-prod', 'record_type': 'key', 'out': []}]

kv_report = AzureKeyVaultReport(res)
kv_report.parse_results()
kv_report.report_summary()
report = kv_report.get_report()
print(report)

#kv_report.generate_report(expire_threshold=expire_threshold,
#                          ignore_no_expiration=ignore_no_expiration,
#                          include_all=include_all,
#                          teams_json=teams_output)
#
