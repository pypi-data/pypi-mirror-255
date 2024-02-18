from kthutils.participants import *
import os

ps = ParticipantsSession(os.environ["KTH_LOGIN"],
                         os.environ["KTH_PASSWD"])

def test_get_all_data():
  data = ps.get_all_data("DD1310", "HT2023")
  assert "totalNumberOfParticipants" in data
  assert "courseRounds" in data
  assert "participants" in data
  assert "funkaCountersCombinations" in data
  assert "funkaFlag" in data
  assert "ugdata" in data
  assert "numberOfCourseRoundChanged" in data
def test_participants_data():
  data = ps.get_all_data("DD1310", "HT2023")
  assert "participants" in data
  participant = data["participants"][0]
  assert "courseRound" in participant
  assert "courseRoundsCode" in participant
  assert "personnumer" in participant
  assert "firstName" in participant
  assert "lastName" in participant
  assert "email" in participant
  assert "programCode" in participant
  assert "funkaCode" in participant
