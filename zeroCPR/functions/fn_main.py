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
        output = self.list_complementary(product_name)
        for k in output:
            index, product_name_ = self.search_similar(k[0])
            selection.append([index, k[1], k[0]])
        df_ = pd.DataFrame([[x[0], x[2], self.product_list[x[0]], x[1]] for x in selection])
        df_.columns = ['index', 'llm_product', 'product_name', 'score']
        df_ = df_.drop_duplicates(subset='product_name').reset_index(drop=True)
        df_ = df_[df_['index']!=0]
        return df_


    def filter_complementary_candidates(self, df_candidates, product_name, verbose=False):
        
        # uses a llm to check values
        complementary_list = df_candidates['product_name'].tolist()
        complete_list = self.check_complementary(product_name=product_name, complementary_list=complementary_list, verbose=verbose)
        df_filtered = pd.DataFrame(complete_list)
        df_filtered.columns = ['product_name', 'recommended_product', 'reasoning', 'score']
        df_filtered['llm_product'] = df_candidates['llm_product']
        df_filtered['index'] = df_candidates['index']
        df_filtered['similarity_score'] = df_candidates['score']
        df_filtered = df_filtered[['index', 'product_name', 'llm_product', 'recommended_product', 'reasoning', 'similarity_score', 'score']]
        return df_filtered
    

    def filter_complementary_candidates(self, df_candidates, product_name, verbose=False):
        
        # ask the llm to check values
        complementary_list = df_candidates['product_name'].tolist()
        complete_list = self.check_complementary(product_name=product_name, complementary_list=complementary_list, verbose=verbose)
        df_filtered = pd.DataFrame(complete_list)
        df_filtered.columns = ['product_name', 'recommended_product', 'reasoning', 'score']
        df_filtered['llm_product'] = df_candidates['llm_product']
        df_filtered['index'] = df_candidates['index']
        df_filtered['similarity_score'] = df_candidates['score']
        df_filtered = df_filtered[['index', 'product_name', 'llm_product', 'recommended_product', 'reasoning', 'similarity_score', 'score']]
        return df_filtered


    def find_product_complementaries(self, product_names):

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
                        if consecutive_err == 5:
                            # maximum consecutive errors before exiting the iteration
                            break
            
            df_complementaries = pd.concat(df_list)
            return df_complementaries