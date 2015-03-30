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

def createClass(nameClass):
    try:
        trans = theSession().createTransaction("Class " + nameClass)
        c1 = fact.createClass(nameClass,myp)
        trans.commit()
        trans.close()
    except:
        trans.rollback()
        raise    
    trans.close()
        
  
def createAttribute(className, type_ ,AttributeName):
    try:
        trans = theSession().createTransaction("Attribut " + AttributeName)
        class_ = instanceNamed(Class, className)
        a = fact.createAttribute(AttributeName, type_, class_)
        trans.commit()
    except:
        trans.rollback()
        raise
    trans.close()
        
def process():
    for table in root.find("tables"):
        class_ = table.attrib.get("name")
        print class_
        createClass(class_)
        for attribute in table.findall("column"):
            attribute_ = attribute.attrib.get("name")
            type_ = sqlType2UML(attribute.attrib.get("type"))
            print "\t" + attribute_ + " : " + type_.name
            createAttribute(class_, type_, attribute_)

for class_ in myp.getOwnedElement(Class):
    class_.delete()
process()