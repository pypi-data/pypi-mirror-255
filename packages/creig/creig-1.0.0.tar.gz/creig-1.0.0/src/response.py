from libs.common import json_open, path

resp = json_open(path("response.json"))

eng = input("英文:")

eng_word = eng + ": Word"
eng_trans = eng + ": Translation"

for key, value in resp.items():
    if key == eng_word or key == eng_trans:
        print("[" + value["tag"] + "]\n" + value["response"])