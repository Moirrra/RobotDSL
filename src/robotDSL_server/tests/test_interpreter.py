import pytest
from RSL_pkg import interpreter
from RSL_pkg import myparser

p = myparser.Parser("..\\script\\bank_robot.txt")

@pytest.mark.parametrize(
    "parser,user_id,script_name",
    [(p,"1","bank_robot"),
     (p,"12","online_shop_robot"),
     (p,"3","tele_robot"),
     (p,"40","robot"),
     (p,"sa","tele"),
     (p,"2ef3","tele_robot"),
     (p,"a","tele_robot"),
     (p,"7","tele_robot")],
    ids=["case" + "{}".format(i) for i in range(1,9)]
)
def test_init(parser, user_id, script_name):
    assert interpreter.Interpreter(parser,user_id,script_name)

if __name__ == '__main__':
    pytest.main(["-s", "test_interpreter.py"])