import csv
import logging
import os
import unittest
from logging import info, warning

import cantools

from packages.bridge.index import onCANMessage

class MyTestCase(unittest.TestCase):
    def test_loading_CAN_records(self):

        print(os.getcwd())
        cans = [cm[2] for cm in load_space_delimited_file("../../../debug/data/candump-2025-01-12_125209.log")]

        print(cans[0])
        return cans

    def test_decode_CAN(self, msg=None):
        # logging.getLogger().setLevel(logging.INFO)
        # use input msg or create from sample data
        msg = msg or CanMessage(*'0003#0FF6100004FFA01B'.split('#'))
        # load database unless cached
        db = cantools.database.load_file('../db/tesla_can.dbc')

        onCANMessage(msg, sendToBus=False, database=db)

    def test_decode_all_records(self, max_records=50):
        cans = self.test_loading_CAN_records()

        for mstr in cans[:max_records or len(cans)]:
            self.test_decode_CAN(msg=CanMessage(*mstr.split('#')))

class CanMessage:
    def __init__(self, arbitration_id, data):
        """
        Constructor to initialize a CAN message with an arbitration ID and data.

        Parameters:
            arbitration_id (int or str): The arbitration ID of the message (typically an integer).
            data (bytes or str): The data to be sent, either as a byte sequence or a hex string.
        """
        # Initialize the fields
        self.arbitration_id = int(arbitration_id, 16)
        self.data = self._process_data(data)

    def _process_data(self, data):
        """
        Helper method to ensure data is in bytes format.

        Parameters:
            data (bytes or str): The data to be processed.

        Returns:
            bytes: The processed data in bytes format.
        """
        if isinstance(data, str):
            # If data is a hex string, convert it to bytes
            return bytes.fromhex(data)
        elif isinstance(data, bytes):
            return data
        else:
            raise ValueError("Data must be either a hex string or a byte sequence.")

    def __repr__(self):
        """Return a string representation of the CAN message."""
        return f"CanMessage(arbitration_id={self.arbitration_id}, data={self.data.hex()})"

    def to_dict(self):
        """
        Converts the CanMessage instance into a dictionary.

        Returns:
            dict: Dictionary representation of the CanMessage.
        """
        return {
            'arbitration_id': self.arbitration_id,
            'data': self.data.hex()
        }

    def get_arbitration_id(self):
        """Returns the arbitration ID of the CAN message."""
        return self.arbitration_id

    def get_data(self):
        """Returns the data of the CAN message in byte format."""
        return self.data


def load_space_delimited_file(file_path):
    """
    Loads a space-delimited file using the csv module and returns its contents as a list of lists.
    Each line in the file represents one record.

    Parameters:
        file_path (str): The path to the space-delimited file.

    Returns:
        List[List[str]]: A list where each item is a list of strings representing a record.
    """
    records = []

    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=' ')  # Using space as the delimiter
            for row in reader:
                # Strip out any empty strings that might be caused by multiple spaces
                records.append([field for field in row if field])

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return records

if __name__ == '__main__':
    unittest.main()
