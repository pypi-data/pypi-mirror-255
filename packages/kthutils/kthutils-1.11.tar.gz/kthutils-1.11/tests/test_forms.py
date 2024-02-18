import pytest
import kthutils.forms
import kthutils.credentials
import os

forms = kthutils.forms.FormsSession(*kthutils.credentials.get_credentials())

def test_get_data_by_url():
  data, content_type = forms.get_data_by_url(
      "https://www.kth.se/form/admin/api/webform/64ec8baa917ea4c31c33267e/answer/export")
  assert content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  assert data.startswith(b"PK")
def test_get_csv_by_url():
  csvdata = forms.get_csv_by_url(
      "https://www.kth.se/form/admin/api/webform/64ec8baa917ea4c31c33267e/answer/export")
  assert "Svarsdatum" in csvdata[0] and "Kurs" in csvdata[0]
