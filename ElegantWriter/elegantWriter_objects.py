import yaml
import traceback
import itertools
import copy
import collections

stream = file('commands.yaml', 'r')
commandkeywords = yaml.load(stream)
stream.close()

stream = file('elements.yaml', 'r')
elementkeywords = yaml.load(stream)
stream.close()

class elegantLattice(object):

    def __init__(self):
        super(elegantLattice, self).__init__()
        # self.parent = parent
        self.elementObjects = {}
        self.lineObjects = {}
        self.commandObjects = {}


    def __getitem__(self,key):
        return getattr(self,key.lower())

    @property
    def elements(self):
        return self.elementObjects.keys()

    @property
    def lines(self):
        return self.lineObjects.keys()

    @property
    def commands(self):
        return self.commandObjects.keys()

    def addElement(self, name=None, **kwargs):
        if name == None:
            if not 'name' in kwargs:
                raise NameError('Element does not have a name')
            else:
                name = kwargs['name']
        element = elegantElement(name, **kwargs)
        setattr(self,name,element)
        # setattr(self.parent,name,element)
        self.elementObjects[name] = element.properties
        return element

    def addLine(self, name=None, line=[]):
        if name == None:
            raise NameError('Line does not have a name')
        line = elegantLine(name, line)
        setattr(self,name,line)
        # setattr(self.parent,name,line)
        self.lineObjects[name] = line.line
        return line

    def addCommand(self, name=None, **kwargs):
        if name == None:
            if not 'name' in kwargs:
                if not 'type' in kwargs:
                    raise NameError('Command does not have a name')
                else:
                    name = kwargs['type']
            else:
                name = kwargs['name']
        command = elegantCommand(name, **kwargs)
        setattr(self,name,command)
        # setattr(self.parent,name,command)
        self.commandObjects[name] = command.properties
        return command

    def writeCommandFile(self, filename):
        file = open(filename,'w')
        for command in self['commands'].iteritems():
            file.write(getattr(self,command[0]).write())
        file.close()

    def writeLatticeFile(self, filename, lattice):
        file = open(filename,'w')
        self.writeElements(file, lattice)
        self.writeLines(file, lattice)
        file.close()

    def _getLinelements(self, lattice):
        for element in getattr(self,lattice).line:
            element = getattr(self,element)
            if isinstance(element,(elegantLine)):
                [element.name]+self.lineDefinitions
                self._getLinelements(element.name)
            elif isinstance(element,(elegantElement)):
                self.elementDefinitions.append(element.name)
            else:
               print type(element)
        self.lineDefinitions.append(lattice)

    def _doLineExpansion(self,lattice):
        self.lineDefinitions = []
        self.elementDefinitions = []
        self._getLinelements(lattice)

    def expandLattice(self,lattice):
        self._doLineExpansion(lattice)
        return self.elementDefinitions

    def getLatticeDefinitions(self,lattice,headings):
        self._doLineExpansion(lattice)
        properties = collections.OrderedDict()
        for elem in self.elementDefinitions:
            properties[elem] = {}
            for heading in headings:
                if heading in getattr(self,elem).properties:
                    properties[elem][heading] = getattr(self,elem)[heading]
                else:
                    properties[elem][heading] = None
        return properties

    def writeElements(self, file, lattice):
        self._doLineExpansion(lattice)
        self.elementDefinitions = reduce(lambda l, x: l if x in l else l+[x], self.elementDefinitions, [])
        for element in self.elementDefinitions:
            file.write(getattr(self,element).write())

    def writeLines(self, file, lattice):
        self._doLineExpansion(lattice)
        self.lineDefinitions = reduce(lambda l, x: l if x in l else l+[x], self.lineDefinitions, [])
        for line in self.lineDefinitions:
            file.write(getattr(self,line).write())

class elegantObject(object):

    def __init__(self, name=None, type=None, **kwargs):
        super(elegantObject, self).__init__()
        if name == None:
            raise NameError('Command does not have a name')
        if type == None:
            raise NameError('Command does not have a type')
        self.name = name
        self.type = type
        self.commandtype = 'command'
        self.properties = {}
        self.properties['name'] = self.name
        self.properties['type'] = self.type
        if type in commandkeywords:
            self.allowedKeyWords = commandkeywords[self.type]
        elif type in elementkeywords:
            self.allowedKeyWords = elementkeywords[self.type]
        for key, value in kwargs.iteritems():
            if key.lower() in self.allowedKeyWords:
                try:
                    self.properties[key.lower()] = getattr(self,self.allowedKeyWords[key.lower()])(value)
                except:
                    pass

    @property
    def parameters(self):
        return self.properties

    def __getitem__(self,key):
        return self.properties.__getitem__(key.lower())

    def __setitem__(self,key,value):
        self.properties.__setitem__(key.lower(),value)
        setattr(self,key.lower(),value)

    def long(self, value):
        return int(value)

    def double(self, value):
        return float(value)

    def string(self, value):
        return '"'+value+'"'

class elegantCommand(elegantObject):

    def __init__(self, name=None, type=None, **kwargs):
        super(elegantCommand, self).__init__(name, type, **kwargs)
        if not type in commandkeywords:
            raise NameError('Command \'%s\' does not exist' % commandname)

    def write(self):
        wholestring=''
        string = '&'+self.type+'\n'
        for key, value in self.properties.iteritems():
            if not key =='name' and not key == 'type':
                string+='\t'+key+' = '+str(value)+'\n'
        string+='&end\n'
        return string

