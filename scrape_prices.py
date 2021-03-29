"""Web scraping Oil and Gasoline Prices (for Sennder)"""
from bs4 import BeautifulSoup    
# from urllib.request import urlopen
import requests
import pandas as pd

source_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_sny_w.htm'
# URL with MONTHLY data selection grouped by AREA
gas_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_a_epm0_pte_dpgal_m.htm'
diesel_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_a_epd2d_pte_dpgal_m.htm'

def read_url_html(url):
    r = requests.get(url)
    if r.status_code == 200:
        print('URL Connection working')
    else:
        print('Error code:{}'.format(r))
    soup= BeautifulSoup(r.text, 'html.parser')
    # or html=urlopen(m_area_url)
    print('Dataset name: {}'.format(soup.title.text))
    return soup

def find_all_data(url):
    soup = read_url_html(url)
    # Create empty DataFrame
    df_all = pd.DataFrame()
    data_rows = soup.find_all('tr', {'class':'DataRow'})
    for dr in data_rows:
        if dr.find('a', href=True):
            location = dr.find('td', {'class':'DataStub1'}).text # Filter in states only
            link = dr.find('a', {'class':'Hist'})['href']
            prefix, series, suffix = link.split('&')
            series_id = series.replace('s=','PET.')
            monthly_data = 'https://www.eia.gov/opendata/qb.php?sdid={}.M'.format(series_id)
            df_data = pd.read_html(monthly_data)
            df_data[0]['Location']=location
            print('Done: {}'.format(location)) 
#        elif dr.find('td', {'class':'DataStub2'}):
#            # Identify aggregation label
#            loc_type = dr.find('td', {'class':'DataStub2'}).text.replace('\n','')
#            df_data[0]['Aggregation']=loc_type
        else:
            continue
        df_all = df_all.append(df_data[0], ignore_index=True)
    return df_all

gas_df = find_all_data(gas_url)
diesel_df = find_all_data(diesel_url)


"""Statistics per State"""
states = ['California','Colorado','Florida','Massachusetts','Minnesota',
          'New York','Ohio','Texas','Washington']

def state_variations(df_name=gas_df):
    for index, item in df_name.iterrows():
        output = ''
        if item['Location'] in states:
            state = item['Location']
            min_value = df_name.loc[df_name['Location'] == state, 'Value'].min()
            max_value = df_name.loc[df_name['Location'] == state, 'Value'].max()
            variation = min_value - max_value
            # Csv write row
            output = '{},{},{},{}'.format(item['Location'], min_value, max_value, variation)
    return output


"""Save results"""
diesel_csv = r'C:\Users\Francesco.Sollitto\Desktop\Diesel_Prices.csv'
diesel_df.to_csv(diesel_csv, index=False)
