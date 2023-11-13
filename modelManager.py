import os

def isH5Model(filename):
    # Check if the file is an H5 file based on its extension
    _, ext = os.path.splitext(filename)
    return ext.lower() == '.h5'


def getAvailableModels(hashedUserName):
    models = []
    directory = './models/' + hashedUserName

    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)) and isH5Model(filename):
                models.append(filename)

    return models


def storeUserModel(hashedUserName, modelData, modelName):
    directory = './models/' + hashedUserName
    if not os.path.exists(directory):
        # create the directory if it doesn't already exist
        os.makedirs(directory)
    
    try:
        with open(directory + '/' + modelName, 'w') as file:
            file.write(modelData)
    except IOError as e:
        print(f"An error occurred while writing modelData to file: {e}")