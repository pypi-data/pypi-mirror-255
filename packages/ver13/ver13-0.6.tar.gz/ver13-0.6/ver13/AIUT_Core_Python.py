import os
import subprocess
from openai import AzureOpenAI
from configparser import ConfigParser

MODEL_TEMP = 0.7
MAX_TOKENS = 1000

class utils():
    def __init__(self):
        pass

    def cient(self, client):
        self.__client = client

    def client(self):
        return self.__client

    def api_end_point(self, api_end_point):
        self.__api_end_point = api_end_point

    def api_end_point(self):
        return self.__api_end_point

    def api_key(self, api_key):
        self.__api_key = api_key

    def api_key(self):
        return self.__api_key

    def api_version(self, api_version):
        self.__api_version = api_version

    def api_version(self):
        return self.__api_version

    def model_deployment_name(self, model_deployment_name):
        self.__model_deployment_name = model_deployment_name

    def model_deployment_name(self):
        return self.__model_deployment_name

    def src_files_location(self, src_files_location):
        self.__src_files_location = src_files_location

    def src_files_location(self):
        return self.__src_files_location

    def dest_test_files_location(self, dest_test_files_location):
        self.__dest_test_files_location = dest_test_files_location

    def dest_test_files_location(self):
        return self.__dest_test_files_location

    def code_base_location(self, code_base_location):
        self.__code_base_location = code_base_location

    def code_base_location(self):
        return self.__code_base_location

    def unit_test_framework(self, unit_test_framework):
        self.__unit_test_framework = unit_test_framework

    def unit_test_framework(self):
        return self.__unit_test_framework

    def read_config(self):
        try:
            configur = ConfigParser()
            configur.read('UT_Settings.ini')
            self.api_end_point = configur.get('default','azure_endpoint')
            self.api_key = configur.get('default','api_key')
            self.api_version = configur.get('default','api_version')
            self.model_deployment_name = configur.get('default','model_deployment_name')
            #self.src_files_location = configur.get('default','src_files_location')
            #self.dest_test_files_location = configur.get('default','dest_test_files_location')
            #self.code_base_location = configur.get('default','code_base_location')
            
            self.src_files_location = "C:\\Users\\Administrator\\Downloads\\Java Unit Test Cases POC\\TCGen-main\\TCGen-main\\CSharp\\src"
            self.dest_test_files_location = "C:\\Users\\Administrator\\Downloads\\Java Unit Test Cases POC\\TCGen-main\\TCGen-main\\CSharp\\test"
            self.code_base_location = "C:\\Users\\Administrator\\Downloads\\Java Unit Test Cases POC\\TCGen-main\\TCGen-main\\CSharp\\"
                       
            
            #self.unit_test_framework = configur.get('default','unit_test_framework')
            self.unit_test_framework = "unittest"

            if self.src_files_location[-1] != '\\':
                self.src_files_location += '\\'

            if self.dest_test_files_location[-1] != '\\':
                self.dest_test_files_location += '\\'

            if self.code_base_location[-1] != '\\':
                self.code_base_location += '\\'

            return True
        except Exception as err:
            print(err)
            return False

    def create_azure_connection(self):
        try:
            if (self.read_config()):
                self.client = AzureOpenAI(
                    azure_endpoint=self.api_end_point,
                    api_key=self.api_key,
                    api_version=self.api_version)
                return self.client
            else:
                return False
        except Exception as err:
            print(err)
            return False

def gen_no_of_tc(class_to_test, unit_test_framework):
    try:
        global NO_OF_TC
        global NO_OF_LARGE_TC
        count = 1
        for letter in class_to_test:

            if unit_test_framework.lower()=="unittest":
                if letter == ':' or letter == ")":
                    count += 1

        NO_OF_TC = count // 10

        if count > 100:
            NO_OF_TC = count // 10
        else:
            NO_OF_TC = 10

        if count > 100:
            NO_OF_LARGE_TC = count // 100
        else:
            NO_OF_LARGE_TC = 1

        return True
    except Exception as err:
        print(err)
        return  False

