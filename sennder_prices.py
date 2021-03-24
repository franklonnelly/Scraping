from bs4 import BeautifulSoup
import requests
import pandas as pd

source_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_sny_w.htm'
# URL for Gasoline with monthly data selection and grouped by area
m_gas_area_url = 'https://www.eia.gov/dnav/pet/pet_pri_gnd_a_epm0_pte_dpgal_m.htm'
r = requests.get(m_gas_area_url)

if r == 200:
    print('URL Connection working')
else:
    print('Error code:{}'.format(r))
    
soup= BeautifulSoup(r.text, 'html.parser')
# or html=urlopen(m_area_url)
print(soup.title.text)

# Find all rows containing data
data_rows = soup.find_all('tr', {'class':'DataRow'})
print(len(data_rows))

for dr in data_rows:
    if dr.find('a', href=True):
        location = dr.find('td', {'class':'DataStub1'}).text # Filter in states only
        link = dr.find('a', {'class':'Hist'})['href']
        prefix, series, suffix = link.split('&')
        series_id = series.replace('s=','PET.')
        monthly_data = 'https://www.eia.gov/opendata/qb.php?sdid={}.M'.format(series_id)
        df = pd.read_html(monthly_data)
    else:
        continue
