import os
import time
from datetime import datetime, timedelta

def main():
    # Clear the terminal
    os.system("clear")

    # Print header
    print("-------------------------------------------------------------")
    print("The Program has started")
    print("-------------------------------------------------------------")
    print("")

    mode = input("do you want to create a new file (c) or move one to active (m):\n")

    if(mode == "c"):
        create_new()
    elif(mode == "m"):
        move()
    else:
        print("")
        print("no valid selection")
        time.sleep(2)

        main()

def create_new():
    # Clear the terminal
    os.system("clear")
    
    path = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/possible_andachten"

    print("-------------------------------------------------------------")
    print("")
    readtime = input("Wiviele minuten ist die Lese-Dauer (m):\n")
    print("")
    print("-------------------------------------------------------------")

    # Explain to user how to enter
    print("")
    print("In Version 2 kannst du nun die ganze Andacht auf einmal eingeben.")
    print("Dies jedoch erfordert eine ganz besondere Formatierung:")
    print("")
    print("Titel: [...]")
    print("")
    print("Text: [...]")
    print("")
    print("Andacht:")
    print("")
    print("[...]")
    print("")
    print("Gebet:")
    print("")
    print("[...]")
    print("")
    print("-------------------------------------------------------------")

    # Asks user for andacht in a given format
    print("")
    print("Now please enter the entire Andacht in the Provided Format:")
    
    # Pick out title & throw away empty line after
    prefix = "Titel: "
    title = input("")[len(prefix):]
    trash = input("")

    # Pick out Text & throw away empty line after
    prefix = "Text: "
    text = input("")[len(prefix):]
    trash = input("")
    trash = input("")
    trash = input("")

    content = []
    counter = 0

    line = input("")

    while(counter < 2):
        if(line != ""):
            content.append(line + "<br><br>")
            counter = 0
        else:
            counter += 1

        line = input("")

    print("")
    print("-------------------------------------------------------------")
    print("")

    andacht = ""
    prayer = ""

    switch = False

    for x in content:
        if (x == "Gebet:<br><br>"):
            switch = True
        elif(switch == False):
            andacht = andacht + x
        elif(switch == True):
            prayer = prayer + x

    andacht = andacht.strip().strip("<br><br>")
    prayer = prayer.strip().strip("<br><br>")

    print("Andacht und Gebet extrahiert")
    print("")
    print("-------------------------------------------------------------")
    print("")
    print("Gibt es einen besonderen Author? Eine leere ausgabe wird mit \"DailyAndacht Team\" ersetzt:")
    author = input("")

    createfile(path, title, readtime, text, andacht, prayer, author)

def createfile(path, title, readtime, text, andacht, prayer, author):    
    filename = title + ".csv"

    seperator = "*DailyAndachtSeperationTag*"

    if not os.path.exists(path):
        print("The required path (" + path + ") does not exist,\nthis indicates that there are errors. We recommend exiting the program.\n If you want you can choose so set an alternate path for the file to be stored into.")
        exit = input("Do you want to exit the program? y/n:\n")

        if(exit != "n"):
            exit()
        else:
            path = input("please enter the new path:\n")
            print("")
        
    if os.path.isfile(path + '/' + filename):
        proceede = input(f"The file for the {filename} already exists in the given path {path}.\nDo you want to change the date for the Andacht, replace the file or exit the Program?\nChange Date = c\nReplace File = r\nExit Program = e\n")
        
        if(proceede == "c"):
            filename = input("What is the Andacht supposed to be called:\n")
            filename = filename + ".csv"
            print("")
        elif(proceede == "r"):
            os.remove(path + '/' + filename)
        else:
            exit()

    date_formatted = "DD.MM.YYYY"
    author_formatted = author
    if(author == ""):
        author_formatted = "DailyAndacht Team"
    
    content = title + seperator + readtime + seperator + text + seperator + andacht + seperator + prayer + seperator + date_formatted + seperator + author_formatted
    
    file_path = os.path.join(path, filename)

    with open(file_path, 'w') as csv_file:
        csv_file.write(content)

    print("-------------------------------------------------------------")
    print("")
    print("File has successfully been created")
    print("")
    another = input("Do you want to continue? y/n\n")

    if(another == "y"):
        main()
    else:
        print("")
        print("-------------------------------------------------------------")
        print("")
        print("Vielen Dank, noch einen Schönen Tag!")
        print("Auf Wiedersehen!")
        print("")
        print("-------------------------------------------------------------")

        time.sleep(3)
        os.system("clear")
        quit()
    
def move():
    print("implement")

main()