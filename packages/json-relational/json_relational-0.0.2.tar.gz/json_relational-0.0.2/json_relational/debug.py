from src.main import JsonRelational
import json


jr = JsonRelational(pin_root=True)

json_data = [
    {"confirm_ack": {"ca": {"k21": "v21_1"}, "k12": "v12_1"}},
    {"confirm_req": {"qr": {"k21": "v21_2"}, "k12": "v12_2"}},
    {"as_pull":     {"ap": {"k21": "v21_2"}, "k12": "v12_2"}}
]


actual_result = jr.flatten_json(json_data)
print(json.dumps(actual_result, indent=4))
