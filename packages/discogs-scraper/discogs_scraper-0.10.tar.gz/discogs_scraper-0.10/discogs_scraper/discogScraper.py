import discogs_client

def getReleases(fileName,dis):
    f = open(fileName,"r")
    lines = f.readlines()
    f.close()
    releases = []
    sub1 = "release/"
    sub2 = "-"
    for line in lines:
        if len(line.strip()) != 0 :
            id = ''.join(line.split(sub1)[1].split(sub2)[0])
            releases.append(dis.release(id))
    return releases


def getTracks1(release):
    tracks = ""
    if int(release.formats[0]['qty']) > 1:
        tracks += release.formats[0]['name'] + "1: "
        tracks += release.tracklist[0].title
        for track in release.tracklist[1:]:
            if "1-" or "1." in track.position  :
                tracks += ".- " + str(track.title)
    else :
        canConnect = False
        if len(release.tracklist[0].position) == 0:
            tracks += ""
        else:
            tracks += release.tracklist[0].title
        for track in release.tracklist[1:]:
            if len(track.position) == 0 :
                tracks += ""
            else:
                if canConnect:
                    tracks += ".- " + str(track.title)
                else:
                    tracks += track.title
                    canConnect = True
    return tracks.replace("*","")

def getTracks2(release):
    tracks = ""
    if int(release.formats[0]['qty']) > 1:
        tracks += release.formats[0]['name'] + "2: "
        count = 0
        for track in release.tracklist:
            if "2-" in track.position:
                break
            else:
                count += 1
        tracks += release.tracklist[count].title
        try:
            for track in release.tracklist[(count + 1):]:
                if "2-" or "2." in track.position:
                    tracks += ".- " + str(track.title)
        except:
            tracks += ""
    return tracks.replace("*","")


def getCompony(release):
    compony = release.labels[0].name
    if 'Not On Label' in compony:
        return ""
    return "\"" + compony + "\""

def lettersOnly (inputString):
    return ''.join(c for c in inputString if c.isalpha())

def digitsOnly (inputString):
    return ''.join(c for c in inputString if c.isdigit())

def getLabel(release):
    compony = "\"" + release.labels[0].name + "\""
    if 'Not On Label' in compony:
        compony = ''.join(compony.split('(')[1].split(')')[0])
    catno = ""
    try:
        if any(c.isalpha() for c in release.labels[0].data['catno']):
            catno += "|b" + lettersOnly(release.labels[0].data['catno']).upper()
        if any(c.isdigit() for c in release.labels[0].data['catno']):
            catno += "|c" + digitsOnly(release.labels[0].data['catno'])
    except:
        catno = ""
    return compony.upper() + catno



def getLabelMatch (release):

    compony = "\"" + release.labels[0].name + "\""
    if 'Not On Label' in compony:
        compony = ''.join(compony.split('(')[1].split(')')[0])
    try:
        catno = lettersOnly(release.labels[0].data['catno']).upper()
        catno += digitsOnly(release.labels[0].data['catno'])
    except:
        catno = ""
    return compony.upper().replace(' ', '') + catno

def getFormat (release):
    format = release.formats[0]['qty'] + " "
    if release.formats[0]['name'] == "Vinyl":
        format += "LP"
    else:
        format += release.formats[0]['name']
    if int(release.formats[0]['qty']) > 1:
        format += "s"
    return format

def getBootlegNote (release):
    note = "bootleg "
    if release.formats[0]['name'] == "Vinyl":
        note += "LP"
    else:
        note += release.formats[0]['name']
    return note

def getDate (release):
    if int(release.year) == 0:
        return ""
    else:
        return str(release.year)


d = discogs_client.Client('my_user_agent/1.0', user_token='oZENLBNZAGdNfSaGNEncACkrSPFrdzZLvCTUGslh')
releases = getReleases("URL.txt", d)
f = open("output.csv", "w")
f.write(
    "shelfmarkCD,shelfMarkLP,barcode,compony,label,labelMatch,title,contributer1,genre1,genre2,genre4,genre5,format,recordingAddress,conntentsNote1,contentsNote2,contentsNote3,country,date,copyConditionCode,Collection,Acess,BootlegNote\n")
f.close()
for release in releases:
    csv = ""
    row = []
    row.append("")  # shelfmarkCD
    row.append("")  # shelfMarkLP
    row.append("")  # barcode
    row.append(getCompony(release))  # compony
    row.append(getLabel(release))  # label
    row.append(getLabelMatch(release))  # labelMatch
    row.append("\"" + release.title + "\"")  # title
    row.append("")  # contributer1
    row.append("")  # genre1
    row.append("")  # genre2
    row.append("")  # genre4
    row.append("")  # genre5
    row.append(getFormat(release))  # format
    row.append("")  # recording address
    row.append("\"" + getTracks1(release) + "\"")  # contentsNote1
    row.append("\"" + getTracks2(release) + "\"")  # contentsNote 2
    row.append("")  # contentsNote 3
    row.append(release.country)  # country
    row.append(getDate(release))  # date (empty for now as there are lots of edge case)
    row.append("B")  # copycondition code
    row.append("BPI Anti-Piracy Unit Donation")  # Collection
    row.append("No copies to be made without permission of the donor")  # Access
    row.append(getBootlegNote(release))  # Boolteg note
    for item in row:
        csv += str(item) + ","
    csv += "\n"
    f = open("output.csv", "a")
    f.write(csv)
    f.close()

# print(trackList)
