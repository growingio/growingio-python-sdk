# -*- coding: utf-8 -*-

from sdk import *
reload(sys) 
sys.setdefaultencoding('utf8')

def __main__():
    gio = GrowingIO(ai="0a1b4118dd954ec3bcc69da5138bdb96", client_id="7f8it37dxdt91x4n5cvuvccc1cgaqe22", is_debug = True)
    user_id = 526 
    gr_user_id = "7328beea-ee89-43a0-86cb-48879e90a67d" 
    session_id = "bb9aa471-3bc9-455b-b3a1-eeb9e0e9a0e3" 

    properties = {
        "u" : gr_user_id,
        "s" : session_id,
        "time" : datetime.datetime.now(),
        "account_id": "0a1b4118dd954ec3bcc69da5138bdb96",
        "chart_dimension_count": 12,
        "chart_id": 9999,
        "chart_metric_count": 1,
        "chart_name": "python sdk test",
        "chart_type": "line"
    }

    gio.track(user_id, "create_chart", properties)

__main__()