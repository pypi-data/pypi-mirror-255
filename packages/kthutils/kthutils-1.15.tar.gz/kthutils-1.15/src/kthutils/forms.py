import typer
from typing import Annotated, Any, List, Tuple, Dict

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
from enum import Enum
import re
CONFIG_ADDED_FORMS = "forms.added_forms"
CONFIG_REWRITERS = "forms.rewriter"

cli = typer.Typer(name="forms", help="Access KTH Forms")

def get_added_forms(prefix: str = "") -> List[str]:
  """
  Returns a list of all the forms added to the configuration that are prefixed 
  by `prefix`. Default prefix is an empty string, which returns all forms.
  """
  forms = typerconf.get(CONFIG_ADDED_FORMS).keys()
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
    csvdata = map(clean_row, csvdata)

    return list(csvdata)
def clean_row(row: List[str]) -> List[str]:
  """
  Cleans a row of form data by replacing ell newline characters by spaces.
  """
  return map(lambda x: x.replace("\n", " "), row)
def export(name: str) -> List[List[str]]:
  """
  Returns data from a form in CSV format (lists of lists)
  """
  url = typerconf.get(f"{CONFIG_ADDED_FORMS}.{name}")
  forms = kthutils.forms.FormsSession(*kthutils.credentials.get_credentials())
  return forms.get_csv_by_url(url)
def next(name: str) -> List[List[str]]:
  """
  Returns new data (since last run) from a form in CSV format (lists of lists)
  """
  data_dir = pathlib.Path(typerconf.dirs.user_data_dir)
  prev_csvdata = []
  prev_csvfile = data_dir / "next.csv"
  if prev_csvfile.exists():
    with prev_csvfile.open("r") as f:
      prev_csvdata = list(csv.reader(f))
  new_csvdata = export(name)
  csvdata = list(filter(lambda x: x not in prev_csvdata, new_csvdata))
  if not data_dir.exists():
    data_dir.mkdir(parents=True)
  with prev_csvfile.open("w") as f:
    csv.writer(f).writerows(new_csvdata)
  return csvdata
def get_added_rewriters(prefix: str = "") -> List[str]:
  """
  Returns a list of all the rewriters added to the configuration that are 
  prefixed by `prefix`. Default prefix is an empty string, which returns all 
  rewriters.
  """
  rewriters = typerconf.get(CONFIG_REWRITERS).keys()
  return list(filter(lambda x: x.startswith(prefix), rewriters))
def rewrite_row(row: List[str], rewriter: Dict[str, Any]) -> str:
  """
  Rewrites a row of form data using the rewriter and returns it as a string.
  """
  format_string = rewriter["format_string"]
  substitutions = {}
  for variable, var_subst in rewriter["substitutions"].items():
    if "column" in var_subst:
      column = var_subst["column"]
      if ":" in column:
        if column.count(":") == 2:
          try:
            start, end, step = map(int, column.split(":"))
          except ValueError as err:
            raise ValueError(f"{variable}.column = {column} is not a valid slice: {err}")
          s = slice(start, end, step)
        elif column.count(":") == 1:
          try:
            start, end = map(int, column.split(":"))
          except ValueError as err:
            raise ValueError(f"{variable}.column = {column} is not a valid slice: {err}")
          s = slice(start, end)
        else:
          raise ValueError(f"{variable}.column = {column} has too many colons.")
        data = "\t".join(row[s])
      else:
        try:
          data = row[int(column)]
        except IndexError:
          raise ValueError(f"{variable}.column = {column} is "
                           f"out of range, row has {len(row)} columns: {row}.")
        except ValueError as err:
          raise ValueError(f"{variable}.column = {column} is not an int: {err}")
    else:
      data = "\t".join(row)

    try:
      if not isinstance(var_subst["regex"], list):
        regexes = [var_subst["regex"]]
      else:
        regexes = var_subst["regex"]
    except KeyError:
      substitutions[variable] = data
      continue

    regex_results = []
    for regex in regexes:
      if regex[0] != "s" and regex[-1] != regex[1]:
        raise ValueError(f"{variable}.regex has invalid content: '{regex}', "
                          f"must be of form 's/regex/replacement/'")
      regex = regex.split(regex[1])
      pattern = regex[1]
      replacement = regex[2]
      value = re.sub(pattern, replacement, data)
      if value != data:
        regex_results.append(value)

    num_results = len(regex_results)
    if num_results == 1:
      substitutions[variable] = regex_results[0]
    elif num_results < 1:
      if "no_match_default" in var_subst:
        substitutions[variable] = var_subst["no_match_default"]
      else:
        substitutions[variable] = data
    else:
      substitutions[variable] = f"({'|'.join(regex_results)})"
  return format_string.format(**substitutions)

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
rewriter_arg = typer.Argument(help="Name of the rewriter",
                              parser=FormName,
                              autocompletion=get_added_rewriters)
opt_form_name_arg = typer.Argument(help="Name of the form, if not provided, "
                                        "read from data from stdin",
                                   parser=FormName,
                                   autocompletion=get_added_forms)
class Source(str, Enum):
  export = "export"
  next = "next"

source_opt = typer.Option(help="Source of the form data, either "
                               "the export or next command.",
                          case_sensitive=False)
@cli.command(name="add")
def cli_add_form(name: Annotated[FormName, form_name_arg],
                 url: Annotated[str, form_url_arg]):
  """
  Adds a form to the configuration
  """
  typerconf.set(f"{CONFIG_ADDED_FORMS}.{name}", url)
@cli.command(name="export")
def cli_export_form(name: Annotated[FormName, form_name_arg],
                    delimiter: Annotated[str, delimiter_arg] = "\t",):
  """
  Prints data from a form to stdout in CSV format
  """
  csvout = csv.writer(sys.stdout, delimiter=delimiter)
  csvdata = export(name)
  for row in csvdata:
    csvout.writerow(row)
@cli.command(name="next")
def cli_next_form(name: Annotated[FormName, form_name_arg],
                  delimiter: Annotated[str, delimiter_arg] = "\t",):
  """
  Prints new data from a form to stdout in CSV format
  """
  csvout = csv.writer(sys.stdout, delimiter=delimiter)
  csvdata = next(name)
  for row in csvdata:
    csvout.writerow(row)
rewriter = typer.Typer(name="rewriter", help="Rewriter for form data")
cli.add_typer(rewriter)
@rewriter.command(name="rewrite")
def rewriter_rewrite_form(rewriter: Annotated[FormName, rewriter_arg],
                          form: Annotated[FormName, opt_form_name_arg] = None,
                          source: Annotated[Source, source_opt] = "next",
                          delimiter: Annotated[str, delimiter_arg] = "\t",):
  """
  Rewrites data from a form and prints it to stdout
  Rewrites data from a form using a rewriter and prints it to stdout in a more 
  structured format
  """
  if form is None:
    csvdata = list(csv.reader(sys.stdin, delimiter=delimiter))
  elif source == Source.export:
    csvdata = export(form)
  elif source == Source.next:
    csvdata = next(form)
  else:
    raise typer.BadParameter(f"Unknown source: {source}")
  rewriter = typerconf.get(f"{CONFIG_REWRITERS}.{rewriter}")
  for row in csvdata:
    print(rewrite_row(row, rewriter))

def main():
  cli()

if __name__ == "__main__":
  main()
