from lxml import etree
from datetime import datetime
import csv
import codecs
import ujson
import re
import os
import sys
import json
import requests
from hurry.filesize import size
import gzip
import shutil
import uuid

from functools import partial

p = partial(uuid.uuid5, uuid.NAMESPACE_DNS)

# all of the element types in dblp
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
# all of the feature types in dblp
all_features = {"address", "author", "booktitle", "cdrom", "chapter", "cite", "crossref", "editor", "ee", "isbn",
                "journal", "month", "note", "number", "pages", "publisher", "school", "series", "title", "url",
                "volume", "year"}


def log_msg(message):
    """Produce a log with current time"""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)


def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing, disabling DTD validation"""
    return etree.iterparse(
        source=dblp_path,
        dtd_validation=False,  # Disable DTD validation
        load_dtd=False,        # Prevent loading DTD (avoids entity loops)
        recover=True           # Attempt to continue even if there are errors
    )


def clear_element(element):
    """Free up memory for temporary element tree after processing the element"""
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]


def count_pages(pages):
    """Borrowed from: https://github.com/billjh/dblp-iter-parser/blob/master/iter_parser.py
    Parse pages string and count number of pages. There might be multiple pages separated by commas.
    VALID FORMATS:
        51         -> Single number
        23-43      -> Range by two numbers
    NON-DIGITS ARE ALLOWED BUT IGNORED:
        AG83-AG120
        90210H     -> Containing alphabets
        8e:1-8e:4
        11:12-21   -> Containing colons
        P1.35      -> Containing dots
        S2/109     -> Containing slashes
        2-3&4      -> Containing ampersands and more...
    INVALID FORMATS:
        I-XXI      -> Roman numerals are not recognized
        0-         -> Incomplete range
        91A-91A-3  -> More than one dash
        f          -> No digits
    ALGORITHM:
        1) Split the string by comma evaluated each part with (2).
        2) Split the part to subparts by dash. If more than two subparts, evaluate to zero. If have two subparts,
           evaluate by (3). If have one subpart, evaluate by (4).
        3) For both subparts, convert to number by (4). If not successful in either subpart, return zero. Subtract first
           to second, if negative, return zero; else return (second - first + 1) as page count.
        4) Search for number consist of digits. Only take the last one (P17.23 -> 23). Return page count as 1 for (2)
           if find; 0 for (2) if not find. Return the number for (3) if find; -1 for (3) if not find.
    """
    cnt = 0
    for part in re.compile(r",").split(pages):
        subparts = re.compile(r"-").split(part)
        if len(subparts) > 2:
            continue
        else:
            try:
                re_digits = re.compile(r"[\d]+")
                subparts = [int(re_digits.findall(sub)[-1]) for sub in subparts]
            except IndexError:
                continue
            cnt += 1 if len(subparts) == 1 else subparts[1] - subparts[0] + 1
    return "" if cnt == 0 else str(cnt)


def extract_feature(elem, features, include_key=False):
    """Extract the value of each feature"""
    if include_key:
        attribs = {'key': [elem.attrib['key']]}
    else:
        attribs = {}
    for feature in features:
        attribs[feature] = []
    for sub in elem:
        if sub.tag not in features:
            continue
        if sub.tag == 'title':
            text = re.sub("<.*?>", "", etree.tostring(sub).decode('utf-8')) if sub.text is None else sub.text
        elif sub.tag == 'pages':
            text = count_pages(sub.text)
        else:
            text = sub.text
        if text is not None and len(text) > 0:
            attribs[sub.tag] = attribs.get(sub.tag) + [text]
    return attribs


def parse_all(dblp_path, save_path, include_key=False):
    log_msg("PROCESS: Start parsing...")
    f = open(save_path, 'w', newline='', encoding='utf-8-sig', errors='ignore')
    for _, elem in context_iter(dblp_path):
        if elem.tag in all_elements:
            attrib_values = extract_feature(elem, all_features, include_key)
            f.write(str(attrib_values) + '\n')
        clear_element(elem)
    f.close()
    log_msg("FINISHED...")  # load the saved results line by line using json


def parse_entity(dblp_path, save_path, type_name, features=None, save_to_csv=False, include_key=False):
    """Parse specific elements according to the given type name and features"""
    log_msg("PROCESS: Start parsing for {}...".format(str(type_name)))
    assert features is not None, "features must be assigned before parsing the dblp dataset"
    results = []
    attrib_count, full_entity, part_entity = {}, 0, 0
    for _, elem in context_iter(dblp_path):
        if elem.tag in type_name:
            attrib_values = extract_feature(elem, features, include_key)  # extract required features
            results.append(attrib_values)  # add record to results array
            for key, value in attrib_values.items():
                attrib_count[key] = attrib_count.get(key, 0) + len(value)
            cnt = sum([1 if len(x) > 0 else 0 for x in list(attrib_values.values())])
            if cnt == len(features):
                full_entity += 1
            else:
                part_entity += 1
        elif elem.tag not in all_elements:
            continue
        clear_element(elem)
    if save_to_csv:
        f = open(save_path, 'w', newline='', encoding='utf8')
        writer = csv.writer(f, delimiter=',')
        writer.writerow(features)  # write title
        for record in results:
            # some features contain multiple values (e.g.: author), concatenate with `::`
            row = ['::'.join(v) for v in list(record.values())]
            writer.writerow(row)
        f.close()
    else:  # default save to json file
        with codecs.open(save_path, mode='w', encoding='utf8', errors='ignore') as f:
            ujson.dump(results, f)
    return full_entity, part_entity, attrib_count


def parse_author(dblp_path, save_path, save_to_csv=False):
    type_name = ['article', 'book', 'incollection', 'inproceedings']
    log_msg("PROCESS: Start parsing for {}...".format(str(type_name)))
    authors = set()
    for _, elem in context_iter(dblp_path):
        if elem.tag in type_name:
            authors.update(a.text for a in elem.findall('author'))
        elif elem.tag not in all_elements:
            continue
        clear_element(elem)
    if save_to_csv:
        f = open(save_path, 'w', newline='', encoding='utf8')
        writer = csv.writer(f, delimiter=',')

        batch_size = 100000  # Adjust batch size as needed
        authors_list = sorted(a if a is not None else "Unknown Author" for a in authors)

        for i in range(0, len(authors_list), batch_size):
            writer.writerows([[a] for a in authors_list[i:i+batch_size]])

        f.close()
    else:
        with open(save_path, 'w', encoding='utf8') as f:
            f.write('\n'.join(sorted(authors)))
    log_msg("FINISHED...")


def parse_article(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ['article']
    features = ['title', 'author', 'year', 'journal', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total articles found: {}, articles contain all features: {}, articles contain part of features: {}'
            .format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_inproceedings(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["inproceedings"]
    features = ['title', 'author', 'year', 'pages', 'booktitle']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total inproceedings found: {}, inproceedings contain all features: {}, inproceedings contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_proceedings(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["proceedings"]
    features = ['title', 'editor', 'year', 'booktitle', 'series', 'publisher']
    # Other features are 'volume','isbn' and 'url'.
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total proceedings found: {}, proceedings contain all features: {}, proceedings contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_book(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ["book"]
    features = ['title', 'author', 'publisher', 'isbn', 'year', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total books found: {}, books contain all features: {}, books contain part of features: {}'
            .format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def parse_publications(dblp_path, save_path, save_to_csv=False, include_key=False):
    type_name = ['article', 'book', 'incollection', 'inproceedings']
    features = ['title', 'year', 'pages']
    info = parse_entity(dblp_path, save_path, type_name, features, save_to_csv=save_to_csv, include_key=include_key)
    log_msg('Total publications found: {}, publications contain all features: {}, publications contain part of '
            'features: {}'.format(info[0] + info[1], info[0], info[1]))
    log_msg("Features information: {}".format(str(info[2])))


def download_file(url:str, filename:str)->bool:
    """Function that downloads files (general).
    
    Args:
        url (string): Url of where the model is located.
        filename (string): location of where to save the model
    Returns:
        boolean: whether it is successful or not.
    """
    is_downloaded = False
    with open(filename, 'wb') as file:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            #f.write(response.content)
            self.__log_msg('There was an error while downloading the DTD.')
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                file.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}] {}/{}'.format('█' * done, '.' * (50-done), size(downloaded), size(total)))
                sys.stdout.flush()
            sys.stdout.write('\n')
            # self.__log_msg('[*] Done!')
            is_downloaded = True

    return is_downloaded

def log_msg(message:str)->None:
    """
    Prints log with current time.

    Parameters
    ----------
    message : str
        The message to print out.

    Returns
    -------
    None


    """
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "DBLP", message)

def download_dtd():
    """Function that downloads the DTD from the DBLP website.
    Args:
        None
    Returns:
        None
    """
    filename_dtd = "dblp.dtd"
    url = "https://dblp.uni-trier.de/xml/dblp.dtd"
    download_file(url, filename_dtd)
    
    log_msg(f"DTD downloaded from {url}.")

def download_and_prepare_dataset():
    """Function that downloads the whole dataset (latest dump) from the DBLP website.
    Then it decompresses it
    Args:
        None
    Returns:
        None
    """
    filename_zip = "dblp.xml.gz"
    url = "https://dblp.uni-trier.de/xml/dblp.xml.gz"
    download_file(url, filename_zip)
    
    (f"Latest dump of DBLP downloaded from {url}.")
    
    filename_unzip = "dblp.xml"
    

    with gzip.open(filename_zip, 'rb') as f_in:
        with open(filename_unzip, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            

def download_the_latest_version_of_DBLP():
    download_dtd()
    download_and_prepare_dataset()
    log_msg("Dataset prepared. You can now parse it.")

import argparse
import os

def main():
    # Add command-line arguments
    parser = argparse.ArgumentParser(description="DBLP Data Processing Script")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading the DBLP XML file")
    parser.add_argument("--skip-parsing", action="store_true", help="Skip parsing XML to CSV")
    parser.add_argument("--only", type=str, help="Specify a dataset to process (e.g., 'author', 'book')", default=None)

    args = parser.parse_args()

    # Step 1: Download the dataset only if necessary
    dblp_path = 'dblp.xml'
    if not args.skip_download:
        if os.path.exists(dblp_path):
            print("DBLP XML already exists. Skipping download.")
        else:
            download_the_latest_version_of_DBLP()

    # Step 2: Ensure dataset folder exists
    dataset_path = 'dataset'
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)

    # Step 3: Parse XML to CSV only if necessary
    if not args.skip_parsing:
        parse_data(dblp_path, dataset_path, args.only)

def parse_data(dblp_path, dataset_path, only=None):
    """Handles selective parsing of data based on the 'only' argument"""
    if only in [None, 'article']:
        if not os.path.exists(os.path.join(dataset_path, "article.csv")):
            parse_article(dblp_path, os.path.join(dataset_path, "article.csv"), save_to_csv=True)
        else:
            print("Skipping article.csv - already exists.")

    if only in [None, 'publications']:
        if not os.path.exists(os.path.join(dataset_path, "publications.csv")):
            parse_publications(dblp_path, os.path.join(dataset_path, "publications.csv"), save_to_csv=True)
        else:
            print("Skipping publications.csv - already exists.")

    if only in [None, 'book']:
        if not os.path.exists(os.path.join(dataset_path, "book.csv")):
            parse_book(dblp_path, os.path.join(dataset_path, "book.csv"), save_to_csv=True)
        else:
            print("Skipping book.csv - already exists.")

    if only in [None, 'proceedings']:
        if not os.path.exists(os.path.join(dataset_path, "proceedings.csv")):
            parse_proceedings(dblp_path, os.path.join(dataset_path, "proceedings.csv"), save_to_csv=True)
        else:
            print("Skipping proceedings.csv - already exists.")

    if only in [None, 'inproceedings']:
        if not os.path.exists(os.path.join(dataset_path, "inproceedings.csv")):
            parse_inproceedings(dblp_path, os.path.join(dataset_path, "inproceedings.csv"), save_to_csv=True)
        else:
            print("Skipping inproceedings.csv - already exists.")

    if only in [None, 'author']:
        if not os.path.exists(os.path.join(dataset_path, "author.csv")):
            parse_author(dblp_path, os.path.join(dataset_path, "author.csv"), save_to_csv=True)
        else:
            print("Skipping author.csv - already exists.")

if __name__ == '__main__':
    main()
