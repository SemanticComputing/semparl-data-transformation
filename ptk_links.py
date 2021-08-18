from bs4 import BeautifulSoup
from urllib import request
import lxml

# Script to gather main page content and urls for each discussion page from eduskunta.fi
# Currently built for one year at a time, year changed manually.
# Due to technical difficulties, tries to find PTKs up to while-clause
# This limit is chosen arbitrarily, and 'i' and while-limit must be edited for a second run


i = 1
year = 2014


while i < 176:
    url = 'https://www.eduskunta.fi/FI/Vaski/sivut/trip.aspx?triptype=ValtiopaivaAsiakirjat&docid=ptk+{:d}/{:d}'.format(
        i, year)
    page = request.urlopen(url)
    as_bytes = page.read()
    string = as_bytes.decode('utf8')
    page.close()
    print(i)
    i += 1
    soup = BeautifulSoup(string, 'lxml')
    content = soup.find(id='content')
    #divs = soup.find_all('div', ['KYSKESK', 'KESKUST'])
    # if divs:
    #    links = []
    #    for div in divs:
    #        links.append(div.a.attrs['href'])
    #    file = open('links_{:d}.txt'.format(year), 'a')
    #    for link in links:
    #        file.write('\nhttps://www.eduskunta.fi{:s}'.format(link))
    #    file.close()

    if content:
        with open('main_pages_{:d}.html'.format(year), 'a', encoding='utf-8') as save_to:
            save_to.write('{:s}\n'.format(str(content)))
