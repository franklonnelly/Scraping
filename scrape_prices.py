"""Web scraping Oil and Gasoline Prices"""

from bs4 import BeautifulSoup    
import requests
import pandas as pd
import csv

source_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_sny_w.htm'
# URL with monthly data selection grouped by area
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
    loc_type = 'Regions'
    for dr in data_rows:
        if dr.find('a', href=True):
            location = dr.find('td', {'class':'DataStub1'}).text # Filter in states only
            link = dr.find('a', {'class':'Hist'})['href']
            prefix, series, suffix = link.split('&')
            series_id = series.replace('s=','PET.')
            monthly_data = 'https://www.eia.gov/opendata/qb.php?sdid={}.M'.format(series_id)
            df_data = pd.read_html(monthly_data)
            df_data[0]['Location']=location
            df_data[0]['Aggregation']=loc_type
            print('Done: {}'.format(location))
        elif dr.find('td', {'class':'DataStub2'}):
            # Identify aggregation label
            loc_type = dr.find('td', {'class':'DataStub2'}).text.replace('\n','')
            print('Type of location: {}'.format(loc_type))
        else:
            continue
        df_all = df_all.append(df_data[0], ignore_index=True)
        df_all.drop('Series Name', inplace=True, axis=1)
    return df_all

gas_df = find_all_data(gas_url)
diesel_df = find_all_data(diesel_url)

"""Save results"""

diesel_csv = r'C:\Users\Francesco.Sollitto\Desktop\Diesel_Prices.csv'
gas_csv = r'C:\Users\Francesco.Sollitto\Desktop\Gas_Prices.csv'
price_var = r'C:\Users\Francesco.Sollitto\Desktop\Price_variations.csv'
min_trimester = r'C:\Users\Francesco.Sollitto\Desktop\Min_state.txt'

diesel_df.to_csv(diesel_csv, index=False)
gas_df.to_csv(gas_csv, index=False)


"""Statistics per State"""
# states = ['California','Colorado','Florida','Massachusetts','Minnesota',
#          'New York','Ohio','Texas','Washington']

def state_variations(gas_df):
    df_states = gas_df.loc[gas_df['Aggregation']=='States']
    df_st = df_states.drop_duplicates(['Location'])
    state_list = df_st['Location'].tolist()
    output=''
    for st in state_list:
        min_value = df_states.loc[(df_states['Location'] == st) & (df_states['Period']>202100), 'Value'].min()
        max_value = df_states.loc[(df_states['Location'] == st) & (df_states['Period']>202100), 'Value'].max()
        variation = abs(round((min_value - max_value),3))
        output += '{};{}\n'.format(st, variation)
        # Csv write row
    with open(price_var, 'w+') as pv:
        pv.write(output)


def state_min_avglast_3months(gas_df):
    df_states = gas_df.loc[gas_df['Aggregation']=='States']
    df_st = df_states.drop_duplicates(['Location'])
    state_list = df_st['Location'].tolist()
    df_means = pd.DataFrame()
    for st in state_list:
        df_trim = df_states.loc[(df_states['Location'] == st) & (df_states['Period']>202100)]
        df_mean = df_trim.groupby(['Location'], as_index=False).mean()
        df_means = df_means.append(df_mean)
    state_min = df_means[df_means.Value == df_means.Value.min()]
    # min_value = round(df_means['Value'].min(),3)    
    output = '{},{}'.format(state_min.iloc[0]['Location'], round(state_min.iloc[0]['Value'], 2))
    with open(min_trimester, 'w+') as mt:
        mt.write(output)
        
        
        
