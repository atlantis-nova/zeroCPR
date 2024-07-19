import ast
import pandas as pd

class fn_prompts():

    def list_complementary(self, product_name):

        prompt = \
        f"""
        a customer is doing shopping and buys the following product
        product_name: {product_name}

        Make a list of SPECIFIC products that the customer WILL NEED TO add to the same shopping list
        # Ex. when a person buys a toothpaste, needs a toothbrush
        Remember, I am searching for **complementaries**, similar products are not useful to me

        You can make a long list (even 20), as long as they are complementary:
        Output a **parsable python list** using python, no comments or extra text, in the following format:
        [
            [<product_name>, <reasoning behind the choice>, <complementary product 1>],
            [<product_name>, <reasoning behind the choice>, <complementary product 2>],
            [<product_name>, <reasoning behind the choice>, <complementary product 3>],
            ...
        ]
        Take it easy, take a big breath to relax and be accurate. **Output must start with [, end with ]**, no extra text or comments
        # for example, avoid using "Here is the output:" or anything similar
        """
        
        # parse
        output = self.query_llm(prompt)
        output = ast.literal_eval(output)

        # recreate df
        df_complementaries = pd.DataFrame(output)
        df_complementaries.columns = ['product_name', 'reasoning', 'complementary']

        return df_complementaries
    

    def check_complementary(self, product_name, complementary_list):

        prompt = \
        f"""
        a customer is doing shopping and buys the following product
        product_name: {product_name}

        A shopping junior recommend the following products to be bought together, however he still has to learn:
        given the following possible_complementaries list:

        # format [possible_complementary_id, possible_complementary]
        possible_complementaries: {complementary_list}

        Output a parsable python list using python, no comments or extra text, in the following format:
        [
            [<product_name>, <possible_complementary_id>, <possible_complementary>, <reason why it is complementary or not>, <0 or 1>],
            [<product_name>, <possible_complementary_id>, <possible_complementary>, <reason why it is complementary or not>, <0 or 1>],
            [<product_name>, <possible_complementary_id>, <possible_complementary>, <reason why it is complementary or not>, <0 or 1>],
            ...
        ]
        the customer is only interested in **products that can be paired with the existing one** to enrich his experience, not substitutes
        THE ORDER OF THE OUTPUT MUST EQUAL THE ORDER OF ELEMENTS IN  complementary_list

        Take it easy, take a big breath to relax and be accurate. **Output must start with [, end with ]**, no extra text or comments
        # for example, avoid using "Here is the output:" or anything similar
        """
        
        output = self.query_llm(prompt)

        # parse
        list1 = ast.literal_eval(output)

        # recreate df
        complete_list = [[x[0], x[1], x[2], x[3], x[4]] for x in list1]
        df_filtered = pd.DataFrame(complete_list)
        df_filtered.columns = ['product_name', 'index', 'recommended_product', 'reasoning', 'score']

        return df_filtered