def gen_prompt(class_to_test,unit_test_framework):
    try:
        global execute_messages
        execute_system_message = {}
        execute_user_message = {}
        unit_test_framework_temp = "MSTest"
        if unit_test_framework.lower()=="unittest":
            execute_system_message = {
                "role": "system",
                "content":
                    "You are a world-class developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with the lanugage of the function, code, you write all of your code in a single block.",
            }
            
            #Since you're using `{unit_test_framework_temp}`, Use assertEquals to compare expected result, so inclue using unittest.Framework; to #compare the answers. Make sure there are no syntax errors in the generated code. Feel free to import any other packages that are used. 
            execute_user_message = {
                "role": "user",
                "content":
                    f"""
                ```python
              {class_to_test}
              ```
              A good unit test suite should aim to:
              - Test the function's behavior for a wide range of possible inputs
              - Test edge cases that the author may not have foreseen
              - Take advantage of the features of `{unit_test_framework_temp}` to make the tests easy to write and maintain
              - Be easy to read and understand, with clean code and descriptive names
              - Be deterministic, so that the tests always pass or fail in the same way.
              Using the required framework for that language, mentioning the framework used, write a suite of unit tests for the function, following the cases above. Also create an object of all the classes while generating test cases. Use <classname>.<function_name> before calling the function everytime. If there's any class being created in the given program, include it in the generated program also and make sure to create an object of it in the test cases program as well. 
              All the using statements from the provided source to be added also in the generated program.
              Include helpful comments to explain each line. Reply only with code.
              Since you're using `{unit_test_framework_temp}`, Use Asserts to compare expected result, so inclue 1)from unittest import TestCase 2) from io import StringIO 3) from unittest.mock import patch or both to compare the answers. Make sure there are no syntax errors in the generated code. Feel free to import any other packages that are used. 
              Ensure 100% Code Coverage, so include all unexpected edge cases also.
              Also create the caes to cover the exceptions block added in provided code.
              Make sure there are no missed branches or lines while generating test cases. Ensure 100% cyclomatic complexity. Have atleast {NO_OF_TC} test cases + unexpected edge cases and atleast {NO_OF_LARGE_TC} large test case. 
              """,
            }
            execute_messages = [execute_system_message, execute_user_message]
            return True
    except Exception as err:
        print(err)
        return False

def read_src_file(objUtils, file):
    try:
        objFile = open(file, "r+")
        class_to_test = objFile.read()
        print(class_to_test)
        if (gen_no_of_tc(class_to_test, objUtils.unit_test_framework)):
            if(gen_prompt(class_to_test, objUtils.unit_test_framework)):
                return True
            else:
                return  False
        else:
            return False
    except Exception as err:
        print(err)
        return False

def create_testcase_file(objUtils, response):
    try:
        code_in_response = ""
        testcase_file_name = ""
        for chunk in response.choices[0].message.content:
            code_in_response += chunk
            print(code_in_response)
        if objUtils.unit_test_framework.lower() == "unittest":
            generated_code = code_in_response.split("```python")[1].split("```")[0].strip()
            classs = ""
            words = generated_code.split(" ")
            x = words.index("class")
            classs = words[x + 1]
            location = objUtils.dest_test_files_location
            testcase_file_name = classs.strip() + ".py"
            location = location + testcase_file_name
            f = open(location, "w+")
            f.write(generated_code)
            f.close()
        return location, testcase_file_name
    except Exception as err:
        print(err)
        return False

def execute_test_cases(objUtils):
    try:
        if objUtils.unit_test_framework.lower() == "unittest":
            command = "ant"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=objUtils.code_base_location)
            if result.returncode == 0:
                print("Command executed successfully.")
                print("Output:")
                print(result.stdout)
            else:
                print("Command execution failed.")
                print("Error:")
                print(result.stderr)
            # Open the HTML file in the default web browser
            subprocess.run("start index.html", shell=True, text=True, cwd=objUtils.code_base_location+ "report\\jacoco\\")
            return True
    except Exception as err:
        print(err)
        return False

def generate_unit_cases(file_path):
    try:
        objUtils = utils()
        if objUtils.create_azure_connection():
            read_src_file(objUtils,file_path)
            response = objUtils.client.chat.completions.create(
               model=objUtils.model_deployment_name,  # model = "deployment_name".
               messages=execute_messages,
               temperature=MODEL_TEMP,
               max_tokens=MAX_TOKENS
            )
            testcase_file_name = create_testcase_file(objUtils, response)
            print(f"Metrics:"
                  f"Generated Test Case File {testcase_file_name[1]}, "
                  f"Token sent in Prompt as request {response.usage.prompt_tokens}, "
                  f"Token received as response {response.usage.completion_tokens}, "
                  f"Total Tokens processed {response.usage.total_tokens}")
            metrics = f"Metrics:"\
                      f"Generated Test Case File {testcase_file_name[1]}," \
                      f"Token sent in Prompt as request {response.usage.prompt_tokens}," \
                      f"Token received as response {response.usage.completion_tokens}, "\
                      f"Total Tokens processed {response.usage.total_tokens}"
            #execute_test_cases(objUtils)
            return testcase_file_name, objUtils, metrics
    except Exception as err:
        print(err)
        return False