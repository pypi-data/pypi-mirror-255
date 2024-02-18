from opendatagen.template import Template, TemplateManager, TemplateName, Variable
from opendatagen.data_generator import DataGenerator
from opendatagen.model import OpenAIChatModel, OpenAIInstructModel, OpenAIEmbeddingModel, ModelName, MistralChatModel
from mistralai.models.chat_completion import ChatMessage
from opendatagen.anonymizer import Anonymizer
from opendatagen.utils import function_to_call
import warnings
import json 
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pandas as pd
import os 



def anonymize_text(): 

    text_to_anonymize = """
            My name is Thomas, Call me at 0601010129 or email me at john.doe@example.com. 
            My SSN is 123-45-6789 and 4242 4242 8605 2607 is my credit card number. 
            Living in the best city in the world: Melbourne.
            New York & Co is a restaurant.
            It is 10 am.
            I have 10€ in my pocket. Oh my god.
            I have park my Tesla next to your house.
            My id is 0//1//2//2//2//2
    """
    
    completion_model = OpenAIChatModel(model_name="gpt-3.5-turbo-1106")

    anonymizer = Anonymizer(completion_model=completion_model)

    anonymized_text = anonymizer.anonymize(text=text_to_anonymize)
    
    print(anonymized_text)

def generate_data_from_predefined_template(template_file_path:str, template_name:str, output_path:str, output_decontaminated_path:str = None): 
    
    manager = TemplateManager(template_file_path=template_file_path)
    template = manager.get_template(template_name=template_name)

    if template:
     
        generator = DataGenerator(template=template)
        
        data, data_decontaminated = generator.generate_data(output_path=output_path, output_decontaminated_path=output_decontaminated_path)
        
        print(data)

    else: 

        print("The predefined template is badly formatted")


def check_question(result: dict):

    question = result["question"].value.lower().strip()

    if "given text" not in question and "mentioned" not in question and "text provided" not in question and "provided text" not in question and "according to the text" not in question:
        return True, "All is ok."
    else:
        return False, "The question must not contain 'given text' or 'mentioned text' and be self contained."

def test_question():

    return "What is the capital of France?"

if __name__ == "__main__":
    
    data = generate_data_from_predefined_template(template_file_path="opendatagen/template.json", 
                                           template_name="opendatagen", 
                                           output_path="opendatagen.csv",
                                           output_decontaminated_path="opendatagen_decontaminated.csv")
    