class elegantElement(elegantObject):

    def __init__(self, name=None, type=None, **kwargs):
        super(elegantElement, self).__init__(name, type, **kwargs)
        if not type in elementkeywords:
            raise NameError('Element \'%s\' does not exist' % commandname)

    def __mul__(self, other):
        return [self for x in range(other)]

    def __rmul__(self, other):
        return [self for x in range(other)]

    def __neg__(self):
        if 'bend' in self.type:
            newself = copy.deepcopy(self)
            # print newself.properties
            if 'e1' in newself.properties and 'e2' in newself.properties:
                e1 = newself['e1']
                e2 = newself['e2']
                newself.properties['e1'] = e2
                newself.properties['e2'] = e1
            elif 'e1' in newself.properties:
                newself.properties['e2'] = newself.properties['e1']
                del newself.properties['e1']
                del newself['e1']
            elif 'e2' in newself.properties:
                newself.properties['e1'] = newself.properties['e2']
                del newself.properties['e2']
                del newself['e2']
            if 'edge1_effects' in newself.properties and 'edge2_effects' in newself.properties:
                e1 = newself.properties['edge1_effects']
                e2 = newself.properties['edge2_effects']
                newself.edge1_effects = newself.properties['edge1_effects'] = e2
                newself.edge2_effects = newself.properties['edge2_effects'] = e1
            elif 'edge1_effects' in newself.properties:
                newself.edge2_effects = newself.properties['edge2_effects'] = newself.properties['edge1_effects']
                del newnewself.properties['edge1_effects']
                del newself.edge1_effects
            elif 'edge2_effects' in newself.properties:
                newself.edge1_effects = newself.properties['edge1_effects'] = newself.properties['edge2_effects']
                del newself.properties['edge2_effects']
                del newself.edge2_effects
            newself.name = '-'+newself.name
            return newself
        else:
            return self

    def write(self):
        wholestring=''
        string = self.name+': '+self.type
        for key, value in self.properties.iteritems():
            if not key is 'name' and not key is 'type' and not key is 'commandtype':
                tmpstring = ', '+key+' = '+str(value)
                if len(string+tmpstring) > 78:
                    wholestring+=string+', &\n'
                    string=''
                string+= tmpstring
        wholestring+=string+';\n'
        return wholestring

class elegantLine(object):

    def __init__(self, name=None, line=[]):
        super(elegantLine, self).__init__()
        if name == None:
            raise NameError('Line does not have a name')
        self.name = name
        self.commandtype = 'line'
        self.line = line

    def __mul__(self, other):
        return [self for x in range(other)]

    def __rmul__(self, other):
        return [self for x in range(other)]

    def writeElements(self):
        unique = reduce(lambda l, x: l if x in l else l+[x], self.line, [])
        return [element.write() for element in unique]

    def getElements(self):
        unique = reduce(lambda l, x: l if x in l else l+[x], self.line, [])
        return unique

    def expandLine(self, line=None):
        if line == None:
            line = self.line
        try:
            self.lineNames
        except AttributeError:
            self.lineNames = []
        if isinstance(line,(list, tuple)):
            for element in line:
                self.expandLine(element)
        else:
            if isinstance(line,str):
                self.lineNames.append(line)
            else:
                self.lineNames.append(line)
        return self.lineNames

    def write(self):
        wholestring=''
        string = self.name+': Line=('
        self.lineNames = []
        self.expandLine(self.line)
        for element in self.lineNames:
            if string[-1] == '(':
                if isinstance(element,str):
                    tmpstring = element
                else:
                    tmpstring = getattr(element,'name')
            else:
                if isinstance(element,str):
                    tmpstring = ', '+element
                else:
                    tmpstring = ', '+getattr(element,'name')
            if len(string+tmpstring) > 78:
                wholestring+=string+', &\n'
                string=''
                string+=tmpstring[2::]
            else:
                string+= tmpstring
        wholestring+=string+');\n'
        return wholestring

class elegantInterpret(object):

    def __init__(self, parent=None):
        self.lattice = elegantLattice()

    def readElegantFile(self,file):
        self.f = open(file,'r')
        line = self.readLine(self.f)
        while line != '':
            line = self.readLine(self.f)
        return self.lattice

    def readLine(self,f):
        element = ''
        tmpstring = f.readline()
        while '&' in tmpstring:
            element+= tmpstring
            tmpstring = f.readline()
        element+= tmpstring
        string = element.replace('&','').replace('\n','').replace(';','')
        if '!' in string:
            pos = string.index('!')
            string = string[:pos].strip()
        if not 'line' in string.lower():
            try:
                pos = string.index(':')
                name = string[:pos].strip().lower()
                keywords = string[(pos+1):].split(',')
                commandtype = keywords[0].strip().lower()
                if commandtype in elementkeywords:
                    kwargs = {}
                    kwargs['type'] = commandtype.strip().lower()
                    kwargs['name'] = name.strip().lower()
                    for kw in keywords[1:]:
                        kwname = kw.split('=')[0].strip()
                        kwvalue = kw.split('=')[1].strip()
                        if kwname.lower() in elementkeywords[commandtype]:
                            kwargs[kwname.lower()] = kwvalue
                    elem = self.lattice.addElement(**kwargs)
            except:
                pass
        else:
            try:
                pos = string.index(':')
                name = string[:pos]
                pos1 = string.index('(')
                pos2 = string.index(')')
                lines = [x.strip().lower() for x in string[(pos1+1):pos2].split(',')]
                # print 'lines = ', lines
                self.lattice.addLine(name=name.lower(),line=lines)
                print 'added line ', name.lower()
            except:
                pass
        return element
