from operator import index
from tkinter.tix import Tree
import yaml
import json
from cerberus import Validator
import re
import os

os.chdir("..")
root_path = os.getcwd()

def get_rule_file():
    path = root_path + "/log_alerts/rules"
    l_files = os.listdir(path)

    for file in l_files:
        if(file[0]!='.'):
            return file;

def find_line_number(filename, string_to_search):
    with open(filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if string_to_search in line:
                return num

def load_doc():
    with open(root_path + '/log_alerts/rules/temp/temp_rule_file.yaml', 'r') as stream:
        try:
            return yaml.load(stream,Loader=yaml.Loader)
        except yaml.YAMLError as exception:
            raise exception

def delete_temp_files():
    temp_rule_file = root_path + '/log_alerts/rules/temp/temp_rule_file.yaml'
    os.remove(temp_rule_file)

rules_error = [];
def validate_rule(schema,key,value,line_number):

    temp_rule_file = root_path + '/log_alerts/rules/temp/temp_rule_file.yaml'

    with open(temp_rule_file, 'w') as file:
        documents = yaml.dump(value, file)

    v = Validator(schema)
    doc = load_doc()

    if(re.match(r'\w*[A-Z\s]\w*', key)):
        rules_error.append(f"Rulee name should be smaller case only and should not contain spaces, Error in '{key}', on or after Line Number :: {line_number}")
    if (value["index"][-1])!="*":
        rules_error.append(f"Index name must be end with * , Error in '{key}', on or after Line Number :: {line_number}")
    if v.validate(doc, schema) == False:
        rules_error.append(f"Error in '{key}', on or after Line Number :: {line_number}")
        rules_error.append(v.errors)


freqency_schema_file = "validate_log_alerts/schema/haystack_freqency_rule_schema.json";
freqency_schema = eval(open(freqency_schema_file, 'r').read())

anyrule_schema_file = "validate_log_alerts/schema/haystack_any_rule_schema.json";
anyrule_schema = eval(open(anyrule_schema_file, 'r').read())

flatline_schema_file = "validate_log_alerts/schema/haystack_flatline_rule_schema.json";
flatline_schema = eval(open(flatline_schema_file, 'r').read())

rule_file = get_rule_file()

with open(root_path + '/log_alerts/rules/'+rule_file, 'r') as file:
    configuration = yaml.safe_load(file)

with open('config.json', 'w') as json_file:
    json.dump(configuration, json_file)
    
output = json.dumps(json.load(open('config.json')), indent=2)
rules_obj = json.loads(output)



for key, value in rules_obj["alert_params"].items():

    line_number = find_line_number(root_path + '/log_alerts/rules/'+rule_file,key)

    if((value["type"])=="frequency"):
        validate_rule(freqency_schema,key,value,line_number)

    elif((value["type"])=="any"):
        validate_rule(anyrule_schema,key,value,line_number)

    elif((value["type"])=="flatline"):
        validate_rule(flatline_schema,key,value,line_number)

delete_temp_files()
if len(rules_error) >=1:
    print(False)
    raise Exception(rules_error)
else:
    print(True)