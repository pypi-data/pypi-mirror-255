from pathlib import Path

import pandas as pd

import om_code.omerrors as errors
from om_code.parseTecan import parseTecan
from om_code.parseSunrise import parseSunrise


def parseplate(
    platereaderfile, platereadertype, wdirpath=".", sheetnumber=0, export=False
):
    """
    Parse plate-reader output into a long dataframe.

    Note that the plate-reader file is assumed to be an Excel file
    and that time is converted into hours.

    Parameters
    ----------
    platereaderfile: str
        The name of the data file created by a platereader.
    platereadertype: str
        The type of plate reader, currently only "Tecan"
        for a Tecan M200 or Tecan F200.
    wdirpath: str, optional
        The path to the platereader_file.
    sheetnumber: integer, optional
        The sheet to read from an excel file.
    export: boolean, optional
        If True, write parsed data to tsv file.

    Example
    -------
    >>> from om_code.parseplate import parseplate
    >>> rdf= parseplate("ExampleData.xlsx", "Tecan", wdirpath="data")
    >>> print(rdf)

                time well      OD   GFP  AutoFL  mCherry
    0       0.000000   A1  0.2555  46.0    18.0     19.0
    1       0.232306   A1  0.2725  45.0    17.0     17.0

    """
    if isinstance(wdirpath, str):
        wdirpath = Path(wdirpath)
    if platereadertype == "tidy":
        print(
            "Columns must be labelled 'time', 'well', 'OD', etc., "
            "and time must be in units of hours."
        )
        try:
            if ".tsv" in platereaderfile:
                rdf = pd.read_csv(str(wdirpath / platereaderfile), sep="\t")
            else:
                rdf = pd.read_csv(str(wdirpath / platereaderfile))
        except FileNotFoundError:
            raise errors.FileNotFound(str(wdirpath / platereaderfile))
        if rdf.time.max() > 100:
            print("Warning: time does not appear to be in hours.")
        return rdf
    else:
        # load data
        try:
            dfd = pd.read_excel(
                str(wdirpath / platereaderfile), sheet_name=sheetnumber
            )
        except FileNotFoundError:
            raise errors.FileNotFound(str(wdirpath / platereaderfile))
        # create a dict to store data
        rdict = {"time": [], "well": []}
        # parse loaded data frame
        if platereadertype == "Tecan":
            rdict = parseTecan(dfd, rdict)
        elif platereadertype == "Sunrise":
            rdict = parseSunrise(dfd, rdict)
        else:
            raise ValueError(f"{platereadertype} not recognised.")
        # convert parsed dict to data frame
        rdf = pd.DataFrame.from_dict(rdict)
        if export:
            outname = platereaderfile.split(".")[0] + ".tsv"
            print(f"exporting {outname}")
            rdf.to_csv(str(wdirpath / outname), sep="\t")
        return rdf
