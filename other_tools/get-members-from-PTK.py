import sys, re

class personMP:
    def __init__(self, lastName, firstName):
        self.firstName = firstName
        self.lastName = lasttName

def getMPtext(text):
    start = "vaalipiireittäin"
    end = "1. "
    return (text[text.index(start) :text.index(end)])
    
def getNames(text):
    allNames = re.findall(r'(^[A-Z][^,.\d]+),|([A-Z][^,.\d]+),', text, re.M)
    names = []
    for i in range(1, len(allNames), 2):
        # print(allNames[i-1][0], allNames[i][1])
        names.append((allNames[i-1][0], allNames[i][1]))
    return names

def getDistricts(text):
    # return re.findall(r"^[A-Z][a-z]+ .+ vaalipiiri", text)
    district = re.findall(r'^[A-Z].+ vaalipiiri', text, re.M)
    return district

def getProfesion(text):
    # profesions = re.findall(r'\s([äöåa-z \-]*),', text, re.M)
    profesions = re.findall(r'\s([äöåa-z \-]*),', text, re.M)
    return profesions

def getCity(text):
    # city = re.findall(r', ([^,]*)\. [F|S]\.', text, re.M)
    city = re.search(r', ([^,.]*)\.', text, re.M).group()
    return city

def getBirthdate(text):
    date = re.findall(r'(\d[\d\.,]*)', text, re.M)
    return date
    
def getParty(text):
    party = re.findall(r'\d[\.,] ([^\.]*)\.', text, re.M)
    return party

def main(filename):

    with open(filename, 'r', encoding="utf-8") as f:
        # text = f.readlines()
        text = f.read()

    text = getMPtext(text)
    
    district = getDistricts(text)
    # print (district)

    
    # for i in range(1, len(district)):
    for i in range(3,4):
        
    # start = district[0]
    # end = district[1]   
        start = district[i-1]
        end = district[i]

        oneDistrict =text[text.index(start) + len(start):text.index(end)].replace('-\n','-')

        
        
        # Divide into correct lines/paragraphs
        
        print(oneDistrict)
        names = getNames(oneDistrict)
        print(getNames(oneDistrict))
        
        lastnames = [x[0] for x in names]
        # print(lastnames)
        
        
        newLines = []
        tmpNewLine = ''
        tmpLines = oneDistrict.strip().split('\n')
        i = len(tmpLines)
        for line in tmpLines:
            line = line.split()
            i -= 1
            if (len(line) > 1 ):
                # print(line)
                s = re.sub(',$', '', line[0])
                # print ("S:", s)
                if s in lastnames :
                    # print ("YES")
                    if (len(tmpNewLine) > 0):
                        newLines.append(tmpNewLine)
                    tmpNewLine = line
                else:
                    tmpNewLine += line
                if (i == 0):
                    if s in lastnames:
                        newLines.append(line)
                    else:
                        newLines.append(tmpNewLine)
        # for l in newLines:
            # print ("NEW:", l)
            # fixedString = [' '.join(x) for x in newLines]
            # fixedString = '\n'.join(fixedString)
            
            
        # Parse the newLines
        for line in newLines:
            # print (line)
            fixedString = ' '.join(line)
        
            # print(fixedString)
            profesions = getProfesion(fixedString)
            # print (profesions)
        
            name = getNames(fixedString)
        
            city = getCity(fixedString)
        
            date = getBirthdate(fixedString)
        
            party = getParty(fixedString)
            print ((name), (profesions), (city), (date), (party))
            
        
        # print (len(lastnames), len(profesions), len(city), len(date), len(party))
    
    
    
    
if __name__ == "__main__":
    main(sys.argv[1])
