import requests
import lxml.html as lh
import json
from statistics import mode
import re

pages = [
    'http://www.goseattleu.com/StaffDirectory.dbml',
    'http://www.astateredwolves.com/ViewArticle.dbml?ATCLID=207138',
    'https://athletics.arizona.edu/StaffDirectory/index.asp',
    'https://arizonawildcats.com/sports/2007/8/1/207969432.aspx'
]

sport = "volleyball"


def get_data(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95'
                             ' Safari/537.36'}
    content = requests.get(url, headers=headers).text
    tree = lh.fromstring(content)
    rows = tree.xpath('//tr')

    if len(rows) == 0:
        #todo: check iframe
        pass

    most_common = mode([len(T) for T in rows])
    staff = []
    flag = False
    for row in rows:
        if flag and len(row) == most_common:
            phone = ""
            email = ""

            for j in range(2, len(row)):
                if '@' in row[j].text_content().strip():
                    email = row[j].text_content().strip()
                if re.match(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
                            row[j].text_content().strip()):
                    phone = row[j].text_content().strip()
                    if ('\t' in phone):
                        phone = phone[:14]

            member = {
                "sport": sport,
                "name": row[0].text_content().strip(),
                "position": row[1].text_content().strip(),
                "phone": phone,
                "email": email
            }
            staff.append(member)
        elif len(row) == 1:
            if flag:
                break
            if row[0].text_content().strip().lower() == sport.lower():
                flag = True
        elif len(row.attrib) > 0:
            for column in row.iterchildren():
                if column.text_content().strip().lower() == sport.lower():
                    flag = True
                    break


    print(json.dumps(staff, indent=4))

def main():
    # todo: add argument parsing
    url = pages[0]
    get_data(url)


if __name__ == '__main__':
    main()
