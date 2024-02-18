"""
 ProvenanceDB test
 December 8th 2021 - P. Maeght
"""

import unittest
from unittest.mock import patch

from CTADIRAC.DataManagementSystem.DB.ProvenanceDB import ProvenanceDB


class TestProvDB(unittest.TestCase):
    """
    test class for ProvDB
    """

    def test_dictToObject(self):
        """
        Test _dictToObject
        """

        def mock_ProvenanceDB__init__(self):
            # No init need for _dictToObject
            pass

        with patch.object(ProvenanceDB, "__init__", mock_ProvenanceDB__init__):
            # New ProvenanceDB
            pdb = ProvenanceDB()

            # Dummy fromDict dict
            item = {
                "field1": "OK",
                "field2": "OK",
            }

            # Table Object
            class Table:
                field1 = "NOK"
                field2 = "NOK"

            # ret = pdb._dictToObject(Table, item)
            pdb._dictToObject(Table, item)

            # Table updated
            assert Table.field2 == b"OK"


if __name__ == "__main__":
    unittest.main()
