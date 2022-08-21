import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# before running this script you have to populate codes.txt and key.txt

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope) # this is where your goole API keys are located (you have to populate this file with data according to your account)
client = gspread.authorize(creds)

# instead of "<spreadsheetname>" write down your sheet name
sheet = client.open("<spreadsheetname>").sheet1

#####################################################################
#                                                                   #
#                     SpeedDating Algorithm                         #
#                   created by Mikołaj Mrózek                       #
#                                                                   #
#####################################################################

# disclaimer: I know that writing majority of data to separate files is not optimal but I don't want to destroy the code
# and additionally separating data files help with statiscics and RODO regulations

#
#

# some information have to be given manually to reduce number of request send to google sheet API
columnCount = 50  # number of columns in sheet with form exit data
rowCount = 863 # number of rows in form exit data (last rows should be added and filled with fake info in sheet with form exit data)
maxScore = 43 # number of questions that are not about sex or orientation
genderIdx = 5 # column with info about gender (counting from 0)
sexPrefIdx = 6 # column with info about sexPref (counting from 0)
schoolIdx = 3 # column with info about school (counting from 0)
classIdx = 4 # column with info about class (counting from 0)
notScored = columnCount - maxScore # number of questions that are about personal info

minimalNoMatches = 5  # number of minimal matches per persona (output list length)
matchMode = "interscholar" # set maching for "scholar" | "interscholar" | "mixed" (counting matches within own school | only from other schools | mixed)

doesntMatter = "Bez znaczenia"  # label for no restriction about sexual orientation in spreadsheet
other = "Inne"  # label for other gender in spreadsheet


print("\n--------------------\nDating algorithm: ON\n--------------------\n")

# script start timestamp
dt_started = datetime.utcnow()

# download whole spreadsheet (only first page)
wholeSheetTmp = sheet.get_all_values()

# delete row with questions
wholeSheetTmp.pop(0)
wholeSheet = []

# doing some matrix stuff to switch array form from row to column based
for i in range(columnCount):
    tmp = []
    for j in range(rowCount):
        tmp.append(wholeSheetTmp[j][i])
    wholeSheet.append(tmp)

print("\n--------------------\nSheet mapped!\n--------------------\n")

with open("codes.txt", "w", encoding="utf8") as txt_file:  # write down codes (emails)
    for line in wholeSheet[0]:
        txt_file.write("".join(line) + "\n")

with open("key.txt", "w", encoding="utf8") as txt_file:  # write down keys (name + surname + school + class)
    for i in range(len(wholeSheet[0])):
        txt_file.write(wholeSheet[1][i] + " " + wholeSheet[2][i] + "\t" + wholeSheet[schoolIdx][i] + "\t" + wholeSheet[classIdx][i] + "\n")

scoreForNameArr = [''] * rowCount

# count how many times given person answered as checked on
for k in range(rowCount):
    checkCode = wholeSheet[0][k]
    for i in range(columnCount - notScored):
        checkAns = wholeSheet[i + notScored][k]
        for j in range(rowCount):
            checkCell = wholeSheet[i + notScored][j]
            currCode = wholeSheet[0][j]
            if checkCell == checkAns and checkCode != currCode:
                scoreForNameArr[k] = scoreForNameArr[k] + " " + currCode
    print((str(int(k + 1)) + " out of " + str(rowCount) + " matched" +
           "\t\t" + str(int(((k + 1) / rowCount) * 100)) + "%"), end="\r")

print("\n--------------------\nAnswers matched!\n--------------------\n")


