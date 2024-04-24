from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from typing import Dict, List
import os


class ChatGroqUty:
    '''
    This class is used to get response from Groq API
    '''
    def __init__(self) -> None:
        # Initialize API KEY
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    def load_model(self):
        "Load the model from the Langchain-Groq"
        self.chat = ChatGroq(temperature=0,
                             groq_api_key=self.GROQ_API_KEY, 
                             model_name="llama3-8b-8192")

    def get_prompt(self, product_title: List[str],category: List[str]):
        "Build the prompt template"

        system = "You are a vietnamese language expert"
        human = f"""Given a list of product title {product_title}
                
                Your first task is group the vietnamese product titles above to correct category in list of categories {category}.
                If you CAN NOT group the product title to correct category, then create a new category for that product.
                
                The second task is FINDING or CREATING the main product which is inside of the title.

                After completing two tasks, you MUST provide me back the result in the list of json of each product

                [
                    'product_title': '<product_title>',
                    'category': '<category>',
                    'sub-category': '<sub-category>',
                ]

                Example:
                The list of product is ["Hạt mix dinh dưỡng Ganyuan thơm ngon béo ngậy,ngũ cốc sấy khô", 
                                        "Trái cây sấy khô Kam Yuen (gói ~30g)"]
                the list of category is ["Hạt", "Trái cây sấy khô"]
                
                the response MUST BE:
                [
                    product_title: "Hạt mix dinh dưỡng Ganyuan thơm ngon béo ngậy,ngũ cốc sấy khô",
                    category: "Hạt",
                    sub-category: "Hạt  mix dinh dưỡng",
                ],
                [
                    product_title: "Xoài cây sấy khô Kam Yuen (gói ~30g)",
                    category: "Trái cây sấy khô",
                    sub-category: "Xoài sấy khô",
                ]

                Your third task is TRANSLATING the final response to English.

                DO NOT TELL ANYTHING ELSE, JUST KEEP THE RESPONSE IN THE FORMAT ABOVE

                """
        self.prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    def get_response(self, product_title: List[str],category: List[str]) -> List[Dict]:
        "Get the response from Groq API"
        self.load_model()
        self.get_prompt(product_title=product_title, category=category)
        self.chain = self.prompt | self.chat
        self.result = self.chain.invoke({"product_title": product_title,
                               "category": category,
                               })
        return self.result
    

