#GROUP228

import os
DIRECTORY = Modelio.getInstance().getContext().getWorkspacePath().toString() + "/macros/"

from xml.etree.ElementTree import ElementTree
tree = ElementTree()

tree.parse(DIRECTORY + "library.xml")

root = tree.getroot()


fact= theUMLFactory()
myp = instanceNamed(Package,"MyPackage")

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
        
  
def createAttribute(className, AttributeName):
    try:
        trans = theSession().createTransaction("Attribut " + AttributeName)
        class_ = instanceNamed(Class, className)
        a = fact.createAttribute(AttributeName, class_)
        trans.commit()
    except:
        trans.rollback()
        raise
    trans.close()
        
        
for element in root:
    print (element.tag)
    for table in element:
        class_ = table.attrib.get("name")
        print class_
        #createClass(class_)
        for attribute in table.findall("column"):
            if attribute.attrib.get("name") != None:
                attribute_ = attribute.attrib.get("name")
                print "\t" + attribute.attrib.get("name")
                #createAttribute(class_, attribute_)
        
        
