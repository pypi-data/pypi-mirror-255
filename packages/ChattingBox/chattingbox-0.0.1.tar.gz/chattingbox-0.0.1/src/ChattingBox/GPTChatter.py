import openai
import os
import sys
from ModelChatter import chatterbox

__validmodels = ["gpt-3.5-turbo", "gpt-4", "gpt-4-32k", ]
__validoperators = ["system", "user", "assistant", ] #all valid operators
AIOPERATOR = __validoperators[2] #the operator for the AI specifically
#possible TODO: allow this to be changed somehow?  Likely unneeded

DEBUG_OUTPUT = False

DEFAULT_KEY_NAME = "default"
#files are stored in the local folder GPT, in openai.apikeys
KEYS_LOCATION = os.path.join(os.path.dirname(sys.modules[__name__].__file__), "GPT", "openAI.apikeys")

def getValidModels():
    return __validmodels

def validateModelName(name):
    return name in __validmodels

def getValidOperators():
    return __validoperators

def __validateLine(line):
    #if the line is a string, and is formatted as "[system|user|assistant]:[Message]", then it is valid!
    if(not isinstance(line, str)):
        return False
    tokens = line.split(":", 1)
    if (not (tokens[0].strip().lower() in __validoperators and tokens[1].strip())):
        return False
    return True

def validateContext(context, singleLine = False):
    #this function ensures that the context given is valid
    if singleLine or isinstance(context, str):
        return __validateLine(context)
    #multi-line contexts must both be lists of strings, and have every line validate correctly.
    if not isinstance(context, list):
        return False
    for line in context:
        if not __validateLine(line):
            return False
    return True

def __saveKeys(keyMap):
    if not keyMap:
        return
    with open(KEYS_LOCATION, 'w') as keyFile:
        keystring = keyMap.get(DEFAULT_KEY_NAME, default="")
        for key in keyMap:
            if(key == DEFAULT_KEY_NAME):
                continue
            keystring = keystring + '\n' + key + ":" + keyMap[key]
        keyFile.write(keystring)

