import os
import time
from datetime import datetime, timedelta

def main():
    # Clear the terminal
    os.system("clear")

    # initialize the path and possiblepath
    path = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/andachten"
    possiblepath = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/possible_andachten"

    # Print header
    print("-------------------------------------------------------------")
    print("The Program has started")
    print("-------------------------------------------------------------")
    print("")

    mode = input("do you want to create a new file (c) or move one to active (m):\n")

    if(mode == "c"):
        create_new(possiblepath)
    elif(mode == "m"):
        move(path, possiblepath)
    else:
        print("")
        print("no valid selection")
        time.sleep(2)

        main()

def create_new(possiblepath):
    # Clear the terminal
    os.system("clear")

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

    createfile(possiblepath, title, readtime, text, andacht, prayer, author)

def createfile(possiblepath, title, readtime, text, andacht, prayer, author):    
    filename = title + ".csv"

    seperator = "*DailyAndachtSeperationTag*"

    if not os.possiblepath.exists(possiblepath):
        print("The required possiblepath (" + possiblepath + ") does not exist,\nthis indicates that there are errors. We recommend exiting the program.\n If you want you can choose so set an alternate possiblepath for the file to be stored into.")
        exit = input("Do you want to exit the program? y/n:\n")

        if(exit != "n"):
            exit()
        else:
            possiblepath = input("please enter the new possiblepath:\n")
            print("")
        
    if os.possiblepath.isfile(possiblepath + '/' + filename):
        proceede = input(f"The file for the {filename} already exists in the given possiblepath {possiblepath}.\nDo you want to change the date for the Andacht, replace the file or exit the Program?\nChange Date = c\nReplace File = r\nExit Program = e\n")
        
        if(proceede == "c"):
            filename = input("What is the Andacht supposed to be called:\n")
            filename = filename + ".csv"
            print("")
        elif(proceede == "r"):
            os.remove(possiblepath + '/' + filename)
        else:
            exit()

    date_formatted = "DD.MM.YYYY"
    author_formatted = author
    if(author == ""):
        author_formatted = "DailyAndacht Team"
    
    content = title + seperator + readtime + seperator + text + seperator + andacht + seperator + prayer + seperator + date_formatted + seperator + author_formatted
    
    file_possiblepath = os.possiblepath.join(possiblepath, filename)

    with open(file_possiblepath, 'w') as csv_file:
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
    
def move(path, possiblepath):
    # Clears the terminal
    os.system("clear")

    # Print the Header with all the possible Andachdachten
    print("-------------------------------------------------------------")
    print("")
    print("The Following Andachten are in the Possible Folder and not jet active:")
    print("")

    # Get all file names in the directory
    directory = os.listdir(possiblepath)
    files = []
    count = 0

    # Filter out non-csv files and print Filenames
    for file in directory:
        if file.endswith(".csv"):
            try:
                # Store and display Filenames with the appropriate index
                files.append(file)
                print(str(count) + ": " + file)

                count = count + 1
            except ValueError:
                pass

    print("")
    print("-------------------------------------------------------------")
    print("")
    
    # Let the user choose a file
    chosenfile = input("Please enter the number of the required file:\n")

    print("")
    print("-------------------------------------------------------------")
    print("")
    
    # ask user for validation
    checker = input("You have chosen:\n" + files[int(chosenfile)] + "\nis that correct? (y/n)\n")

    if(checker == "y"):
        # Onitialize Varbiables
        filename = possiblepath + "/" + files[int(chosenfile)]
        values = []
        seperator = "*DailyAndachtSeperationTag*"

        # Store the values
        with open(filename, 'r') as csv_file:
            values = csv_file.readline().strip()

        # Clears the Terminal
        os.system("clear")

        print("-------------------------------------------------------------")
        print("")
        modeselector = input("Do you want to add the files missing details manually?: (y/n)\n")

        if(modeselector == "n"):
            if not os.path.exists(path):
                print("The required path for the active Andachten (" + path + ") does not exist,\nthis indicates that there are errors. We recommend exiting the program.\n If you want you can choose so set an alternate path for the file to be stored into.")
                exit = input("Do you want to exit the program? y/n:\n")

                if(exit != "n"):
                    exit()
                else:
                    path = input("please enter the new path:\n")
                    print("")

            # Get all file names in the directory
            files = os.listdir(path)

            # Filter out non-csv files and convert file names to dates
            dates = []
            for file in files:
                if file.endswith(".csv"):
                    try:
                        date = datetime.strptime(file[:-4], "%Y%m%d")
                        dates.append(date)
                    except ValueError:
                        pass

            # Find the latest date
            latest_date = max(dates)

            # Add one day to the latest date
            next_date = latest_date + timedelta(days=1)

            # Convert the next date back to a string in YYYYMMDD format
            date = next_date.strftime("%Y%m%d")

            # Convert the next date to a string in DD.MM.YYYY format
            date_formatted = date[6:] + "." + date[4:6] + "." + date[:4]

            # Update the Date in the file
            values[5] = date_formatted
            newfilename = path + date + ".csv"
            content = values[1] + seperator + values[2] + seperator + values[3] + seperator + values[4] + seperator + values[5] + seperator + values[6]

            # Create new file
            with open(newfilename, 'w') as csv_file:
                csv_file.write(content)

            # Clear the terminal
            os.system("clear")

            print("-------------------------------------------------------------")
            print("")
            print("The new File has successfully been created as " + date + ".csv")
            print("")
            print("-------------------------------------------------------------")

            time.sleep(1)

            print("-------------------------------------------------------------")
            print("")
            print("The old File has successfully been deleted")
            print("")
            print("-------------------------------------------------------------")

            time.sleep(1)

            # Clear the terminal
            os.system("clear")

            print("-------------------------------------------------------------")
            print("")
            again = input("Do you want to keep working?: (y/n)")

            if(again == "y"):
                main()
            else:
                #Clear the Terminal
                os.system("clear")

                print("-------------------------------------------------------------")
                print("")
                print("Vielen Dank, noch einen Schönen Tag!")
                print("Auf Wiedersehen!")
                print("")
                print("-------------------------------------------------------------")

                time.sleep(3)
                os.system("clear")
                quit()
        else:
            print("Implement")
    else:
        move(path, possiblepath)
    

main()