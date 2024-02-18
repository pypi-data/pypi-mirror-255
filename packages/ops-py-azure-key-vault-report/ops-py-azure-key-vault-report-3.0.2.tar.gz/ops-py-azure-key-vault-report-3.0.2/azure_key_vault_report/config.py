#!/usr/bin/env python

config = {
    "summary":
        {"widths": [],
         "heading": ["Summary", "Comment"],
         "vaults": {"text": "Total number of vaults", "value": 0},
         "records": {"text": "Total number of records", "value": 0},
         "missing": {"text": "Records missing Expiration Date", "value": 0},
         "this_year": {"text": "Records updated in the last year", "value": 0},
         "one_year": {"text": "Records NOT updated in the last year", "value": 0},
         "two_years": {"text": "Records NOT updated for the last 2 years", "value": 0},
         "three_years": {"text": "Records NOT updated for the last 3 years", "value": 0}
         },
    "report":
        {"widths": [],
         "heading": ["Record Name", "Record Type", "Vault Name", "Last Updated", "Expiration",
                     "Comment"]
         }
}
