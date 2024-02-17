import gspread  # type: ignore
import os
import logging
import pandas
import typing


logger = logging.getLogger('g3tables.utils.gdrive')


class TableMetadataDict(typing.TypedDict):
    id: str
    name: str
    createdTime: str
    modifiedTime: str


@typing.overload
def list_tables_from_gdrive(
    project: str | typing.Any | None, with_meta: typing.Literal[True]
) -> list[TableMetadataDict]:
    ...


@typing.overload
def list_tables_from_gdrive(
    project: str | typing.Any | None, with_meta: typing.Literal[False]
) -> list[str]:
    ...


def list_tables_from_gdrive(
    project: str | typing.Any | None, with_meta: bool = True
) -> list[TableMetadataDict] | list[str]:
    logger.info('Connecting to Google Drive repository')
    creds_file = os.path.join(os.path.dirname(__file__), "creds.json")
    client = gspread.service_account(filename=creds_file)
    logger.info('Collecting Google Drive G3 project tables')
    tables: list[TableMetadataDict] = [
        table for table in client.list_spreadsheet_files()
        ]
    if project is not None:
        logger.info('Filtering "%s" Google Drive G3 project tables', project)
        tables = [
            table for table in tables
            if str(project).casefold() in str(table['name']).casefold()
            ]
    if with_meta:
        return tables
    return [table['name'] for table in tables]


def get_table_data_from_gdrive(
    gdrive_table_name: str,
    header_row: int = 1,
    include_sheets: typing.Optional[typing.Iterable[str]] = None,
    exclude_sheets: typing.Optional[typing.Iterable[str]] = None
) -> dict[str, pandas.DataFrame]:
    """both excluded and included == excluded"""
    logger.info('Connecting to Google Drive repository')
    creds_file = os.path.join(os.path.dirname(__file__), "creds.json")
    client = gspread.service_account(filename=creds_file)
    try:
        logger.info('Loading spreadsheet "%s"', gdrive_table_name)
        table = client.open(gdrive_table_name)
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(
            'Unable to access spreadsheet "%s". Make sure '
            'that the table name is spelled correctly and '
            'that access to the table has been granted to '
            '"el-script@g3-spreadsheet-sync.iam.gserviceaccount.com".',
            gdrive_table_name
            )
        return {}
    sheets = {}
    for sheet in table.worksheets(exclude_hidden=True):
        if (
            (exclude_sheets and sheet.title in exclude_sheets) or
            (include_sheets and sheet.title not in include_sheets)
        ):
            logger.debug('Ignoring sheet "%s"', sheet.title)
            continue
        try:
            logger.info('Loading sheet "%s"', sheet.title)
            sheets[sheet.title] = pandas.DataFrame(
                sheet.get_all_records(
                    head=header_row, numericise_ignore=['all']
                    )
                )
        except Exception as exp:
            if logger.isEnabledFor(logging.WARNING):  # optimize err str format
                err = f'Failed to load sheet "{sheet.title}"'
                if (exp_str := str(exp)):
                    err = f'{err} ({exp_str})'
                logger.warning(err)
    return sheets
