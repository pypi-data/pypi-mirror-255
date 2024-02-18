#!/usr/bin/env python

# stdlib imports
import argparse
import json
import logging
import pathlib
import sys
import tempfile
from urllib.request import urlopen

# third party imports
import numpy as np
import pandas as pd
import rasterio

# local imports
from esi_utils_pager.calc import calc_pager_event, calc_pager_events
from esi_utils_pager.config import read_config

EVENT_TEMPLATE = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{eventid}.geojson"
)


def main():
    helpstr = (
        "Render complete empirical/semi-empirical PAGER results.\n\n"
        "Default behavior renders PAGER results for a set of earthquakes\n"
        "as a formatted DataFrame with multiple rows of exposure and loss,\n"
        "one row per country, plus a final row with totals. Output columns (in order):\n"
        "EventID: ComCat event ID\n"
        "Time: Event Time (y-m-d h:m:s)\n"
        "Latitude: Event hypocentral latitude\n"
        "Longitude: Event hypocentral longitude\n"
        "Depth: Event hypocentral depth\n"
        "Magnitude: Event magnitude\n"
        "Location: Event location description\n"
        "CountryCode: Country code where exposures/losses occur (or Total)\n"
        "MMI01: Population exposure to shaking at MMI level 1\n"
        "...\n"
        "MMI10: Population exposure to shaking at MMI level 10\n"
        "Fatalities: Fatalities due to shaking\n"
        "EconMMI01: Economic exposure to shaking at MMI level 1\n"
        "...\n"
        "EconMMI10: Economic exposure to shaking at MMI level 10\n"
        "Dollars: Economic losses (USD) due to shaking\n"
    )
    parser = argparse.ArgumentParser(
        description=helpstr,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--folder", help="A folder containing many ShakeMap grid.xml files."
    )
    group.add_argument("-g", "--grid-xml", help="A ShakeMap grid.xml file.")
    group.add_argument(
        "-e",
        "--eventid",
        help="ComCat event ID - preferred ShakeMap grid.xml will be used.",
    )
    parser.add_argument(
        "-s",
        "--semimodel",
        help="Calculate semi-empirical model results as well.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-o", "--outfile", help="Specify output file (.xlsx for Excel, .csv for CSV)"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="Print progress output to the screen",
    )

    args = parser.parse_args()

    if args.verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.CRITICAL
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s %(message)s",
        handlers=[logging.StreamHandler()],
    )

    if args.folder:
        dataframe = calc_pager_events(args.folder, args.verbose, args.semimodel)
    elif args.eventid:
        url = EVENT_TEMPLATE.format(eventid=args.eventid)
        with tempfile.TemporaryDirectory() as tempdir:
            with urlopen(url) as fh:
                data = fh.read().decode("utf8")
                jdict = json.loads(data)
                if "shakemap" not in jdict["properties"]["types"]:
                    print(f"No ShakeMap for event {args.eventid}. Exiting.")
                    sys.exit(1)
                shakemap = jdict["properties"]["products"]["shakemap"][0]
                grid_url = shakemap["contents"]["download/grid.xml"]["url"]
                with urlopen(grid_url) as fh2:
                    xdata = fh2.read().decode("utf8")

                tmpgridfile = pathlib.Path(tempdir) / "tmp.xml"
                with open(tmpgridfile, "wt") as fout:
                    fout.write(xdata)
                config = read_config()
                dataframe = calc_pager_event(tmpgridfile, config, args.semimodel)
    else:
        config = read_config()
        dataframe = calc_pager_event(args.grid_xml, config, args.semimodel)

    if args.outfile:
        print(f"Saving {len(dataframe)} rows to {args.outfile}")
        if args.outfile.endswith(".xlsx"):
            dataframe.to_excel(args.outfile, index=False)
        else:
            dataframe.to_csv(args.outfile, index=False)
        sys.exit(0)
    else:
        print(dataframe.to_string(index=False))


if __name__ == "__main__":
    main()
