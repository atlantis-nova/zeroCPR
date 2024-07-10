import pandas as pd
from tqdm import tqdm
tqdm.pandas()

class fn_encoding():
    
    def encode_products(self, product_list):

        #load/create df
        df = pd.DataFrame(product_list)
        df.columns = ['raw']

        #encode df version: for small dataset only
        # ***TO AVOID NaN ERRORS, always use dropna(subset=...)
        df['text_vector_'] = df['raw'].progress_apply(lambda x : self.model.encode(x).tolist())
        self.df = df
        self.product_list = product_list

        return df
    

    def upload_encoded_products(self, df_encoded):

        self.df = df_encoded
        self.product_list = df_encoded['raw'].tolist()