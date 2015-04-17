#GROUP228

DIRECTORY = Modelio.getInstance().getContext().getWorkspacePath().toString() + "/macros/"

from xml.etree.ElementTree import ElementTree
tree = ElementTree()

tree.parse(DIRECTORY + "library.xml")

root = tree.getroot()

fact= theUMLFactory()
myp = instanceNamed(Package,"MyPackage")

classes = []
dependencies = {}

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
        self.parent = None

def run():
    for c in myp.getOwnedElement(Class):
        c.delete();
    try:
        trans = theSession().createTransaction("UML generator")
        print "Generating classes"
        for class_ in classes:
            createClass(class_)
        print "Generating dependencies"
        for d in dependencies.keys():
            print str(d) + " --> " + str(dependencies[d])
            fact.createDependency(dependencies[d]["parent"], dependencies[d]["child"], "LocalModule", "FKC")
        print "Done !"
        trans.commit()
        trans.close()
    except:
        trans.rollback()
        raise
    finally:
        trans.close()


def createClass(class_):
    print class_.name
    c = fact.createClass(class_.name, myp)
    for a in class_.attributes:
        t = createAttribute(class_, a)
    if t:
        c.addStereotype("LocalModule", "T")
  
def createAttribute(class_, attribute):
    t = False
    output = "\t" + attribute.name + " : " + attribute.type_ + " ["
    c = instanceNamed(Class, class_.name)
    a = fact.createAttribute(attribute.name, sqlType2UML(attribute.type_), c)
    if attribute.name in class_.pks:
        output += "PK"
        a.addStereotype("LocalModule", "PK")
    else:
        t = True
    if attribute.parent != None:
        output += " FK"
        a.addStereotype("LocalModule", "FK")
        if not (attribute.parent in dependencies.keys()):
            dependencies[attribute.parent] = {"child": None, "parent": a}
        else:
            dependencies[attribute.parent]["parent"] = a
    else:
        t = True
    for child in attribute.children:
        if not (child in dependencies.keys()) :
            dependencies[child] = {"child": a, "parent": None}
        else:
            dependencies[child]["child"] = a
    print output + "]"
    return t
        
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
        classes.append(class_)
    run()
process()