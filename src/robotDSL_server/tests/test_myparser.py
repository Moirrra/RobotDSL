import pytest
from RSL_pkg import myparser

datapath = "./data/filename.txt"
data = []
with open(datapath, 'r', encoding='utf8') as fp:
    for line in fp:
        line = line.rstrip()
        data.append(line)

@pytest.mark.parametrize(
    "file_name",
    data,
    ids=["case" + "{}".format(i) for i in range(1,len(data)+1)]
)
def test_init(file_name):
    p = myparser.Parser(file_name)

def test_run(file_name):
    p1 = myparser.Parser(file_name)
    assert p1.run()


if __name__ == '__main__':
    pytest.main(["-s", "test_myparser.py"])