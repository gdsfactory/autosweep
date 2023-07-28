import logging

from ta.base.io import write_json, read_json


data = {'hello': {'1': 'a', 'b': 2}, 'world': '123'}
filename = 'temp.json'

write_json(data=data, path=filename)
data_in = read_json(path=filename)

assert data == data_in, "The data written should be the data read back"
logging.info("Passed")