class GptBox(chatterbox):
    def __checkForKey(self):
        keyNames = []
        with open(KEYS_LOCATION) as keyFile:
            for keyLine in keyFile:
                if(not keyLine.strip()):
                    continue
                #check if the line even exists!
                #TODO: See if you can validate the key somehow, right now it just trusts it.
                #TODO: Use OS environ vars to load default keys
                name = DEFAULT_KEY_NAME
                keyTokens = keyLine.strip().split(":")
                if(len(keyTokens) > 2):
                    print("More than two tokens found on a line in the keys file, skipping...", file=sys.stderr)
                    continue
                if(len(keyTokens) == 2 and keyTokens[0].strip()):
                    #this one has a name, use it!
                    name = keyTokens[0].strip()
                if(keyTokens[-1].strip()):
                    keyNames.append(name)
                    self.__keys[name] = keyTokens[-1]
        if(not self.__keys):
            print("Warning, no keys found.  Ensure keys are set before using!", file=sys.stderr)
        else:
            #set ourselves to the key default if it exists, otherwise whichever was first
            if DEFAULT_KEY_NAME in keyNames:
                self.__activeKey = DEFAULT_KEY_NAME
            else:
                self.__activeKey = keyNames[0]
        
    def __init__(self, *, model_type = "gpt-3.5-turbo", context = "", key=None, keyName=None, saveKeys=True):
        if(not validateModelName(model_type)):
            #check if the user wrote something like "gpt4"
            if(model_type.lower() == "gpt4"):
                model_type = "gpt-4"
            elif(model_type.lower == "gpt3" or
                 model_type.lower == "gpt-3" or
                 model_type.lower == "gpt3.5" or
                 model_type.lower == "gpt-3.5"):
                model_type = "gpt-3.5-turbo"
            else:
                #throw an error and return, don't try to keep going
                raise Exception("Invalid model name, use getValidModels to see valid options.")
                return
        self.__aiModel = model_type
        #now initialize the settings so we can add context if present
        self.__context = []
        if(context and validateContext(context)):
            if isinstance(context, str):
                self.__context = [context]
            else:
                self.__context = context
        elif(context):
            raise Exception("Context must be a list of strings.  See formatting guidelines for acceptable examples.")
        self.__keys = {}
        self.__activeKey = None
        self.__keysUpdated = False
        self.__saveKeys = saveKeys
        self.__checkForKey()
        self.__apiClient = None
        self.__initialized = False

    def addContext(self, newContext):
        if validateContext(newContext):
            if isinstance(newContext, str):
                self.__context.append(newContext)
            else:
                self.__context.extend(newContext)

    def setContext(self, newContext):
        #returns true if the context was accepted, false otherwise
        if validateContext(newContext):
            if isinstance(newContext, str):
                self.__context = [newContext]
            else:
                self.__context = newContext
            return True
        return False

    def getContext(self):
        return self.__context

    #TODO: use the environment variables to hold default keys
    def setKey(self, key, keyName, *, useKey=False):
        self.__keys[keyName] = key
        self.__keysUpdated = True
        if(useKey):
            self.activeKey = keyName

    def getKey(self, keyName=None, *, default=None):
        #if no name is supplied, get the key we are currently using
        if not keyName:
            return self.__keys.get(self.__activeKey, default)
        return self.__keys.get(keyName, default)

    def getCurrentKeyName(self):
        return self.__activeKey

    def useKey(self, keyName):
        #TODO: validate the key somehow, but currently it just accepts it if it exists at all
        #Returns true if the system successfully swapped to the key
        #Returns false if the key wasn't found
        #Note that a key MUST be set in order to fully initialize
        if self.__keys.get(keyName):
            self.__activeKey = keyName
            return True
        return False

    def initialize(self, *, key=None, context=None, noContext=False):
        #first check if the key exists
        if not self.__activeKey:
            if key:
                #if given a key here, then set it to be the default and use it
                self.__activeKey = DEFAULT_KEY_NAME
                self.__keys[DEFAULT_KEY_NAME] = key
            elif self.__keys.get(DEFAULT_KEY_NAME):
                #if a default key was added/found but somehow missed, use it here
                self.__activeKey = DEFAULT_KEY_NAME
            #the checks failed, print to stderr and return False.  Do not initialize.
            else:
                print("No keys were found!  Either give one to the initialize function or set it with setKey!", file=sys.stderr)
                return False
        #now check if the context exists or if the user provided context here
        if not self.__context:
            if noContext:
                #just let it go through without any context
                self.__context = []
            elif not self.setContext(context):
                #if this context is invalid, then we failed initialization.  State that and return.
                print("Warning!  Context is invalid!  Aborting!", file=sys.stderr)
                return False
        #Everything is now ready to begin, so wrap up and return
        #We set the base context used by the system, as well as the key used
        self.__transcript = self.__context
        self.__apiClient = openai.OpenAI(api_key = self.getKey())
        self.__initialized = True
        return True
                
    def __setTranscript(self, script):
        if validateContext(script):
            if isinstance(script, str):
                self.__transcript = [script]
            else:
                self.__transcript = script
            return True
        return False

    def isInitialized(self):
        return self.__initialized

    def __transcriptToAPI(self):
        #take the transcript, and turn it into a form usable by the API
        #the API expects a list of dicts, each having a "role" and "content" key
        apiDictList = []
        for line in self.__transcript:
            parts = line.split(":")
            apiDict = {"role":parts[0].strip(), "content":parts[1].strip()}
            if DEBUG_OUTPUT:
                print(apiDict)
            apiDictList.append(apiDict)
        return apiDictList

    def __APIToTranscript(self, response):
        #given the following response, add it to the transcript
        newResponse = AIOPERATOR + ":" + response
        return self.prompt(newResponse)

    def respond(self):
        if not self.__initialized:
            print("Error, not initialized, use initialize() first!", file=sys.stderr)
            return None
        #get a response via the API
        response = self.__apiClient.chat.completions.create(
                model=self.__aiModel,
                messages = self.__transcriptToAPI()
                ).choices[0].message
        #add the response to the transcript
        self.__APIToTranscript(response.content)
        #return the response
        return response

    def prompt(self, text):
        if not self.__initialized:
            print("Error, not initialized, use initialize() first!", file=sys.stderr)
        if not validateContext(text):
            return False
        if isinstance(text, str):
            self.__transcript.append(text)
        else: #for validateContext to pass, it must be either a list of strings or a string
            self.__transcript.extend(text)
        return True

    def getTranscript(self):
        if not self.__initialized:
            print("Error, transcript is made during initialization, use initialize() first!", file=sys.stderr)
            return None
        return self.__transcript
    

    def updateTranscript(self, newTranscript):
        if not self.__initialized:
            print("Error, the transcript value is made during initialization, use initialize() first!", file=sys.stderr)
        return self.__setTranscript(self, newTranscript)

