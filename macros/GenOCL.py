"""
=========================================================
                       GenOCL.py
 Generate a USE OCL specification from a UML package
=========================================================

FILL THIS SECTION AS SHOWN BELOW AND LINES STARTING WITH ###
@author Abdourahamane TOURE <toureab@e.ujf-grenoble.fr>
@author Donatien GBE <donatien.gbe@gmail.com>
@group  G228

Current state of the generator
----------------------------------
FILL THIS SECTION 
Explain which UML constructs are supported, which ones are not.
What is good in your generator?
What are the current limitations?

Current state of the tests
--------------------------
FILL THIS SECTION 
Explain how did you test this generator.
Which test are working? 
Which are not?

Observations
------------
Additional observations could go there
"""


#---------------------------------------------------------
#   Helpers on the source metamodel (UML metamodel)
#---------------------------------------------------------
# The functions below can be seen as extensions of the
# modelio metamodel. They define useful elements that 
# are missing in the current metamodel but that allow to
# explorer the UML metamodel with ease.
# These functions are independent from the particular 
# problem at hand and could be reused in other 
# transformations taken UML models as input.
#---------------------------------------------------------

# example
def isAssociationClass(element):
    """ 
    Return True if and only if the element is an association 
    that have an associated class, or if this is a class that
    has a associated association. (see the Modelio metamodel
    for details)
    """
    return element.linkToAssociation != None
    
 
#---------------------------------------------------------
#   Application dependent helpers on the source metamodel
#---------------------------------------------------------
# The functions below are defined on the UML metamodel
# but they are defined in the context of the transformation
# from UML Class diagramm to USE OCL. There are not
# intended to be reusable. 
#--------------------------------------------------------- 

# example
def associationsInPackage(package):
    """
    Return the list of all associations that start or
    arrive to a class which is recursively contained in
    a package.
    """
    associations = []
    for element in package.ownedElement:
        if isinstance(element, Class):
            for target in element.targetingEnd:
                if target.association not in associations and target.association.linkToClass == None:
                    associations.append(target.association)
    return associations
    

    
#---------------------------------------------------------
#   Helpers for the target representation (text)
#---------------------------------------------------------
# The functions below aims to simplify the production of
# textual languages. They are independent from the 
# problem at hand and could be reused in other 
# transformation generating text as output.
#---------------------------------------------------------


# for instance a function to indent a multi line string if
# needed, or to wrap long lines after 80 characters, etc.

#---------------------------------------------------------
#           Transformation functions: UML2OCL
#---------------------------------------------------------
# The functions below transform each element of the
# UML metamodel into relevant elements in the OCL language.
# This is the core of the transformation. These functions
# are based on the helpers defined before. They can use
# print statement to produce the output sequentially.
# Another alternative is to produce the output in a
# string and output the result at the end.
#---------------------------------------------------------



# examples

def umlEnumeration2OCL(enumeration):
    """
    Generate USE OCL code for the enumeration
    """
    print 'enum %s' % enumeration.name + ' {'
    value = ''
    for val in enumeration.value:
        value += '\t' + val.name + ',\n'
    print value[:-2] + '\n}'

def umlBasicType2OCL(basicType):
    """
    Generate USE OCL basic type. Note that
    type conversions are required.
    """
    type_ = basicType.name
    if type_ == 'string': 
        return 'String'
    elif type_ == 'integer':  
        return 'Integer'
    elif type_ == 'float':    
        return 'Real'
    elif type_ == 'boolean':  
        return 'Boolean'
    else:
        return type_
    
# etc.

def umlClass2OCL(class_):
    if isAssociationClass(class_):
        print "associationclass " + class_.name + " between"
        for l in class_.linkToAssociation.associationPart.end:
            print "\t%s[%s..%s] role %s" %(l.target.name, l.multiplicityMin, l.multiplicityMax, l.name)
    else:
        abst = 'abstract ' if class_.isAbstract else ''
        superClasses = ''
        if class_.parent:
            superClasses += ' < '
            for p in class_.parent:
                superClasses += '%s, ' % p.superType.name
            superClasses = superClasses[:-2]
        print '%sclass %s%s' %(abst, class_.name, superClasses)
    attributes2OCL(class_.ownedAttribute)
    operations2OCL(class_.ownedOperation)
    print ('end\n')

def attributes2OCL(attr):
    if (attr):
        print "attributes"
    for a in attr:
        name = a.name
        type_ = umlBasicType2OCL(a.type)
        ann = ''
        if a.isDerived :
            ann += ' @derived'
        if a.visibility == VisibilityMode.PUBLIC :
            ann += ' @Public'
        elif a.visibility == VisibilityMode.PRIVATE :
            ann += ' @Private'
        elif a.visibility == VisibilityMode.PACKAGEVISIBILITY :
            ann += ' @Package'
        elif a.visibility == VisibilityMode.PROTECTED :
            ann += ' @Protected'
        ann = ' --' + ann if ann else ''
        print '\t%s : %s%s' %(name ,type_,ann)

def operations2OCL(oper):
    if (oper):
        print 'operation'
    for o in oper:
        name = o.name
        params = ''
        for param in o.IO:
            params += "%s : %s," % (param.name, umlBasicType2OCL(param.type))
        if (o.IO):
            params = params[:-1]
        type_ = ' : %s' % umlBasicType2OCL(o.return.type) if o.return else ''
        print '\t%s(%s)%s' %(name,params,type_)

def association2OCL(package):
    for association in associationsInPackage(package):
        kind = 'association'
        for x in association.end:
            if x.aggregation.name == "KindIsComposition":
                kind = 'composition'
            elif association.end[0].aggregation.name == "KindIsAggregation":
                kind = 'aggregation'
        print '%s %s between' % (kind, association.name)
        for x in association.end:
            print '\t%s[%s..%s] role %s' % (x.target.name, x.multiplicityMin, x.multiplicityMax, x.name)
        print 'end'

def package2OCL(package):
    """
    Generate a complete OCL specification for a given package.
    The inner package structure is ignored. That is, all
    elements useful for USE OCL (enumerations, classes, 
    associationClasses, associations and invariants) are looked
    recursively in the given package and output in the OCL
    specification. The possibly nested package structure that
    might exist is not reflected in the USE OCL specification
    as USE is not supporting the concept of package.
    """
    for element in package.getOwnedElement():
        if isinstance(element, Enumeration):
            umlEnumeration2OCL(element)
        if isinstance(element, Class):
            umlClass2OCL(element)
    association2OCL(package)



#---------------------------------------------------------
#           User interface for the Transformation 
#---------------------------------------------------------
# The code below makes the link between the parameter(s)
# provided by the user or the environment and the 
# transformation functions above.
# It also produces the end result of the transformation.
# For instance the output can be written in a file or
# printed on the console.
#---------------------------------------------------------

# (1) computation of the 'package' parameter
# (2) call of package2OCL(package)
# (3) do something with the result
for element in selectedElements:
    if isinstance(element, Package):
        package2OCL(element)
    elif isinstance(element, Class):
        umlClass2OCL(element)
    elif isinstance(element, Enumeration):
        umlEnumeration2OCL(element)
    else:
        print 'element missed'