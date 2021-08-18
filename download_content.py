from bs4 import BeautifulSoup
from urllib import request
import lxml
import sys

# Gather content-html elements from discussion links.
# Links in a file given as parameter
# Results saved to file


file = sys.argv[1]
year = sys.argv[1][-8:-4]

with open(file, 'r', encoding="utf-8") as f:
    contents = f.read()
    links = contents.split('\n')
    for link in links[1:]:
        page = request.urlopen(link)
        as_bytes = page.read()
        string = as_bytes.decode('utf8')
        page.close()
        soup = BeautifulSoup(string, 'lxml')
        # Get the relevant content-element in either of the two:
        # <div id="content" class="PTK KESKUST">
        # <div id="content" class="PTK SKTP">
        content = soup.find(id='content')
        # save content to file as html-string
        if content:
            link_tag = soup.new_tag('a', href=link)
            content.append(link_tag)
            with open('discussions_{:s}.html'.format(year), 'a', encoding='utf-8') as save_to:
                save_to.write('{:s}\n'.format(str(content)))
            print(link[-30:])