# this function compare sex preferentions and genders as well as schools to output //true// or //false//
def isYeetComplete(genderOne, sexPrefOne, genderTwo, sexPrefTwo, classOne, classTwo, indexOne, indexTwo):

    # check if we are comparing the same person
    if indexOne == indexTwo:
        # print("=========== " + str(indexOne + 1) + " ==========")
        # print(genderOne, sexPrefOne, genderTwo, sexPrefTwo, classOne, classTwo)
        # print(genderTwo == sexPrefOne, genderOne == sexPrefTwo)
        # print("0 false same person")
        return False

    # check mode scholar compares only students in the same school while interscholar only those from diffrent schools
    if matchMode == "scholar":
        if classOne != classTwo:
            return False
        # else:
            # print("=========== " + str(indexOne + 1) + " ==========")
            # print(genderOne, sexPrefOne, genderTwo, sexPrefTwo, classOne, classTwo)
            # print(genderTwo == sexPrefOne, genderOne == sexPrefTwo)
    else:
        if matchMode == "interscholar":
            if classOne == classTwo:
                return False
            # else:
                # print("=========== " + str(indexOne + 1) + " ==========")
                # print(genderOne, sexPrefOne, genderTwo, sexPrefTwo, classOne, classTwo)
                # print(genderTwo == sexPrefOne, genderOne == sexPrefTwo)

    # one person doesnt care about gender and second person preferences match ones gender //true//
    if (sexPrefOne == doesntMatter and sexPrefTwo == genderOne) or (sexPrefOne == genderTwo and sexPrefTwo == doesntMatter):
        # print("1 true")
        return True

    # both dont care about gender //true//
    if sexPrefOne == doesntMatter and sexPrefTwo == doesntMatter:
        # print("2 true")
        return True

    # one person has other gender and second one doesnt care about it //true//
    if (genderOne == other and sexPrefTwo == doesntMatter and sexPrefOne == genderTwo) or (genderTwo == other and sexPrefOne == doesntMatter and sexPrefTwo == genderOne):
        # print("3 true")
        return True

    # standard case when gender and preferences matches
    if (sexPrefOne == genderTwo and sexPrefTwo == genderOne):
        # print("4 true")
        return True

    # print("5 false")
    return False



scoreArr = []
# excluding codes with sex, preferential and school incompatibilities
for i in range(len(scoreForNameArr)):
    tmpArr = []
    for j in range(len(scoreForNameArr)):
        if isYeetComplete(wholeSheet[genderIdx][i], wholeSheet[sexPrefIdx][i], wholeSheet[genderIdx][j], wholeSheet[sexPrefIdx][j], wholeSheet[schoolIdx][i],
                          wholeSheet[schoolIdx][j], i, j):
            tmpArr.append(scoreForNameArr[j].count(wholeSheet[0][i]))
        else:
            tmpArr.append(scoreForNameArr[j].count("yeeeet"))
    scoreArr.append(tmpArr)
    print((str(i + 1) + " row out of " + str(len(scoreForNameArr)) +
           "\t\t" + str(int(((i + 1) / (len(scoreForNameArr))) * 100)) + "%"), end="\r")

# for i in scoreArr:
#     print(i)

print("\n--------------------\nScore table created!\n--------------------\n")

# DEBUG : print 2D array with scores
# for i in range(len(scoreForNameArr)):
#     print(scoreArr[i])

codeArr = []
# generate arr with list of names
for i in range(len(wholeSheet[0])):
    codeArr.append(wholeSheet[0][i])

finalScoresArr = []
# I dont know if i need this one but I'm too scared of deleting it and not being able to recover this one
# row                                                             #checking the best match for given code
# for i in range(len(scoreArr)):
#     tmpArr = []
#     for k in range(maxScore, 0, -1):  # max to min points
#         for j in range(len(scoreArr)):  # column
#             if(scoreArr[j][i] >= k):
#                 tmpArr.append(codeArr[j])
#         if(len(tmpArr) > (minimalNoMatches-1)):
#             # generate output match data per persona
#             finalScoresArr.append(tmpArr)
#             break

# for currPerson in range(len(scoreArr)):
#     tmpArr = []
#     for currScore in range(1, maxScore, 1):
#         for checkPerson in range(len(scoreArr[currPerson])):
#             if(scoreArr[currPerson][checkPerson] == currScore):
#                 tmpArr.append(codeArr[checkPerson])
#         if(len(tmpArr) > (minimalNoMatches-1)):
#             for i in range(len(tmpArr)-minimalNoMatches):
#                 del tmpArr[-1]
#             break
#     finalScoresArr.append(tmpArr)


