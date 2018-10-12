from xml.sax import saxutils
from xml.parsers.expat import ExpatError
import types
import datetime
import logging
import codecs
from xml.dom import minidom, Node
from utils import MetaInfo

def print_tag_file(filepath, feature):
    filehandle = codecs.open(filepath, 'w', 'utf8')

    filehandle.write(u'<?xml version="1.0" encoding="utf-8"?>\n')
    filehandle.write(obj_to_xml('document', feature))

    filehandle.close()

def read_tag_file(filepath, relurl):
    filehandle = codecs.open(filepath, 'r', 'utf8')

    metastring = filehandle.read()
    metainfo = xml_to_tagdict(relurl, metastring)

    filehandle.close()

    return metainfo

def obj_to_xml(tagName, obj):
    if type(obj) in types.StringTypes:
        return get_xml_tag(tagName, obj)

    tags = ['<%s>' % tagName]
    ks = obj.keys()
    ks.sort()
    for k in ks:
        newobj = obj[k]
        if isinstance(newobj, dict):
            tags.append(obj_to_xml(k, newobj))
        elif isinstance(newobj, list):
            if k == 'bench':
                tags.append(u'<%s>'% k)
                for o in newobj:
                    tags.append(obj_to_xml('name', o))
                tags.append(u'</%s>'% k)
            else:
                for o in newobj:
                    tags.append(obj_to_xml(k, o))
        elif isinstance(newobj,  datetime.datetime) or \
                isinstance(newobj, datetime.date):
            tags.append(obj_to_xml(k, date_to_xml(newobj)))
        else:
            tags.append(get_xml_tag(k, obj[k]))
    tags.append(u'</%s>' % tagName)
    xmltags =  u'\n'.join(tags)

    return xmltags

def xml_to_tagdict(docid, xmlstring):
    try:
        xmlnode = minidom.parseString(xmlstring)
    except ExpatError, e:
        logger = logging.getLogger('utils.commonfuncs')
        logger.error(u'Err %s in xml reading of tagfile  %s' % (e, docid))
        return None

    feature = xml_to_obj(xmlnode.childNodes[0])
    metainfo = MetaInfo()
    for k, v in feature.iteritems():
        if k == 'date':
            d = feature['date']
            metainfo['date'] = datetime.date(int(d['year']), int(d['month']), int(d['day']))
        else:
            metainfo[k] = v    

    return metainfo 

def xml_to_obj(xmlNode):
    xmldict = {}
    for node in xmlNode.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
           k = node.tagName
           obj = xml_to_obj(node)
           if xmldict.has_key(k):
               if not (type(xmldict[k]) == types.ListType):
                   xmldict[k] = [xmldict[k]]
               xmldict[k].append(obj)
           else:
               xmldict[k] = obj

    if xmldict:
        return xmldict
    else:
        return get_node_value(xmlNode.childNodes)

def get_xml_tag(tagName, tagValue, escape = True):
    if type(tagValue) == types.IntType:
        xmltag = u'<%s>%d</%s>' % (tagName, tagValue, tagName)
    elif type(tagValue) == types.FloatType:
        xmltag = u'<%s>%f</%s>' % (tagName, tagValue, tagName)
    else:
        if escape:
            tagValue = escape_xml(tagValue)

        xmltag = u'<%s>%s</%s>' % (tagName, tagValue, tagName)
    return xmltag

def escape_xml(tagvalue):
    return saxutils.escape(tagvalue)

def date_to_xml(dateobj):
    datedict =  {}

    datedict['day']   = dateobj.day
    datedict['month'] = dateobj.month
    datedict['year']  = dateobj.year

    return datedict

def get_node_value(xmlNodes):
    value = []
    ignoreValues = ['\n']
    for node in xmlNodes:
        if node.nodeType == Node.TEXT_NODE:
            if node.data not in ignoreValues:
                value.append(node.data)
    return u''.join(value)

