import json
from json import JSONEncoder
import base64 
from datetime import date, datetime,time, timedelta,timezone

# e.g.
# d = datetime(2021, 1, 1, 0, 0, 0, 0, timezone(timedelta(hours=4)))
# print(dumps(d))

class ClassJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date , time)):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.total_seconds()
        if isinstance(o, (bytes, bytearray)):
            # user base64 encode bytes
            return base64.b64encode(o).decode()
        if isinstance(o, (set, frozenset)):
            return list(o)
        if hasattr(o, '__dict__'):
            return { k:o.__dict__[k] for k in o.__dict__ if not k.startswith('_')}
        return json.loads(json.dumps(o ,default=str))
    

def dumps(obj,cls=ClassJSONEncoder , ensure_ascii=False, **kwargs):
    return json.dumps(obj, cls=cls , ensure_ascii=ensure_ascii , **kwargs)
