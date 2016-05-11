import xml.etree.cElementTree as ET
import pprint as pp
import os
import re
import json
import codecs
from pymongo import MongoClient


'''utility functions'''
def parse_array(v):
    if (v[0] == "{") and (v[-1] == "}"):
        v = v.lstrip("{")
        v = v.rstrip("}")
        v_array = v.split("|")
        v_array = [i.strip() for i in v_array]
        return v_array
    return [v]


'''BEGIN BLOCK TO ORGANIZE DATA INTO DESIRED STRUCTURE'''
def datadesign(fname,pretty = False):
    data = []
    file_out = "{0}.json".format(fname)
    with codecs.open(file_out, "w") as fo:
        for event,elem in ET.iterparse(fname, events=('start',)):
            if elem.tag == 'node' or elem.tag == 'way':
                el = shape_element(elem)
                if el:
                    data.append(el)
                    
        if pretty:
            fo.write(json.dumps(data, indent=2)+"\n")
        else:
            fo.write(json.dumps(data) + "\n")
    
        
    return data
    
            
def shape_element(element):
    #Template dictionary
    itemdict = {}
    
    created = {
              "version":None,
              "changeset":None,
              "timestamp":None,
              "user":None,
              "uid":None
            }
    address = {'city': 'NULL',
              'postcode': 'NULL'}
    pos = []
    lat = None
    #Loop through element to collect all data and add it to the node dictionary
    for key, val in element.items():
        if key == 'lat':
            lat = val
        elif key == 'lon':
            lon = val   
        elif key in created.keys():
            created[key] = val
        elif key == 'id':
            itemdict['_id'] = val
        else: 
            itemdict[key] = val

    #Way specific loop for node refs
    if element.tag == 'way':
        node_refs = []
        for nd in element.iter('nd'):
            node_refs.append(nd.get('ref'))
        itemdict['node_refs'] = node_refs
        
        
    #Now we do the subtags
    for tag in element.iter('tag'):
   
        #Organize the address
        if 'addr' in tag.attrib['k']:
            if 'housenumber' in tag.attrib['k']:
                address['housenumber'] = tag.attrib['v']
            elif 'postcode' in tag.attrib['k']:
                address['postcode'] = tag.attrib['v']
            elif 'street' in tag.attrib['k'] and 'street:' not in tag.attrib['k']:
                address['street'] = tag.attrib['v']
            elif 'city' in tag.attrib['k']:
                address['city'] = tag.attrib['v']
        #Deal with gnis tags        
        elif 'gnis' in tag.attrib['k']:
            if 'id' in tag.attrib['k']:
                itemdict['_id'] = tag.attrib['v']
            if 'County' in tag.attrib['k'] and 'num' not in tag.attrib['k']:
                address['city'] = tag.attrib['v']
        else:
            itemdict[tag.attrib['k']] = tag.attrib['v']
     
    
    #Dealing with the address miscellany
    if address:
        #Cities
        if address['city'] is not 'NULL':
            if address['city'].isupper():
                address['city'] = address['city'].lower()
                address['city'] = address['city'].title()
            if 'city' in address['city']:
                address['city'] = re.sub(r' \(city\)', '', address['city'])
            else: 
                address.pop('city')
        #Postal Codes
        if address['postcode'] is not 'NULL':
            if len(address['postcode']) == 5 and address['postcode'].isdigit():
                pass
            elif len(address['postcode']) == 10 and '-' in address['postcode']:
                address['postcode'] = address['postcode'].split('-', 1)[0]
            else:
                address.pop('postcode')
                
    
    #Add the dictionaries and sets that we've made to the final node entry 
    itemdict['type'] = element.tag
    if lat:
        pos.append(float(lat))
        pos.append(float(lon))
    if pos:
        itemdict['pos'] = pos
    if address:  
        itemdict['address'] = address
    if created:
        itemdict['created'] = created
        
    return itemdict
'''END BLOCK TO ORGANIZE DATA INTO DESIRED STRUCTURE'''
        
    
'''BEGIN MAIN FUNCTION'''
def main():
    filename = 'hrva.osm'
    data = datadesign(filename,False)



main()
