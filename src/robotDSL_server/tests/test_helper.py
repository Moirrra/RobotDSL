import pytest
from RSL_pkg.helper import Helper


datapath = "./data/id_script.txt"
data = []
with open(datapath, 'r', encoding='utf8') as fp:
    for line in fp:
        line = line.rstrip()
        newline = tuple(line.split())
        data.append(newline)


@pytest.mark.parametrize(
    "user_id,script_name",
    data,
    ids=["case" + "{}".format(i) for i in range(1,len(data)+1)]
)
def test_init(user_id, script_name):
    assert Helper(user_id,script_name)


@pytest.mark.parametrize(
    "user_id,script_name",
    data,
    ids=["case" + "{}".format(i) for i in range(1,len(data)+1)]
)
def test_get_value(user_id, script_name):
    h = Helper(user_id, script_name)
    val1 = h.get_value("name")
    val2 = h.get_value("nam")
    assert val1 is not None, "查找到结果:%s" % val1
    assert val2 is None, "查找到结果:%s" % val2


if __name__ == '__main__':
    pytest.main(["-s", "test_helper.py"])