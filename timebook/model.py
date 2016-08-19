import collections
import json
import logging
import os
import pathlib
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class Entry():
    """Contains all data for a single entry"""

    def __init__(self, user_id="", name="", date=None, time_in=None,
                 time_out="", index=None, now=None):
        """Parameters have different default behaviors, and can all be
        overwritten.
        """

        if now is None:
            now = datetime.today()
        if date is None:
            date = datetime.strftime(now, "%Y-%m-%d")
        if time_in is None:
            time_in = datetime.strftime(now, "%H:%M:%S")
        if index is None:
            index = self.make_index()

        self.user_id = user_id
        self.name = name
        self.date = date
        self.time_in = time_in
        self.time_out = time_out
        self.index = index

        logger.debug("Entry object initialized: {}".format(repr(self)))

    def __repr__(self):
        """Return an unambiguous representation of the entry."""
        entry = ("Entry(user_id='{}', name='{}', date='{}', "
                 "time_in='{}', time_out='{}', index='{}')")
        return entry.format(
            self.user_id,
            self.name,
            self.date,
            self.time_in,
            self.time_out,
            self.index
        )

    def __eq__(self, other):
        """'==' returns true if both objects are instances of Entry
        and have identical attributes.
        """
        if isinstance(other, Entry):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """'!=' returns the opposite of '=='."""
        return not self == other

    @staticmethod
    def make_index():
        """Generate a UUID version 4 (basically random)"""
        return str(uuid.uuid4())

    def sign_out(self, time=None):
        """Get the time the user signed out"""
        if time is None:
            time = datetime.today()
        self.time_out = datetime.strftime(time, "%H:%M:%S")
        logger.info("Entry signed out: {}".format(repr(self)))


class Timesheet():
    """Contains multiple entries"""

    def __init__(self, data_file=None):
        self.sheet = collections.OrderedDict()
        self.signed_in = []
        data_dir = pathlib.Path('.', 'data')

        if data_file is None:
            today = datetime.strftime(datetime.today(), "%Y-%m-%d")
            file_name = today + ".json"
            data_file = data_dir.joinpath(file_name)

        self.data_file = data_file

        self.load_sheet()
        data_dir.mkdir(exist_ok=True, parents=True)
        logger.debug("Timesheet object initialized.")
        logger.debug("Timesheet data file: {}".format(self.data_file))

        self._update_signed_in()

    def _update_signed_in(self):
        """Update the list of all entries that haven't been signed out."""
        self.signed_in = [k for k, v in self.sheet.items() if v['Out'] == ""]
        logger.debug("Signed in entries: {}".format(self.signed_in))

    def load_entry(self, index):
        """Load and return an entry object."""
        entry = Entry(
            user_id=self.sheet[index]['User ID'],
            name=self.sheet[index]['Name'],
            date=self.sheet[index]['Date'],
            time_in=self.sheet[index]['In'],
            time_out=self.sheet[index]['Out'],
            index=index
        )
        logger.debug("Entry loaded: {}".format(repr(entry)))
        return entry

    def save_entry(self, entry, index=None):
        """Format an entry as a dictionary and add it to the timesheet
        with its index as the key.
        """
        if index is None:
            index = entry.index

        entry_data = collections.OrderedDict()
        entry_data['User ID'] = entry.user_id
        entry_data['Name'] = entry.name
        entry_data['Date'] = entry.date
        entry_data['In'] = entry.time_in
        entry_data['Out'] = entry.time_out

        self.sheet[index] = entry_data
        logger.debug("Entry saved: {}".format(repr(entry)))
        self._update_signed_in()

    def remove_entry(self, index):
        """Delete a single entry from the timesheet."""
        removed_entry = self.load_entry(index)
        del self.sheet[str(index)]
        logger.debug("Entry removed: {}".format(removed_entry))
        self._update_signed_in()

    def search_entries(self, search_term):
        """Look through the values of all entries.
        Return a set of the indices of all entries that have a value matching
        the search term.
        """
        indices = {
            k for k, v in self.sheet.items() if search_term in str(v.items())
        }
        logger.debug(
            "Searched for {}. Results: {}".format(
                search_term, indices
            )
        )
        return indices

    def load_sheet(self, data_file=None):
        """Read the timesheet from a json file."""
        if data_file is None:
            data_file = self.data_file

        try:
            # TODO(amin): lift this IO out into a separate function.
            # Make this method take a file-like-object.
            with data_file.open('r') as data:
                self.sheet = json.load(
                    data, object_pairs_hook=collections.OrderedDict
                )
        except FileNotFoundError:
            logger.debug(
                "{} not found. It will be created.".format(self.data_file)
            )
        # TODO(amin): use utils.validate_json() for validation
        except json.decoder.JSONDecodeError as e:
            backup = data_file.with_suffix('.bak')
            os.rename(str(data_file), str(backup))
            logger.error(
                "Invalid JSON file: {}. {} moved to {}".format(
                    e, data_file, backup
                )
            )
        else:
            logger.debug("Sheet loaded from {}".format(data_file))
        finally:
            self._update_signed_in()

    def save_sheet(self, data_file=None):
        """Write the timesheet to json file."""
        if data_file is None:
            data_file = self.data_file

        with data_file.open('w') as f:
            json.dump(self.sheet, f, indent=4, sort_keys=False)
        logger.debug("Sheet saved to {}".format(data_file.resolve()))
