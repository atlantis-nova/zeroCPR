from sklearn.neighbors import NearestNeighbors
import pandas as pd

class fn_main():

    def search_similar(self, query, k=1):
        df = self.df
        nbrs = NearestNeighbors(n_neighbors=k, metric='cosine').fit(df['text_vector_'].tolist())
        distances, indices = nbrs.kneighbors([self.model.encode(query)])
        indices_filtered = [x[1] for x in list(zip(distances[0][::-1], indices[0]))]
        if k == 1:
            return df.iloc[indices_filtered].index.tolist()[0], df.iloc[indices_filtered].raw.tolist()[0]
        else:
            return df.iloc[indices_filtered].raw.tolist()[0:k]
        
    
    def find_complementary_candidates(self, product_name, verbose=False):

        # uses a llm to extract complementary products
        selection = list()
        df_complementaries = self.list_complementary(product_name)

        for complementary in df_complementaries['complementary'].tolist():
            index, product_name_ = self.search_similar(complementary)
            selection.append([index, complementary, product_name_])

        df_selection = pd.DataFrame(selection)
        df_selection.columns = ['index', 'llm_product', 'product_name']
        df_selection = df_selection.drop_duplicates(subset='index').reset_index(drop=True)

        return df_selection


    def filter_complementary_candidates(self, df_candidates, product_name, verbose=False):
        
        # uses a llm to check values
        complementary_list = df_candidates[['index', 'product_name']].values.tolist()
        df_filtered = self.check_complementary(product_name=product_name, complementary_list=complementary_list)

        df_filtered['llm_product'] = df_candidates['llm_product']
        df_filtered = df_filtered[['index', 'product_name', 'llm_product', 'recommended_product', 'reasoning', 'score']]
        return df_filtered


    def find_product_complementaries(self, product_names, max_retries=5):

        # perform the entire complimentary discovery pipeline
        if len(product_names) == 1:

            # for a single product we run a simplified pipeline
            product_name = product_names[0]
            df_candidates = self.find_complementary_candidates(product_names)
            df_filtered = self.filter_complementary_candidates(df_candidates=df_candidates, product_name=product_name)

            return df_candidates, df_filtered
        
        elif len(product_names) > 1:

            # for multiple products we run a dedicated, more complex pipeline
            df_list = list()
            for product_name in product_names:
                print('**', product_name)
                
                consecutive_err = 0
                while True:
                    try:
                        # we pass in a product name at a time
                        df_candidates, df_filtered = self.find_product_complementaries([product_name])
                        df_list.append(df_filtered)
                        # when search is successful, break the current iteration
                        break
                    except:
                        print('ERR')
                        consecutive_err += 1
                        if consecutive_err == max_retries:
                            # maximum consecutive errors before exiting the iteration
                            break
            
            df_complementaries = pd.concat(df_list)
            return df_complementaries