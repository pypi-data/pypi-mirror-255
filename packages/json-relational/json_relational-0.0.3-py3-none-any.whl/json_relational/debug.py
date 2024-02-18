from src.main import JsonRelational
import json


jr = JsonRelational(pin_root=False)

json_data = [
    {"confirm_ack": {"ca": {"k21": "v21_1"}, "k12": "v12_1"}},
    {"confirm_req": {"qr": {"k21": "v21_2"}, "k12": "v12_2"}},
    {"as_pull":     {"ap": {"k21": "v21_2"}, "k12": "v12_2"}}
]


json_data = [
    {"log1": "time1", "message": {"vote": {"hashes": ["v1", "v2"]}}},
    {"log2": "time2", "message": {"vote": {"hashes": ["v1", "v2"]}}}
]


actual_result = jr.flatten_json(json_data)
print(json.dumps(actual_result, indent=4))
