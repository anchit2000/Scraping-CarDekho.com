import os
import requests
try:
  import pandas as pd
except ModuleNotFoundError:
  os.system("python3 -m pip install pandas")
try:
  from bs4 import BeautifulSoup
except ModuleNotFoundError:
  os.system("python3 -m pip install pip install beautifulsoup4")
  
def make_df(url : str ,car_name : str, company_name : str, model_name : str) -> pd.DataFrame:
  '''
  Extracts all the tables present in the url, does basic cleaning and outputs a dataframe.
  Cleaning is customised for cardekho.com
  '''
  headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
           "Upgrade-Insecure-Requests" : "1",
           "sec-ch-ua-platform" : "macOS",
           "sec-ch-ua-mobile" : "?0",
          #  "sec-ch-ua": ' Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97',
           'DNT': '1'
           }
  try:
    # df = pd.read_html(requests.get(url,headers = headers).content)
    # df = pd.concat(df)
    soup = BeautifulSoup(requests.get(url,headers = headers).content, features="html.parser")
    df = pd.DataFrame(columns = ['car_name','company_name','model_name'])
    df.loc[0] = "No"
    df['car_name'], df['company_name'] = car_name.replace("_"," ").upper(), company_name.replace("_"," ").upper()
    table_soup = soup.find_all("table")
    index = 0
    for table in table_soup:
      rows = table.find("tbody").find_all("tr")
      for row in rows:
        data = row.find_all("td")
        df[data[0].text] = ""
        if data[1].text != "":
          df[data[0].text].loc[0] = data[1].text
        else:
          if "check" in str(data[1]):
            df[data[0].text].loc[0] = "Yes"
          elif "delete" in str(data[1]):
            df[data[0].text].loc[0] = "No"
          else:
            print(data[1])
    try:
      df = df.drop(['City','On-Road Price'],axis = 1)
    except Exception as e:
      # print(url)
      pass
  # df = df.dropna(subset=[0]).set_index(0).T
  except Exception as e:
    print(e)
    print(e.args)
    print(url)
    return pd.DataFrame()
  return df

def make_url(car_name : str) -> list:
  '''
  Accepts company name and car name separated by an underscore
  Made for Cardekho.com
  '''
  car_name = car_name.split("_")
  company_name = car_name[0].replace(" ","_")
  car_model = car_name[1].replace(" ","_")
  url = f'https://www.cardekho.com/carmodels/{company_name}/{car_model}'
  headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
           "Upgrade-Insecure-Requests" : "1",
           "sec-ch-ua-platform" : "macOS",
           "sec-ch-ua-mobile" : "?0",
          #  "sec-ch-ua": ' Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97',
           'DNT': '1'
           }
  contents = requests.get(url,headers = headers).content
  soup = BeautifulSoup(contents, features="html.parser")
  table_contents = soup.find('table',attrs={"class": 'allvariant contentHold'}).find('tbody').find_all('tr')
  urls = []
  model_names = []
  for i in range(len(table_contents)):
    urls.append("https://www.cardekho.com/overview/"+company_name+"_"+car_model+"/"+company_name+"_"+car_model+"_"+table_contents[i].find('td').find('a').text.replace(" ","_")+".htm")
    model_names.append(table_contents[i])  
  return urls,car_model,company_name,model_names

car_names = ['Kia_Sonet','Kia_Seltos', 'Maruti_Vitara Brezza', 'Maruti_Ertiga']

df_list = []
for car_name in car_names:
  urls,car_model,company_name,model_names = make_url(car_name)
  for url, model_name in zip(urls,model_names):
    df_list.append(make_df(url,car_model,company_name,model_name))

# in case some column is not present we will add that column in no or nan
columns_max = []
for each_df in df_list:
  columns_max+=list(each_df.columns)
columns_max = list(set(columns_max))

df_all_models = pd.DataFrame(columns = columns_max)
for i in range(len(df_list)):
  df_all_models.loc[i] = df_list[i].T.to_dict()[1]

df_all_models = df_all_models.replace(np.nan,"Not Available")
df_all_models.to_csv("car_details.csv")
