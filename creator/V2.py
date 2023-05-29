import os
import time
from datetime import datetime, timedelta

def main(path):
    # Clear the terminal
    os.system("clear")

    # Print header
    print("-------------------------------------------------------------")
    print("The Program has started")
    print("-------------------------------------------------------------")
    
    # Asks user for path if no path was set previously
    if(path == "nopath"):
        print("")
        sequential = input("Möchten sie den Pfad und das Datum manuell eingeben? (y/n):\n")

        if(sequential == "y"):
            print("")
            path = input("Bitte geben sie den pfad ein unter dem die datei gespeichert werden soll (no need to end with /):\n")

            if(path == "dev"):
                path = "./"
    
            # Asks user for date to be published
            print("")
            date = input("Für wann ist die Andacht (YYYYMMDD):\n")
        else:
            path = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/andachten"

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

    createfile(path, date, title, readtime, text, andacht, prayer, author)

def createfile(path, date, title, readtime, text, andacht, prayer, author):    
    filename = date + ".csv"

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
            date = input("Für wann ist die Andacht (YYYYMMDD):\n")
            filename = date + ".csv"
            print("")
        elif(proceede == "r"):
            os.remove(path + '/' + filename)
        else:
            exit()

    date_formatted = date[6:] + "." + date[4:6] + "." + date[:4]
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
    another = input("Möchtens sie eine weitere Andacht in dem gleichen Ordner erstellen? y/n\n")

    if(another == "y"):
        main(path)
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

main("nopath")