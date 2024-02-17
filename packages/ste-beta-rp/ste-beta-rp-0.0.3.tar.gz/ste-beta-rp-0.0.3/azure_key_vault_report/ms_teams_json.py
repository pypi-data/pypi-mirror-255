#!/usr/bin/env python

import json


########################################################################################################################

class MSTeamsPayload(object):
    """
        Parameters
        ----------

    Attributes
    ----------
    Attributes
    ----------

    results : list
        The list of results from the 'az keyvault' commands, enriched with 'vault_name' and 'record_type'

    Methods
    -------

    """

    def __init__(self, title, text, vaults_count, records_count, missing_ed_count,
                 this_year, one_year, two_years, three_years):
        """
        Parameters
        ----------
        title : str
            The 'activityTitle' which is the title of the message in MS Teams
        facts : list
            The list of 'facts' which is presented above the html table.
        text : str
            The text to be added below the 'facts'. The 'text' may be in html format.
        """

        self.title = str(title)
        self.text = str(text)
        self.vaults_count = int(vaults_count)
        self.records_count = int(records_count)
        self.missing_ed_count = int(missing_ed_count)
        self.this_year = int(this_year)
        self.one_year = int(one_year)
        self.two_years = int(two_years)
        self.three_years = int(three_years)
        self.facts = []

    def set_json_facts(self):
        """generates the fact used in the json output for MS Teams"""

        self.facts = [
            {"name": "Total number of Key Vaults:",
             "value": self.vaults_count
             },
            {"name": "Total number of records:",
             "value": self.records_count
             }
        ]

        if self.missing_ed_count:
            self.facts.append(
                {"name": "Records missing Expiration Date:",
                 "value": self.missing_ed_count
                 }
            )

        if self.this_year:
            self.facts.append(
                {"name": "Records updated in the last year:",
                 "value": self.this_year
                 }
            )

        if self.one_year:
            self.facts.append(
                {"name": "Records NOT updated in the last year:",
                 "value": self.one_year
                 }
            )

        if self.two_years:
            self.facts.append(
                {"name": "Records NOT updated for the last 2 years:",
                 "value": self.two_years
                 }
            )

        if self.three_years:
            self.facts.append(
                {"name": "Records NOT updated for the last 3 years:",
                 "value": self.three_years
                 }
            )

    def get_facts(self):
        return self.facts

    def get_json_output(self):
        """add the facts and text to the json output for MS Teams, and then return the json output


        Returns
        -------
        json object
            A payload in json format. If not fact are provided, then None is returned.
        """

        if not self.facts:
            return

        json_output = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "-",
            "sections": [
                {
                    "activityTitle": self.title,
                    "activitySubtitle": "",
                    "activityImage": "",
                    "facts": [],
                    "markdown": True
                },
                {
                    "startGroup": True,
                    "text": ""
                }
            ]
        }

        json_output["sections"][0]["facts"] = self.facts
        json_output["sections"][1]["text"] = self.text

        return json.dumps(json_output)
