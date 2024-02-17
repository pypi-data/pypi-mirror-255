from lxml import etree

def extract_str_from_xml(xml_text: str) -> str:
    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring(xml_text, parser=parser)
    notags = etree.tostring(tree, encoding="utf8", method="text").decode("utf-8")
    return notags
