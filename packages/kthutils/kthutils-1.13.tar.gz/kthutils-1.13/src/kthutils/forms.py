import typer
from typing import Annotated, Any, List, Tuple

import typerconf
import weblogin
import weblogin.kth
import csv
import requests
import io
import openpyxl
import warnings
import kthutils.credentials
import sys
import pathlib

cli = typer.Typer(name="forms", help="Access KTH Forms")

def get_added_forms(prefix: str = "") -> List[str]:
  """
  Returns a list of all the forms added to the configuration that are prefixed 
  by `prefix`. Default prefix is an empty string, which returns all forms.
  """
  forms = typerconf.get("forms").keys()
  return list(filter(lambda x: x.startswith(prefix), forms))
class FormsSession:
  """
  Maintains a session to the KTH Forms service.
  """

  BASE_URL = "https://www.kth.se/form/admin"

  def __init__(self, username: str, password: str):
    """
    Creates a new session to the KTH Forms service.

    `username` is the KTH username to use for logging in through 
    https://login.ug.kth.se. `password` is the password to use for logging in.
    """
    self.__session = weblogin.AutologinSession([
                          weblogin.kth.UGlogin(username, password,
                                               self.BASE_URL)
                        ])

  def get_data_by_url(self, url: str) -> Tuple[bytes, str]:
    """
    Gets the form at the given URL and returns it as (content, type) tuple. 
    Content is the raw data of the form, type is the content type of the form.
    """
    response = self.__session.get(url)
    if response.status_code != requests.codes.ok:
      raise ValueError(f"Failed to get form at {url}: {response.text}")

    return response.content, response.headers["Content-Type"]
  def get_csv_by_url(self, url: str) -> List[List[str]]:
    """
    Gets the form at the given URL and returns it as a list of lists.
    """
    data, content_type = self.get_data_by_url(url)

    if content_type == "text/csv":
      csvdata = csv.reader(data.decode("utf-8").splitlines())
    elif "excel" in content_type or "spreadsheet" in content_type:
      datafile = io.BytesIO(data)
      with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(datafile)
      sheet = wb.active
      fix_empty_cells = lambda x: list(map(lambda y: y if y is not None else "", x))
      csvdata = map(fix_empty_cells, sheet.iter_rows(values_only=True))
    else:
      raise ValueError(f"Form at {url} is not in CSV nor XLS(X) format")

    return list(csvdata)

class FormName(str):
  def __new__(cls, value):
    if "." in value:
      raise typer.BadParameter("Name cannot contain '.'")
    return super().__new__(cls, value)

form_name_arg = typer.Argument(help="Name of the form",
                               parser=FormName,
                               autocompletion=get_added_forms)
form_url_arg = typer.Argument(help="URL to the form. This can be any public "
                                   "URL that results in a CSV file. But it "
                                   "automatically logs in for KTH Forms.")
delimiter_arg = typer.Option(help="Delimiter to use for the CSV output")
@cli.command(name="add")
def cli_add_form(name: Annotated[FormName, form_name_arg],
                 url: Annotated[str, form_url_arg]):
  """
  Adds a form to the configuration
  """
  typerconf.set(f"forms.{name}", url)
@cli.command(name="export")
def cli_export_form(name: Annotated[FormName, form_name_arg],
                    delimiter: Annotated[str, delimiter_arg] = "\t",):
  """
  Prints data from a form to stdout in CSV format
  """
  url = typerconf.get(f"forms.{name}")
  forms = kthutils.forms.FormsSession(*kthutils.credentials.get_credentials())
  csvdata = forms.get_csv_by_url(url)
  csvout = csv.writer(sys.stdout, delimiter=delimiter)
  for row in csvdata:
    csvout.writerow(row)
@cli.command(name="next")
def cli_next_form(name: Annotated[FormName, form_name_arg],
                  delimiter: Annotated[str, delimiter_arg] = "\t",):
  """
  Prints new data from a form to stdout in CSV format
  """
  csvout = csv.writer(sys.stdout, delimiter=delimiter)
  url = typerconf.get(f"forms.{name}")
  forms = kthutils.forms.FormsSession(*kthutils.credentials.get_credentials())
  csvdata = forms.get_csv_by_url(url)
  data_dir = pathlib.Path(typerconf.dirs.user_data_dir)
  prev_csvdata = []
  prev_csvfile = data_dir / "next.csv"
  if prev_csvfile.exists():
    with prev_csvfile.open("r") as f:
      prev_csvdata = list(csv.reader(f))
  new_csvdata = csvdata.copy()
  csvdata = list(filter(lambda x: x not in prev_csvdata, new_csvdata))
  if not data_dir.exists():
    data_dir.mkdir(parents=True)
  with prev_csvfile.open("w") as f:
    csv.writer(f).writerows(new_csvdata)
  for row in csvdata:
    csvout.writerow(row)

def main():
  cli()

if __name__ == "__main__":
  main()
