import os
import time
from datetime import datetime, timedelta
import csv
import getpass

def main():
    # Clear the terminal
    os.system("clear")

    # Print header
    print("-------------------------------------------------------------")
    print("The Program has started")
    print("-------------------------------------------------------------")
    print("")

    # have the user selct a mode
    mode = input("Which mode do you want to enter?:\nm = Manual Mode\nd = Date Mode\na = Display all Andachten\n")

    if(mode == "m"):
        print("")
        print("Manual Mode has not been implemented yet")
    elif(mode == "d"):
        dateMode()
    elif(mode == "a"):
        displayMode()
    else:
        print("")
        print("No valid mode detected")
        main()
        

def dateMode():
    # Clear the terminal
    os.system("clear")

    # query for required date
    print("-------------------------------------------------------------")
    date = input("Which Date do you want to read?: (YYYYMMDD)\n")
    print("-------------------------------------------------------------")

    path = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/andachten/" + date + ".csv"

    printout(path)

def printout(path):
    # Clear the terminal
    os.system("clear")

    data = []

    # read CSV file
    with open(path, "r") as file:
        data = file.readline().strip().split("*DailyAndachtSeperationTag*")

    # Display Data
    print("-------------------------------------------------------------")
    print("Titel: " + data[0])
    print("")
    print("Datum: " + data[5])
    print("")
    print("Lesedauer: " + data[1])
    print("")
    print("Text: " + data[2])
    print("-------------------------------------------------------------")
    print(data[3].replace("<br><br>", "\n\n"))
    print("-------------------------------------------------------------")
    print(data[4].replace("<br><br>", "\n\n"))
    print("-------------------------------------------------------------")
    print("By: " + data[6])
    print("-------------------------------------------------------------")
    print("")

    # Allow user to close the file
    finish = input("Enter \"a\" to open another, Enter anything else to close the Program:\n")

    if(finish == "a"):
        main()
    else:
        # Clear the terminal
        os.system("clear")
        quit()

def displayMode():
    # Clear the terminal
    os.system("clear")

    # query for required date
    print("-------------------------------------------------------------")
    mode = input("Do you want to enter Manual Mode?: (y/n)\n")
    print("-------------------------------------------------------------")

    path = ""

    if(mode == "y"):
        path == input("Please enter the Path you want to list:\n")
    else:
        path = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/andachten"

    # Clears the terminal
    os.system("clear")

    # Print the Header with all the possible Andachdachten
    print("-------------------------------------------------------------")
    print("")

    # Get all file names in the directory
    directory = os.listdir(path)
    files = []
    count = 0

    # Filter out non-csv files and print Filenames
    for file in directory:
        if file.endswith(".csv"):
            try:
                # Store and display Filenames with the appropriate index
                files.append(file)

                with open(path + "/" + file, "r") as currentfile:
                    data = currentfile.readline().strip().split("*DailyAndachtSeperationTag*")

                print(file.strip(".csv") + " | " + data[0])

                count = count + 1
            except ValueError:
                pass

    print("")
    print("-------------------------------------------------------------")
    print("")
    print("There are " + str(count) + " Andachten stored")
    print("")
    display = input("If you want to open one of the Andachten, you can enter the date of the Andacht to open it in the YYYYMMDD format. To exit enter \"e\":\n")

    if(display == "e"):
        # Clear the terminal
        os.system("clear")
        quit()
    else:
        printout(path + "/" + display + ".csv")

main()