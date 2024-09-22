import json
import signal
import sys
from typing import Dict, Union, List
from contextlib import contextmanager
from Individual import Supplier, Party
from Entities import RegisterEntry, MemoEntry, OrderForm, Item, ItemEntry
from Tests import TestKhataReport
from Reports import make_report
from Tests import check_status_and_return_class, cleanup

 # Create a Memo Entry
part_input = {'memo_number': 384339,
                'register_date': '2023-08-04',
                'amount': 10,
                'party_id': 78,
                'supplier_id': 5,
                'payment': [{'bank': 'RTGS', 'id': 1, 'cheque': '234'}],
                'mode': 'Part'
                }
breakpoint()
part_memo = check_status_and_return_class(
    MemoEntry.insert(part_input, get_cls=True))
