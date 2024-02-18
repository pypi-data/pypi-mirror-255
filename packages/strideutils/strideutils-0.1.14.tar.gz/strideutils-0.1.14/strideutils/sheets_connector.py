"""
    Gives easy, programatic access to Google sheets.
    By default, any Google Sheet that the email
        publicsheets@stride-nodes.iam.gserviceaccount.com
    can access will be readable by this API.
"""

import json
import warnings
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, cast

import gspread
import pandas as pd
from apiclient import discovery
from google.oauth2 import service_account
from gspread.exceptions import WorksheetNotFound

from strideutils.stride_config import config

# these are default scopes that we hope to access
SCOPES = (
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
)


@lru_cache
def get_auth(
    scopes: Tuple[str, ...] = SCOPES,
    service: str = 'sheets',
    version: str = 'v4',
):
    """
    Grabs auth based on environment, service, and scopes.
    """
    creds = None
    try:
        auth_dict = config.PUBLICSHEETS_AUTH
        if config.ENV == 'PROD':
            # Auth info is passed as a string in prod
            auth_dict = json.loads(cast(str, auth_dict))
        creds = service_account.Credentials.from_service_account_info(auth_dict, scopes=scopes)
    except AttributeError:
        print('Google sheets auth is not found or badly configured')
        raise
    service = discovery.build(service, version, credentials=creds)
    gc = gspread.authorize(creds)
    return gc


def grab_sheet(
    sheet_id: str,
    sheet_name: str,
    columns_labeled: bool = True,
    worksheet: Optional[gspread.Worksheet] = None,
    scopes: Tuple[str, ...] = SCOPES,
    _cache: Dict[str, Any] = {},
) -> pd.DataFrame:
    """
        The primary function you will call in this file. Given a sheet_id and the name of a Sheet, will return
        the contents as a Pandas Dataframe.
        If the first row is a column label (e.g. a normal, well-defined DataFrame) set columns_labeled=True.
        Else, if you just want the results as a grid, set columns_labeled=False.
    Args:
        sheet_id (str): The ID of the Sheet (found in the URL)
        sheet_name (str): The Worksheet name (found in the bottom of Google Sheets)
        columns_labeled (bool): Whether the first row defines column names for a DataFrame. Defaults to True.
        worksheet (GSpread Auth): Output of get_auth, can be passed in to avoid loading data again. Defaults to None.
        scopes (List of Str): What auth you want for the sheet. Defaults to SCOPES.
    Returns:
        DataFrame: DataFrame of your desired values.
    """
    gc = get_auth(scopes=scopes)
    if worksheet is None:
        joint_key = sheet_id + '_' + sheet_name
        if joint_key in _cache:
            opened_sheet = _cache[joint_key]
        else:
            opened_sheet = gc.open_by_key(sheet_id)
            _cache[joint_key] = opened_sheet
        worksheet = _cache[joint_key].worksheet(sheet_name)

    assert worksheet is not None, "worksheet never initialized"

    list_of_dicts = worksheet.get_all_records() if columns_labeled else worksheet.get_all_values()

    return pd.DataFrame(list_of_dicts)


def write_sheet(
    df: pd.DataFrame,
    sheet_id: str,
    sheet_name: str,
    worksheet: Optional[gspread.Worksheet] = None,
    scopes: Tuple[str, ...] = SCOPES,
):
    """
        Allows you to write a Dataframe to a Google Sheet.
    Args:
        sheet_id (str): The ID of the Sheet (found in the URL)
        sheet_name (str): The Worksheet name (found in the bottom of Google Sheets)
        worksheet (GSpread Auth): Output of get_auth, can be passed in to avoid loading data again. Defaults to None.
        scopes (List of Str): What auth you want for the sheet. Defaults to SCOPES.
    Returns:
        DataFrame: DataFrame of your desired values.
    """
    while len(df) < 30:
        df.loc[len(df)] = pd.Series(dtype=float)

    df = df.fillna('')
    gc = get_auth(scopes=scopes)
    if worksheet is None:
        try:
            worksheet = gc.open_by_key(sheet_id).worksheet(sheet_name)
        except WorksheetNotFound:
            # sheet doesn't exist, so we create it
            worksheet = gc.open_by_key(sheet_id).add_worksheet(title=sheet_name, rows="1", cols="1")
    total_len = len(df) + 1
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        worksheet.update(values=[df.columns.values.tolist()] + df.values.tolist(), range_name=f'A1:ZZ{total_len}')


def reorder_sheet(
    sheet_id: str,
    sheet_name: str,
    new_location: int = 0,
    scopes: Tuple[str, ...] = SCOPES,
):
    """
        Alloworksheet you to move a sheet to a new location in the Google Sheet.
        `new_location` is the new index of the sheet.
    Args:
        sheet_id (str): The ID of the Sheet (found in the URL)
        sheet_name (str): The Worksheet name (found in the bottom of Google Sheets)
        new_location (int): The new index of the sheet. Defaults to 0.
        scopes (List of Str): What auth you want for the sheet. Defaults to SCOPES.
    Returns:
        None
    """
    gc = get_auth(scopes=scopes)
    client = gc.open_by_key(sheet_id)
    all_sheets = client.worksheets()
    current_order = [sheet.title for sheet in all_sheets]

    if sheet_name not in current_order:
        raise ValueError(f'{sheet_name} not found in Sheet. Current sheets: {current_order}')

    if (new_location > len(current_order)) or (new_location < 0):
        raise ValueError(f'New location must be between 0 and {len(current_order)}')

    # get the desired new order
    location_of_sheet = current_order.index(sheet_name)
    location_of_next_sheet = location_of_sheet + 1
    new_worksheets = all_sheets[:location_of_sheet] + all_sheets[location_of_next_sheet:]
    new_worksheets.insert(new_location, all_sheets[location_of_sheet])

    # update the sheet
    requests = []
    for i, sheet in enumerate(new_worksheets):
        requests.append(
            {"updateSheetProperties": {"properties": {"index": i + 1, "sheetId": sheet.id}, "fields": "index"}}
        )
    client.batch_update({"requests": requests})


def get_sheet_names(sheet_id: str, scopes: Tuple[str, ...] = SCOPES) -> List[str]:
    """
        Gets the string titles of sheets in a Google Sheet.
    Args:
        sheet_id (str): The ID of the Sheet (found in the URL)
        scopes (List of Str): What auth you want for the sheet. Defaults to SCOPES.
    Returns:
        List of Str: List of sheet names.
    """
    gc = get_auth(scopes=scopes)
    client = gc.open_by_key(sheet_id)
    all_sheets = client.worksheets()
    return [sheet.title for sheet in all_sheets]
