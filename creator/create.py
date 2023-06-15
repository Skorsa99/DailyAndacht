import os
import time
from datetime import datetime, timedelta
import math

from PIL import Image, ImageDraw, ImageFont
import textwrap

# V_3.0

def main():
    # Clear the terminal
    os.system("clear")

    # Print header
    print("-------------------------------------------------------------")
    print("The Program has started")
    print("-------------------------------------------------------------")
    
    print("")
    
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
    print("-------------------------------------------------------------")

    # Explain to user how to enter
    print("")
    print("In Version 3 kannst du nun die ganze Andacht auf einmal eingeben,")
    print("ohne dass weitere eingaben Erfordert sind.")
    print("")
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

    readtime = calculatereadtime(title, andacht, prayer)

    print("-------------------------------------------------------------")
    print("")
    print("Gibt es einen besonderen Author? Eine leere ausgabe wird mit \"DailyAndacht Team\" ersetzt:")
    author = input("")

    createfile(path, date, title, readtime, text, andacht, prayer, author)

def calculatereadtime(title, andacht, prayer):
    content = title + " " + andacht.replace("<br><br>", " ") + " " + andacht.replace("<br><br>", " ")
    words = content.split(" ")
    wordcount = len(words)
    wordsperminute = 200
    readtime = 0

    exacttime = wordcount/wordsperminute
    readtime = math.floor(exacttime) if exacttime % 1 < 0.4 else math.ceil(exacttime)

    return str(readtime)

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

    createimage(title, text, date_formatted, date)

    print("-------------------------------------------------------------")
    print("")
    print("File has successfully been created")
    print("")
    another = input("Möchtens sie eine weitere Andacht in dem gleichen Ordner erstellen? y/n\n")

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

def createimage(title, text, date_formatted, date):
    # Create a new image with the desired dimensions and color
    image = Image.new('RGB', (1080, 1920), '#EFEFEF')
    draw = ImageDraw.Draw(image)

    # Open the logo image and paste it at the top, centered and with a top margin of 50px
    logoimagepath = "/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/src/Logo.jpeg"  # replace with your logo image path
    logosize = 400
    logo = Image.open(logoimagepath).resize((logosize, logosize))
    logo_position = ((image.width - logosize) // 2, 100)  # centering the resized logo and adding 50px top margin
    image.paste(logo, logo_position)


    # Set the fonts. You may need to adjust the paths to the fonts, sizes, and styles according to your needs
    font_big = ImageFont.truetype('/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc', 80)  # for macOS, the default Arial font path
    font_small = ImageFont.truetype('/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc', 35)  # adjust the size as needed

    # Define the text and its properties
    text_big = title
    text_small1 = text
    text_small2 = date_formatted

    headerwords = text_big.split(" ")
    headerlines = [""] * 20
    templine = ""
    linelength = 19
    linecounter = 0

    for word in headerwords:
        if(templine != ""):
            if(len(templine) + len(word) <= linelength):
                templine = templine + " " + word
            else:
                headerlines[linecounter] = templine
                linecounter = linecounter + 1
                templine = word
        else:
            templine = templine + " " + word
    
    headerlines[linecounter] = templine
    linecounter = linecounter + 1

    # Calculate text sizes using 'textbox' function
    width_big1, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[0], font=font_big)[2:]
    width_big2, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[1], font=font_big)[2:]
    width_big3, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[2], font=font_big)[2:]
    width_big4, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[3], font=font_big)[2:]
    width_big5, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[4], font=font_big)[2:]
    width_big6, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[5], font=font_big)[2:]
    width_big7, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[6], font=font_big)[2:]
    width_big8, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[7], font=font_big)[2:]
    width_big9, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[8], font=font_big)[2:]
    width_big10, height_big = draw.textbbox((0, 0, image.width, image.height), headerlines[9], font=font_big)[2:]
    width_small1, height_small1 = draw.textbbox((0, 0, image.width, image.height), text_small1, font=font_small)[2:]
    width_small2, height_small2 = draw.textbbox((0, 0, image.width, image.height), text_small2, font=font_small)[2:]

    # Draw the text on the image. You may need to adjust the positions according to your needs
    padding = 50
    spacer = 10

    draw.text(((1080 - width_big1) / 2, logo_position[1] + logosize + padding * 4), headerlines[0], fill="black", font=font_big)
    draw.text(((1080 - width_big2) / 2, logo_position[1] + logosize + padding * 5 + spacer), headerlines[1], fill="black", font=font_big)
    draw.text(((1080 - width_big3) / 2, logo_position[1] + logosize + padding * 6 + spacer * 2), headerlines[2], fill="black", font=font_big)
    draw.text(((1080 - width_big4) / 2, logo_position[1] + logosize + padding * 7 + spacer * 3), headerlines[3], fill="black", font=font_big)
    draw.text(((1080 - width_big5) / 2, logo_position[1] + logosize + padding * 8 + spacer * 4), headerlines[4], fill="black", font=font_big) 
    draw.text(((1080 - width_big6) / 2, logo_position[1] + logosize + padding * 9 + spacer * 5), headerlines[5], fill="black", font=font_big) 
    draw.text(((1080 - width_big7) / 2, logo_position[1] + logosize + padding * 10 + spacer * 6), headerlines[6], fill="black", font=font_big) 
    draw.text(((1080 - width_big8) / 2, logo_position[1] + logosize + padding * 11 + spacer * 7), headerlines[7], fill="black", font=font_big) 
    draw.text(((1080 - width_big9) / 2, logo_position[1] + logosize + padding * 12 + spacer * 8), headerlines[8], fill="black", font=font_big) 
    draw.text(((1080 - width_big10) / 2, logo_position[1] + logosize + padding * 13 + spacer * 9), headerlines[9], fill="black", font=font_big)

    draw.text(((1080 - width_small1) / 2, image.height - height_small2 - 2 * padding * 2), text_small1, fill="black", font=font_small)
    draw.text(((1080 - width_small2) / 2, image.height - height_small2 - padding * 2), text_small2, fill="black", font=font_small)

    # Save the image to the disk
    image.save('/Users/samuelskorsetz/Documents/Freizeit/Coding/DailyAndacht/social/images/' + date + '.jpg', 'JPEG')

main()