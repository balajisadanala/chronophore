import collections
import json
import logging
import os
from datetime import datetime

import chronophore

logger = logging.getLogger(__name__)


Entry = collections.namedtuple('Entry', 'date name time_in time_out user_id')


class Timesheet():
    """Contains multiple entries"""

    def __init__(self, data_file=None):
        self.sheet = collections.OrderedDict()
        self.signed_in = []
        data_dir = chronophore.config.DATA_DIR

        if data_file is None:
            today = datetime.strftime(datetime.today(), "%Y-%m-%d")
            file_name = today + ".json"
            data_file = data_dir.joinpath(file_name)

        self.data_file = data_file

        try:
            chronophore.utils.validate_json(self.data_file)
        except FileNotFoundError:
            logger.debug(
                "{} not found. It will be created.".format(data_file)
            )
        except json.decoder.JSONDecodeError as e:
            backup = data_file.with_suffix('.bak')
            os.rename(str(data_file), str(backup))
            logger.error("{}. {} moved to {}".format(e, data_file, backup))
        else:
            with data_file.open('r') as f:
                self.load_sheet(data=f)

        logger.debug("Timesheet object initialized.")
        logger.debug("Timesheet data file: {}".format(self.data_file))

        self._update_signed_in()

    def __iter__(self):
        return iter(self.sheet)

    def __contains__(self, key):
        return key in self.sheet.keys()

    def __len__(self):
        return len(self.sheet)

    def __getitem__(self, key):
        """Load and return an entry object."""
        entry = Entry(
            date=self.sheet[key]['date'],
            name=self.sheet[key]['name'],
            time_in=self.sheet[key]['time_in'],
            time_out=self.sheet[key]['time_out'],
            user_id=self.sheet[key]['user_id'],
        )
        logger.debug("Entry loaded: {}".format(repr(entry)))
        return entry

    def __setitem__(self, key, entry):
        """Format an entry as an ordered dict and
        add it to the timesheet.
        """
        self.sheet[key] = entry._asdict()
        logger.debug("Entry saved: {}".format(repr(entry)))
        self._update_signed_in()
        self.save_sheet()

    def _update_signed_in(self):
        """Update the list of all entries that haven't been signed out."""
        self.signed_in = [
            k for k, v in self.sheet.items() if v['time_out'] is None
        ]
        logger.debug("Signed in entries: {}".format(self.signed_in))

    def load_sheet(self, data):
        """Read the timesheet from a json file."""
        self.sheet = json.load(data, object_pairs_hook=collections.OrderedDict)
        logger.debug("Sheet loaded")
        self._update_signed_in()

    def save_sheet(self, data_file=None):
        """Write the timesheet to json file."""
        if data_file is None:
            data_file = self.data_file

        data_file.parent.mkdir(exist_ok=True, parents=True)
        with data_file.open('w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=False)
        logger.debug("Sheet saved to {}".format(data_file.resolve()))
