import drive
import directory_entry

#Written by Benjamin Collins - UPI: BCOL602

class Volume:
    def __init__(self,name):
        self.name = name
        self.bitmap = bitmap()
        self.rootDirectory = []

    #Create or reset the drive file
    def format(self):
        self.drive = drive.Drive(self.name)
        self.drive.format()
        for i in range(6):
            self.rootDirectory.append(directory_entry.directory_entry(self.bitmap))

        self.bitmap.retrieveAvailableBlock()
        self.drive.write_block(0,self.toString())

    def reconnect(self):
        self.drive = drive.Drive(self.name)
        self.drive.reconnect()
        volumedata = self.drive.read_block(0)

        bitmapString = volumedata[:128]
        entryString = volumedata[128:512]

        for i in range(6):

            entry = entryString[:64]
            entryString = entryString[64:]
            directoryEntry = directory_entry.directory_entry(self.bitmap)
            directoryEntry.fromString(entry)
            self.rootDirectory.append(directoryEntry)
        self.bitmap = bitmap()
        self.bitmap.fromString(bitmapString)

    #Print the volume out as a 512 character string
    def toString(self):
        output = self.bitmap.toString()
        for i in range(6):
            output+= self.rootDirectory[i].toString()
        return output

    #Create a file at the specified location
    def mkfile(self,filename):

        path = filename.split("/",-1)
        (prevDirectory,theDirectory) = self.findDirectory(filename)

        newFile = theDirectory.getEmptyEntry()
        if(newFile == "none"):
            print("No space remaining in directory")
        else:
            print ("Creating new file")
            newFile.empty = False
            newFile.filename = path[len(path)-1]

            # Write the adjusted directories to the drive, update Root and Volume information
            if theDirectory != self:
                self.printDirectory(theDirectory)
            if prevDirectory != None:
                self.printDirectory(prevDirectory)

        self.drive.write_block(0, self.toString())

    #Create a new directory
    def mkdir(self,dirname):

        path = dirname.split("/",-1)
        (prevDirectory, theDirectory) = self.findDirectory(dirname)


        newDir = theDirectory.getEmptyEntry()

        if(newDir == "none"):
            print("No space remaining in root directory")
        else:
            print ("Creating new dir")
            newDir.setDirectory(path[len(path)-1])

            #Write the adjusted directories to the drive, update Root and Volume information
            if theDirectory != self:
                self.printDirectory(theDirectory)
            if prevDirectory != None:
                self.printDirectory(prevDirectory)

            self.drive.write_block(0, self.toString())

    #Find an empty entry in the root directory
    def getEmptyEntry(self):

        for entry in self.rootDirectory:
            if entry.empty == True:
                return entry

        return "none"

    #Write provided to data to a given filepath
    def appendToFile(self,filepath,data):
        path = filepath.split("/",-1)
        (prevDirectory, theDirectory) = self.findDirectory(filepath)

        fileName = path[len(path) - 1]
        appendEntry = None
        if(theDirectory == self):
            for entry in self.rootDirectory:
                if entry.filename == fileName and entry.type == "f:":
                    appendEntry = entry
                    break

        else:
            for entry in theDirectory.directoryBlock.directory:
                if entry.filename == fileName:
                    appendEntry = entry
                    break
        if appendEntry == None:
            print("File not found in specified directory")
            return
        lastBlock = appendEntry.getLastBlock()

        if lastBlock == 0:
            newBlock = self.bitmap.retrieveAvailableBlock()
            appendEntry.claimBlock(self.padBlockName(newBlock))
            lastBlock = newBlock

        #Cut quotation marks and whitespace from content
        if data.startswith('"') and data.endswith('"'):
            newContent = data[1:-1]
        else:
            newContent = data

        if appendEntry.length + len(newContent) > (512*12):
            print("File will exceed maximum length")
            return
        oldLength = appendEntry.length
        appendEntry.appendLength(len(newContent))

        #Retrieve latest existing block of file
        content = self.drive.read_block(int(lastBlock))

        content = content[:oldLength] #Trim down to pure content
        content += newContent


        blocksNeeded = len(content)/512
        #When the new content overflows into multiple blocks
        if blocksNeeded > 1:
            contentList = []
            while(len(content)>512):
                contentList.append(content[0:512])
                content = content[512:]
            contentList.append(content)
            #All content now present in max 512 length string, last item confirmed to be 512 by padding
            contentList[-1] = self.padString(contentList[-1])

            for index in range(len(contentList)):
                if(index == 0):
                    self.drive.write_block(int(lastBlock),contentList[0])
                else:
                    assignBlock = self.bitmap.retrieveAvailableBlock()
                    appendEntry.claimBlock(self.padBlockName(assignBlock))
                    self.drive.write_block(assignBlock,contentList[index])
        elif blocksNeeded <= 1:
            content = self.padString(content)
            self.drive.write_block(int(lastBlock),content)
        #Always write volume information
        self.drive.write_block(0,self.toString())

        # Write the adjusted directories to the drive, update Root and Volume information
        if theDirectory != self:
            self.printDirectory(theDirectory)

    ## Print content from specified file
    def  print(self,filepath):
        printEntry = None
        path = filepath.split("/", -1)
        (prevDirectory, theDirectory) = self.findDirectory(filepath)
        fileName = path[len(path)-1]

        if (theDirectory == self):
            for entry in self.rootDirectory:
                if entry.filename == fileName and entry.type == "f:":
                    printEntry = entry
                    break

        else:
            for entry in theDirectory.directoryBlock.directory:
                if entry.filename == fileName and entry.type == "f:":
                    printEntry = entry
                    break
        if printEntry == None:
            print("File not found in specified directory")
            return
        outputString = ""
        for block in printEntry.blocks:
            if int(block) != 0:
                outputString += self.drive.read_block(int(block))
            else:
                break
        outputLength = printEntry.length
        outputString = outputString[:printEntry.length]

        print(outputString)

    ## Delete specified file and clear its claimed blocks
    def delFile(self,filepath):
        path = filepath.split("/", -1)
        (prevDirectory, theDirectory) = self.findDirectory(filepath)
        fileName = path[-1]
        delEntry = None

        if (theDirectory == self):
            for index in range(len(self.rootDirectory)):
                entry = self.rootDirectory[index]
                if entry.filename == fileName and entry.type == "f:":
                    self.rootDirectory.remove(entry)
                    self.rootDirectory.append(directory_entry.directory_entry(self.bitmap))
                    delEntry = entry
                    break
        else:
            for index in range(len(theDirectory.directoryBlock.directory)):
                entry = theDirectory.directoryBlock.directory[index]
                if entry.filename == fileName and entry.type == "f:":
                    theDirectory.directoryBlock.directory.remove(entry)
                    theDirectory.directoryBlock.directory.append(directory_entry.directory_entry(self.bitmap))
                    delEntry = entry
                    break

        emptyString = " "
        paddedEmptyString = self.padString(emptyString)

        if(delEntry == None):
            print("File not found in specified directory")
            return

        for block in delEntry.blocks:
            if int(block) != 0:
                self.drive.write_block(int(block),paddedEmptyString)
                self.bitmap.freeBlock(int(block))


        # Write the adjusted directories to the drive
        if theDirectory != self:
            self.printDirectory(theDirectory)
        # Always write volume information
        self.drive.write_block(0, self.toString())

    #Delete the specified directory if it is empty
    def delDir(self,filepath):
        path = filepath.split("/", -1)
        (prevDirectory, theDirectory) = self.findDirectory(filepath)
        fileName = path[len(path) - 1]

        delEntry = None
        emptyString = " "
        paddedEmptyString = self.padString(emptyString)

        if (theDirectory == self):
            for entry in self.rootDirectory:
                if entry.filename == fileName and entry.type == "d:":
                    delEntry = entry
                    if delEntry.length > 0:
                        for subEntry in delEntry.directoryBlock.directory:
                            if subEntry.empty == False:
                                print("An entry in the specified directory is occupied")
                                return

                    self.rootDirectory.remove(delEntry)
                    self.rootDirectory.append(directory_entry.directory_entry(self.bitmap))
                    break

        else:
            for entry in theDirectory.directoryBlock.directory:
                if entry.filename == fileName and entry.type == "d:":
                    delEntry = entry
                    if delEntry.length > 0:
                        for subEntry in delEntry.directoryBlock.directory:
                            if subEntry.empty == False:
                                print("An entry in the specified directory is occupied")
                                return
                    theDirectory.directoryBlock.directory.remove(delEntry)
                    theDirectory.directoryBlock.directory.append(directory_entry.directory_entry(self.bitmap))
                    break
        for block in delEntry.blocks:
            if int(block) != 0:
                self.drive.write_block(int(block),paddedEmptyString)
                self.bitmap.freeBlock(int(block))

       #Write the adjusted directories to the drive
        if theDirectory != self:
            self.printDirectory(theDirectory)
        # Always write volume information
        self.drive.write_block(0, self.toString())

    #Pad string to length of 512 to be written to drive
    def padString(self,string):
        if len(string) == 512:
            return string
        elif len(string) > 512:
            print("Error: Oversized string requesting padding")
            return None
        else:
            while len(string) < 512:
                string += " "
            return string

    #Pad block name of number to string with leading zeroes
    def padBlockName(self,name):
        string = str(name)
        while len(string) < 3:
            string = "0" + string
        return string

    #Response to ls command from user, list the directory contents
    def ls(self,path):
        if(path == "/"):
            self.list()
        else:
            path += "/empty"
            (prevDirectory,currentDirectory) = self.findDirectory(path)
            currentDirectory.list()

    #Root directory listing
    def list(self):
        headerString = "Filename  " + "FileType   " + "Length"
        headerString2 = "--------  ---------  ------"
        print("")
        print(headerString)
        print(headerString2)
        for entry in self.rootDirectory:
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

    #Write to the blocks storing directory entries for a particular directory
    def printDirectory(self,directory):
        blocks = directory.blocks
        count = 0 #number of blocks in use
        for block in blocks:
            if int(block) != 0:
                count += 1

        for index in range(count):
            outputstring = ""
            for index2 in range(8):
                outputstring += directory.directoryBlock.directory[index*8+index2].toString()
            self.drive.write_block(int(blocks[index]),outputstring)


    def loadDirectory(self,directory):
        if directory.isLoaded: return
        #If no blocks held, ignored
        for block in directory.blocks:
            if int(block) != 0 :
                theEntries = self.drive.read_block(int(block))
                #Retrieve the 8 entries in each block held by the directory
                for i in range(8):
                    entry = theEntries[:64]
                    theEntries = theEntries[64:]
                    directoryEntry = directory_entry.directory_entry(self.bitmap)
                    directoryEntry.fromString(entry)
                    directory.directoryBlock.directory.append(directoryEntry)
            elif int(block) == 0:
                break
        directory.isLoaded = True



    # Retrieve container directory for a specified path

    def findDirectory(self, path):
        directories = path.split("/", -1)
        if len(directories) > 2:
            for entry in self.rootDirectory:
                if entry.filename == directories[1]:
                    currentDirectory = entry  # an entry in root is returned
                    self.loadDirectory(currentDirectory)
                    break
            if len(directories) == 3:
                return (None, currentDirectory)  #
            else:
                depth = 3
                while len(directories) > depth:

                    for entry in currentDirectory.directoryBlock.directory:
                        if entry.filename == directories[depth - 1]:
                            prevDirectory = currentDirectory
                            currentDirectory = entry
                            self.loadDirectory(currentDirectory)
                            break
                    depth += 1
                return (prevDirectory, currentDirectory)
        elif len(directories) == 1:
            print("No filename provided")
            return None
        else:
            return (None, self)

#Track free and in-use blocks
class bitmap:
    def __init__(self):
        self.firstAvailable = 0
        self.map = []

        for index in range(128):
            self.map.append("-")

    def retrieveAvailableBlock(self):
        if self.map[self.firstAvailable] == "+": #Ensure block is available
            self.fetchFirstAvailable()           #Update to available block
        self.map[self.firstAvailable] = "+"
        block = self.firstAvailable
        self.firstAvailable+=1
        return block

    def fetchFirstAvailable(self): #Update to guaranteed available block
        for index in range(self.firstAvailable,128):
            if self.map[index] == "-":
                self.firstAvailable = index
                break

    def freeBlock(self,index):
        self.map[index] = "-"

        if self.firstAvailable > index:
            self.firstAvailable = index


    def toString(self):
        output = ""
        for index in range(128):
            output = output + self.map[index]
        return output

    def fromString(self,string):
        for index in range(128):
            if string[index] == "+":
                self.map[index] = "+"
        self.fetchFirstAvailable()
