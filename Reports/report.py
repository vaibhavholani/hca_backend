from __future__ import annotations
from typing import List, Dict

class Report: 
    def __init__(self, 
                 header_ids: List[int], 
                 subheader_ids: List[int], 
                 start_date: str, 
                 end_date: str) -> None:
        pass

    def generate_table(self) -> Dict:
        pass
        # call the apt function from the 

class Table:
    """
    Returns table data json in the following format
    {
        "title": "Party Name: ...",
        "subheadings": [
          {
            "title": "Supplier Name: ...",
            "dataRows": [{  }],
            "specialRows": [
              {"name": "Total", "value": 1200000.0,"column": "BillNo", "beforeData": false}
            ]
          },
        ]
      }
    """
    def __init__(self) -> None:
        pass