for currPerson in range(len(scoreArr)):
    tmpArr = []
    for currScore in range(maxScore, 0, -1):
        for checkPerson in range(len(scoreArr[currPerson])):
            if scoreArr[currPerson][checkPerson] == currScore:
                tmpArr.append(codeArr[checkPerson])
        if len(tmpArr) > (minimalNoMatches - 1):
            for i in range(len(tmpArr) - minimalNoMatches):
                del tmpArr[-1]
            break
    finalScoresArr.append(tmpArr)


# for i in finalScoresArr:
#     print(i)


def isInOtherMatch(currCode, personToCheck):
    idx = codeArr.index(personToCheck)
    if currCode in finalScoresArr[idx]:
        return "\t*"
    return "\t "


output = []
for i in range(len(finalScoresArr)):  # generating one txt from match data per persona
    tmpMainCode = codeArr[i]
    tmpTxt = ""
    for j in range(len(finalScoresArr[i])):
        tmpTxt += ("\t" + finalScoresArr[i][j] +
                   isInOtherMatch(tmpMainCode, finalScoresArr[i][j]))
    tmp = tmpMainCode + tmpTxt
    # tmp = tmpMainCode + tmpTxt
    output.append(tmp)

# for i in output:
#     print(i)

print("\n--------------------\nMatches per persona created!\n--------------------\n")
print("\n--------------------\nCreating encoded .txt file with results...\n--------------------\n")

now = datetime.now()

open('outputDecoded.txt', 'w').close()
# wipe data from outputEncoded.txt
open('outputEncoded.txt', 'w', encoding="utf8").close()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")  # getting time in right format
with open("outputEncoded.txt", "w") as txt_file:
    txt_file.write("\n" + "-" * 20 + "\t\t\t\tGenerated at: " + dt_string +
                   "\t\t\t" + "-" * 20 + "\n")  # stample file with generate date and time
    txt_file.write(
        "-" * 20 + "\t\t" + "Script developed and created by Mikołaj Mrózek" + "\t\t" + "-" * 20 + "\n\n")
    for line in output:
        # write down resaults to outputEncoded.txt file
        txt_file.write("".join(line) + "\n")
print("\n--------------------\n.txt file created - check outputEncoded.txt\n--------------------\n")
print("\n--------------------\nDecoding outputCoded.txt...\n--------------------\n")
print("\n--------------------\nCreating decoded .txt file with results...\n--------------------\n")

with open("key.txt", "r", encoding="utf8") as fd:  # read file with decoded names
    key = fd.read().splitlines()

with open("codes.txt", "r", encoding="utf8") as fd:  # read file with coded names
    code = fd.read().splitlines()

for i in range(len(output)):  # decode codes
    for j in range(len(key)):
        output[i] = output[i].replace(code[j], key[j])
    output[i] = code[i] + "\t" + output[i]
    tmp = ((i + 1) / (len(output))) * 100
    print(("Decoding:\t\t" + str(int(tmp)) + "%"), end="\r")

now = datetime.now()
dt_ended = datetime.utcnow()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
with open("outputDecoded.txt", "w", encoding="utf8") as txt_file:  # write down decoded results
    txt_file.write("\n" + "-" * 20 + "\t\t\t\tGenerated at: " +
                   dt_string + "\t\t\t" + "-" * 20 + "\n")
    txt_file.write(
        "-" * 20 + "\t\t" + "Script developed and created by Mikołaj Mrózek" + "\t\t" + "-" * 20 + "\n\n")
    for line in output:
        txt_file.write("".join(line) + "\n")

print("\n--------------------\n.txt file created - check outputDecoded.txt\n--------------------\n")
print("\n--------------------\n" + "Total runtime: " +
      str(round((dt_ended - dt_started).total_seconds(), 2)) + "s" + "\n--------------------\n")
