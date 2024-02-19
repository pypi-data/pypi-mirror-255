# -*- coding: utf-8 -*-
import logging
import os
import pathlib

from datetime import datetime
from typing import Optional

from . import constants

from file_helper_utils import utils


DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP,
)


class Manager:
    """Class for managing the creation of the validation modules."""

    def __init__(self, **kwargs):
        """Constructor for Manager."""
        self.config = kwargs.get("config", None)
        self.config_file = kwargs.get("config_file", None)
        self.logfile = kwargs.get("logfile", None)
        self.outdir = kwargs.get("outdir", DEFAULT_OUTDIR)
        self.verbose = kwargs.get("verbose", constants.DEFAULT_VERBOSE)

        logging.info(f"Instantiated Manager in file '{os.path.abspath(__file__)}'")

    def profile_file(
            self,
            infile: str,
            outfile: str = None
        ) -> Optional[str]:

        if infile is None or infile == "":
            raise Exception("infile was not defined")

        utils.check_infile_status(infile)

        utils.check_infile_status(infile)
        md5sum = utils.calculate_md5(infile)
        date_created = utils.get_file_creation_date(infile)
        size = utils.get_file_size(infile)
        basename = os.path.basename(infile)
        line_count = None

        if basename.endswith(".csv") or basename.endswith(".txt") or basename.endswith(".tsv"):
            line_count = utils.get_line_count(infile)
        else:
            logging.info(f"File '{infile}' is not a text file, so line count will not be calculated")

        if outfile is None:
            outfile = os.path.join(
                self.outdir,
                f"{basename}.profile.txt"
            )
            logging.info(f"outfile was not defined and therefore was set to '{outfile}'")

        self._write_profile_metadata_file(
            infile=infile,
            outfile=outfile,
            md5sum=md5sum,
            date_created=date_created,
            size=size,
            line_count=line_count,
        )

    def _write_profile_metadata_file(
            self,
            infile: str,
            outfile: str,
            md5sum: str,
            date_created: datetime,
            size: int,
            line_count: Optional[int],
    ) -> None:

        dirname = os.path.dirname(outfile)
        if not os.path.exists(dirname):
            pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory '{dirname}'")
            if self.verbose:
                print(f"Created directory '{dirname}'")

        with open(outfile, 'w') as of:
            of.write(f"## method-profiled: {os.path.abspath(__file__)}\n")
            of.write(f"## date-profiled: {str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))}\n")
            of.write(f"## profiled-by: {os.environ.get('USER')}\n")

            if self.logfile is not None:
                of.write(f"## logfile: {self.logfile}\n")

            of.write(f"file: {os.path.realpath(infile)}\n")
            of.write(f"md5sum: {md5sum}\n")
            of.write(f"date_created: {date_created}\n")
            of.write(f"file_size: {size}\n")

            if line_count is not None:
                of.write(f"line_count: {line_count}\n")

        logging.info(f"Wrote profile metadata file '{outfile}'")
        if self.verbose:
            print(f"Wrote profile metadata file '{outfile}'")
