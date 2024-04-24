import pandas as pd
import ast
import toml
from dotenv import load_dotenv
from tqdm import tqdm

from src.chat_groq import ChatGroqUty
from src.utils import convert_google_sheet_url
from src.nlp_preprocess import preprocess

load_dotenv()
config_file = toml.load("config.toml")

PATH = config_file["data"]["shopee"]["path"]


def get_raw_data(path:str = None) -> pd.DataFrame: #TODO: this will be changed to getting from Supabase
    """This function to convert the URL of the Google Sheet to a DataFrame

    Args:
        path (str): PATH of the Google Sheet. Defaults to None.

    Returns:
        pd.DataFrame: Output DataFrame.
    """
    url = convert_google_sheet_url(path)
    data = pd.read_csv(url)
    return data


def filter_data(df_raw, threshold: int = 500) -> pd.DataFrame:
    """This function to filter the data by the threshold

    Args:
        df_raw (_type_): DataFrame of the raw data.
        threshold (int, optional): threshold to filter. Defaults to 500.

    Returns:
        pd.DataFrame: output DataFrame.
    """
    df_filter = df_raw.loc[df_raw["Sold/M"].astype(float)>=threshold]
    df_filter = df_filter.sort_values(by=["Sold/M"],ascending=False)
    return df_filter

def flow_run():
    """Total function to run the flow
    """
    # Step 1: get the raw data
    df_raw = get_raw_data(PATH)
    
    
    if df_raw is not None:
        # Step 2: filter the data
        df_filter = filter_data(df_raw=df_raw)
        df_filter['Product'] = df_filter['Product'].map(lambda s:preprocess(s)) 
        df_filter["category"] = [""]*len(df_filter)
        df_filter["sub-category"] = [""]*len(df_filter)

        # Step 3: difine the LLM chat by Groq and Langchain
        chat_system = ChatGroqUty()

        ## TODO: using the existed sheet to get the category and sub-category
        category = ["Trái cây sấy khô",
                    "Snack & Bánh kẹo", 
                    "Bánh tráng", 
                    "Sữa",
                    "Nước mắm & nước tương",
                    "Nước mát & nước giải khát",
                    "Hạt khô",
                    "Bún - mì - phở",
                    "Hạt gia vị",
                    "Trà & cà phê",
                    "Dầu ăn",
                    "Các loại khác"]
        
        # Step 4: Looping the process through Dataframes
        final_result = pd.DataFrame([])
        count_fail = 0
        for index, row in tqdm(df_filter.iterrows(),total=df_filter.shape[0], desc="This is a slow task"):
            try:
                ## Step 4.1: get the product title
                each_product = row["Product"]
                ## Step 4.2: get the category and sub-category by LLM chat
                result = chat_system.get_response(product_title=each_product,
                                            category=category,
                )
                ## Step 4.3: convert the result to a dictionary
                result = result.dict()
                content = result['content']
                content = content.split('[')[1].split("]")[0]
                content = "["+content+"]"
                get_dict_result = ast.literal_eval(content.strip())
                
                ## Final dictionary
                title = list(set([x["product_title"] for x in get_dict_result]))
                cat = list(set([x["category"] for x in get_dict_result]))
                subcat = list(set([x["sub-category"] for x in get_dict_result]))

                final_dict = {
                    "product_title": title,
                    "category": cat,
                    "sub-category": subcat,
                }

                ## Step 4.4: update the category and sub-category to the dataframe
                df_filter.loc[index, "category"] = cat
                df_filter.loc[index, "sub-category"] = subcat
                
                if len(get_dict_result)>1:
                    final_result = pd.concat([final_result, pd.DataFrame.from_dict([final_dict])], ignore_index=True)
                else:
                    final_result = pd.concat([final_result, pd.DataFrame.from_dict([final_dict])], ignore_index=True)

            except:
                count_fail+=1
                df_filter.loc[index, "category"] = "N/A"
                df_filter.loc[index, "sub-category"] = "N/A"

        # Step 5: save the result
        final_result.to_csv("Final_check.csv")
        df_filter.to_csv("After_analysis.csv")
       
    
if __name__ == '__main__':
    flow_run()

    