#Written by Benjamin Collins - UPI: BCOL602

class directory_entry:
    def __init__(self,bitmap):
        self.blocks = []
        self.length = 0000
        for index in range(12):
            self.blocks.append("000 ")
        self.occupiedBlocks = 0
        self.type = "f:"
        self.filename = ""
        self.empty = True
        self.bitmap = bitmap
        self.directoryBlock = None
        self.isLoaded = False

    def setFilename(self,filename):
        self.filename = filename

    def setDirectory(self,name):
        self.empty = False
        self.filename = name
        self.length = 0
        self.type = "d:"
        self.directoryBlock = directoryBlock(self.bitmap,self)
        self.isLoaded = True

    def appendLength(self,length):
        self.length += length

    def claimBlock(self,blockName):
        if(self.occupiedBlocks == 12):
            print("This file already occupied 12 blocks")
            return None
        self.blocks[self.occupiedBlocks] = blockName + " "
        self.occupiedBlocks+=1

    #Convert to 512 bit directory entry string
    def toString(self): #filename must be 8 characters long, length 4 characters

        filenameString = self.filename
        filenameLength = len(filenameString)

        if filenameLength > 8:
            filenameString = "TooLong!"
        elif filenameLength < 8:
            while filenameLength < 8:
                filenameString = filenameString + " "
                filenameLength = len(filenameString)

        lengthString = str(self.length)
        while len(lengthString) < 4:
            lengthString = "0" + lengthString
        if len(lengthString) > 4:
            lengthString = "ERRR"


        outputString = self.type + filenameString + " " + lengthString + ":"

        for index in range(12):
            outputString = outputString + self.blocks[index]
        return outputString

    #Retrieve an emptry directory entry in the directory block
    def getEmptyEntry(self):
        return self.directoryBlock.getEmptyEntry()

    #Find the block containing the end of the file data
    def getLastBlock(self):
        lastBlock = 0
        for block in self.blocks:
            if (block != "000 "):
                lastBlock = block
            elif (block == "000 "):
                break
        return lastBlock

    #Convert from 64 character string to populated directory_entry file
    def fromString(self,string):
        type = string[:2]
        filename = string[2:10].strip()
        length = int(string[11:15])
        blockList = string[16:63]
        blocks = blockList.split(" ",11)

        self.type = type
        self.filename = filename
        self.length = length
        self.blocks = blocks
        if filename != "":
            self.empty = False
        if type == "d:":
            self.directoryBlock = directoryBlock(self.bitmap, self)

        for index in range(len(self.blocks)):
            if int(self.blocks[index]) != 0:
                self.occupiedBlocks += 1
            self.blocks[index] += " "


    def list(self):
        headerString = "Filename  " + "FileType   " + "Length"
        headerString2 = "--------  ---------  ------"
        if len(self.directoryBlock.directory) == 0:
            print("")
            print(headerString)
            print(headerString2)
        else:
            print("")
            print (headerString)
            print (headerString2)
            for entry in self.directoryBlock.directory:
                if entry.empty == False:
                    if entry.type == "f:":
                        type = "  File   "
                    else:
                        type = "Directory"

                    filename = entry.filename
                    while len(filename) < 8:
                        filename += " "

                    length = str(entry.length)
                    while len(length) < 4:
                        length = "0" + length
                    length = "  " + length

                    print(filename + "  " + type + "  " + length)




class directoryBlock:
    def __init__(self,bitmap,entry):
        self.directory = []
        self.bitmap = bitmap
        self.entry = entry

    def getEmptyEntry(self):

        if len(self.directory) == 0:
            self.initialiseDirectory()

        for entry in self.directory:
            if entry.empty == True:
                return entry

        if self.entry.occupiedBlocks < 12:
            #Claim new block for directory entries
            newBlock = self.bitmap.retrieveAvailableBlock()
            newBlockString = str(newBlock)
            while len(newBlockString) < 3:
                newBlockString = "0" + newBlockString
            self.entry.claimBlock(newBlockString)

            #add 8 new entries to directory
            for index in range(8):
                self.directory.append(directory_entry(self.bitmap))
            self.entry.length += 512
            return self.getEmptyEntry()
        return "none"


    def initialiseDirectory(self):
        self.entry.length = 512
        blockNumber = self.bitmap.retrieveAvailableBlock()

        lengthString = str(blockNumber)
        while len(lengthString) < 3:
            lengthString = "0" + lengthString
        self.entry.claimBlock(lengthString)

        for i in range(8):
            self.directory.append(directory_entry(self.bitmap))

    def toString(self):
        output = ""
        for i in range(len(self.directory)):
            output += self.directory[i].toString()
        return output