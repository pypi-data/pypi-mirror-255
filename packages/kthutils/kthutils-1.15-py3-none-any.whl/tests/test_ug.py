import kthutils.ug
import os

ug = kthutils.ug.UGsession(os.environ["KTH_LOGIN"], os.environ["KTH_PASSWD"])

def test_list_editable_groups():
  groups = ug.list_editable_groups()
  assert groups
def test_find_user_by_username():
  data = ug.find_user_by_username("dbosk")
  assert data[0]["username"] == "dbosk"
  assert data[0]["givenName"] == "Daniel"
  data = ug.find_user_by_username("alba")
  assert data[0]["username"] == "alba"
  assert data[0]["givenName"] == "Alexander"
def test_add_group_members():
  group = ug.add_group_members(["u13aecix"], "u2i9xt3r")
  assert "u13aecix" in group["members"]

def test_remove_group_members():
  group = ug.remove_group_members(["u13aecix"], "u2i9xt3r")
  assert "u13aecix" not in group["members"]
