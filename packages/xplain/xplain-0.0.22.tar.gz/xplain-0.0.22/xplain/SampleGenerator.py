import json

import xplain
import argparse

parser = argparse.ArgumentParser()


parser.add_argument('--startup', help='startup configuration')

parser.add_argument('--samplerate', help='samplerate')

args = parser.parse_args()

startup_json_content = json.load(args.startup)

def sampling_object(json_obj):
    if "tableFileName" in json_obj:
        xtable_2_sample = json_obj.get("tableFileName")
        print(xtable_2_sample)


sampling_object(startup_json_content)





