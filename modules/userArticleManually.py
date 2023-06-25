import re
from modules.normalizeString import normalizeString
from .sBERT import sBERT
import pyperclip
import os
from modules.finalBoss import finalBoss

def userArticleManually():
    text = ''
    normalized_text = ''
    while True:
        input("The next text in the clipboard after pressing ENTER on this program will be processed (press ENTER to continue)")
        # Gets the input text from the clipboard
        userInput = pyperclip.paste()
        # Removes hyperlinks, tags, and other junk text
        userInput = re.sub(r'<a.*?>|</a>', '', userInput)
        userInput = re.sub(r'<.*?((class|id|name|src)=".*?").*?>', '', userInput)
        userInput = re.sub(r'<.*?>', '', userInput)
        # Appends the cleaned input text to the string variable
        text += userInput.strip()
        # Prints the text that was just copied to the variable
        print("Text copied to variable:\n", text)
        # Checks if the user wants to add more text or stop
        while True:
            userChoice = input('Do you want to add more text? (y/n): ')
            if userChoice.lower() == 'n' or userChoice.lower() == 'y':
                break
            os.system('cls')
            print("Invalid input. Please enter 'y' or 'n'.")
        if userChoice.lower() == 'n':
            break
        # If the user wants to add more text, add a space and ask for the next paste
        print("Please copy the next text to the clipboard to pass it to the program")
        text += ' '

    # Normalizes the final text
    normalized_text = normalizeString(text)
    os.system('cls')
    print("This is the normalized user string:\n")
    print(normalized_text)
    input("\n Press Enter to continue")

    finalBoss(text, normalized_text)
   
    return