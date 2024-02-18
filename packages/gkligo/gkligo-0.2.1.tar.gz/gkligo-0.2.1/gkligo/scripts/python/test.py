import glob

def getFiles(regex, directory):

    fileList = glob.glob(directory + '/**/' + regex, recursive=True)

    fileList.sort()

    return fileList

if __name__ == '__main__':
    files = getFiles('*.yaml', '/tmp')
    for file in files:
        print(file)
