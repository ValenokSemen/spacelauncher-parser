from lxml import etree
xml = etree.fromstring(xml_str)
elems = xml.xpath(r'//label')  #xpath expression to find all '<label ...> elements

# counts the number of parents to the root element
def get_depth(element):
    depth = 0
    parent = element.getparent()
    while parent is not None:
        depth += 1
        parent = parent.getparent()
    return depth


def reduce_by_depth(element_list):
    crumbs = []
    depth = 0
    elem_crumb = ['']*10
    for elem in element_list:
        depth = get_depth(elem)
        elem_crumb[depth] = elem.text
        elem_crumb[depth+1:] = ['']*(10-depth-1)
        # join all the non-empty string to get the breadcrumb
        crumbs.append('/'.join([e for e in elem_crumb if e]))
    return crumbs

reduce_by_depth(elems)