import argparse
import sys
import requests
import lxml.html as lh
import json
from statistics import mode
import re


def get_data(url, sport, element, element_id, element_index, element_class):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
                             ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95'
                             ' Safari/537.36'}
    content = requests.get(url, headers=headers).text
    tree = lh.fromstring(content)
    rows = tree.xpath('//tr')

    if len(rows) == 0:
        tree = tree.xpath('//iframe')
        if len(tree) == 0:
            return
        for el in tree:
            url = el.attrib['src']
            regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if re.match(regex, url):
                get_data(url,
                         sport,
                         element,
                         element_id,
                         element_index,
                         element_class)
        return

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


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("sport")
    parser.add_argument("--html_elem", choices=['table', 'tr', 'td'])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--element_id')
    group.add_argument('--element_index')
    group.add_argument('--element_class')

    return parser.parse_args(args)


def main():
    parser = parse_args(sys.argv[1:])
    if parser.html_elem \
            and parser.element_id is None \
            and parser.element_index is None \
            and parser.element_class is None:
        print('--html_elem requires --element_id or --element_index ''or --element_class')
        exit()

    get_data(parser.url,
             parser.sport,
             parser.html_elem,
             parser.element_id,
             parser.element_index,
             parser.element_class)


if __name__ == '__main__':
    main()
