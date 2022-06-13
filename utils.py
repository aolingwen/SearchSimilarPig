#coding:utf8
import xml.etree.ElementTree as ET
import os
import sys

def parse_xml(xml_path):
    '''
    解析数据中的busi.xml
    :param xml_path:
    :return: 返回DOC_TYPE为XYZXLP001的图片路径和PAGE_ID
    '''
    img_paths = []
    page_ids = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for node in root:
        if node.tag == 'PAGES':
            for page_node in node:
                attrib = page_node.attrib
                if attrib['DOC_TYPE'] == 'XYZXLP001':
                    img_paths.append(attrib['PAGE_URL'])
                    page_ids.append(attrib['PAGE_ID'])
    return img_paths, page_ids