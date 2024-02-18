import sys

from ChattingBox.GPTChatter import *


#Just give it a singulat test, see if it can respond correctly when asked to perform a simple task.

myPrompt = ["system : Please respond by only writing one line containing only the name of the company that owns google."]



#A correct response is first any response, and then secondly the text should read "Alpha Bravo Charlie"

def main():

    box = GptBox(context=myPrompt)

    box.initialize()

    response = box.respond()

    print("What is the company that owns Google?")

    #print(response)
    print(response.content)

    if not response:
        print("Error!  Unable to get input from the model.  Ensure it is working correctly and has a proper connection to needed servers.", file=sys.stderr)
        return

    strResponse = str(response.content)

    
    if not strResponse.strip()[:8].casefold() == "Alphabet".casefold():
        print("response was not entirely as expected, have a human inspect the prompt!")
    else:
        print("ChatGPT got the question right!")

if __name__ == "__main__":
    main()
