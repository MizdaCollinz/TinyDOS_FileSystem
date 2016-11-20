import sys
import volume
import drive

#Written by Benjamin Collins - UPI: BCOL602

class TinyDOS:
    def startUp(self):
        print("TinyDOS has started, please enter a command")
        self.volume = None
        while True:
            command = input("> ")
            list = command.split(" ",2)

            if list[0] == "append":
                if self.checkVolumeFail(): return

                if len(list) != 3:
                    print(len(list))
                    print("Incorrect arguments, please provide a full qualified filename and a string of data")
                else:
                    self.volume.appendToFile(list[1],list[2])
            elif list[0] == "quit":
                if self.volume != None:
                    self.volume.drive.disconnect()
                sys.exit()
            elif list[0] == "format":
                if len(list) != 2:
                    print("Incorrect arguments, please provide a volume name")
                else:
                    self.format(list[1])
            elif list[0] == "reconnect":
                if len(list) != 2:
                    print("Incorrect arguments, please provide a volume name")
                else:
                    self.reconnect(list[1])
            elif list[0] == "ls":
                if self.checkVolumeFail(): return
                if len(list) != 2:
                    print("Incorrect ls arguments, please provide a fully qualified pathname")
                else:
                    self.volume.ls(list[1])
            elif list[0] == "mkfile":
                if self.checkVolumeFail(): return
                if len(list) != 2:
                    print("Incorrect mkfile arguments, please provide a fully qualified filename")
                else:
                    self.volume.mkfile(list[1])
            elif list[0] == "mkdir":
                if self.checkVolumeFail(): return
                if len(list) != 2:
                    print("Incorrect mkdir arguments, please provide a fully qualified dir name")
                else:
                    self.volume.mkdir(list[1])
            elif list[0] == "print":

                if self.checkVolumeFail(): return
                if len(list) != 2:
                    print("Incorrect print arguments, please provide a fully qualified filename")
                else:
                    self.volume.print(list[1])

            elif list[0] == "delfile":
                if self.checkVolumeFail(): return

                if len(list) != 2:
                    print("Incorrect delfile arguments, please provide a fully qualified filename")
                else:
                    self.volume.delFile(list[1])
            elif list[0] == "deldir":
                if self.checkVolumeFail(): return

                if len(list) != 2:
                    print("Incorrect deldir arguments, please provide a fully qualified dir name")
                else:
                    print("Deleting "+ list[1])
                    self.volume.delDir(list[1])

    def format(self,filename):
        self.volume = volume.Volume(filename)
        self.volume.format()

    def reconnect(self,filename):
        self.volume = volume.Volume(filename)
        self.volume.reconnect()

    def checkVolumeFail(self):
        if self.volume == None:
            print("Please format or connect a drive first")
            return True
if __name__ == '__main__':
    tinyDOS = TinyDOS()
    tinyDOS.startUp()
