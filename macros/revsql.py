#GROUP228

import os
DIRECTORY = Modelio.getInstance().getContext().getWorkspacePath().toString() + "/macros/"

from xml.etree.ElementTree import ElementTree
tree = ElementTree()

tree.parse(DIRECTORY + "library.xml")

root = tree.getroot()

fact= theUMLFactory()
myp = instanceNamed(Package,"MyPackage")

def sqlType2UML(type_):
    types = theSession().getModel().getUmlTypes()
    if type_ in ['VARCHAR', 'VARCHAR2', 'CHAR']: 
        return types.getSTRING()
    elif type_ in ['INT', 'BIGINT']:  
        return types.getINTEGER()
    elif type_ == 'DATE':  
        return types.getDATE()
    else:
        return type_ 

class UMLClass:
    def __init__(self):
        self.name = ''
        self.attributes = []
        self.pks = []
        self.fks = []

class UMLAttribute:
    def __init__(self):
        self.name = ''
        self.children = []
        self.parent = ''

def createClass(class_):
    try:
        trans = theSession().createTransaction("Class " + class_.name)
        print class_.name
        fact.createClass(class_.name, myp)
        for a in class_.attributes:
            print '\t' + a.name
            createAttribute(class_, a) 
        trans.commit()
        trans.close()
    except:
        trans.rollback()
        raise    
    trans.close()
  
def createAttribute(class_, attribute):
    c = instanceNamed(Class, class_.name)
    a = fact.createAttribute(attribute.name, sqlType2UML(attribute.type_), c)
    if attribute.name in class_.pks:
        a.addStereotype("LocalModule", "PK")
        
def process():
    for table in root.find("tables"):
        class_ = UMLClass()
        class_.name = table.attrib.get("name")
        for pk in table.findall("primaryKey"):
            class_.pks.append(pk.attrib.get("column"))
        for attribute in table.findall("column"):
            attribute_ = UMLAttribute()
            attribute_.name = attribute.attrib.get("name")
            attribute_.type_ = attribute.attrib.get("type")
            if attribute.find('parent') != None:
                attribute_.parent = attribute.find('parent').attrib.get('foreignKey')
            for child in attribute.findall('child'):
                attribute_.children.append(child.attrib.get('foreignKey'))
            class_.attributes.append(attribute_)
        createClass(class_)

for c in myp.getOwnedElement(Class):
    c.delete();
process()