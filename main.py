import os
import pandas as pd
import xml.dom.minidom

def checkAdb():
    osRet = os.popen("adb version")
    adbVersion = osRet.read()
    osRet.close()
    print(osRet)
    if adbVersion.find("Version") >=0:
        return True
    else:
        print("error adb command no find\n")
        return False

def getCodecXmlList(path, xmlList):
    osRet = os.popen("adb shell \"ls "+path+" | grep codec\"")
    while True:
        lineStr = osRet.readline()
        if not lineStr:
            break
        if lineStr.lower().find("permission  denied") >=0 or lineStr.lower().find("performance")>=0:
            continue
        xmlList.append(lineStr.strip('\n'))
    osRet.close

"""
give a mediaCodec xml node, then, parse the node and append resulet to audoiDataList or videoDataList
automatically.

audio table:
decoder/encoder | name | type | channel count | sample rate | bitrate | on file

video table:
decoder/encoder | name | type | max size | min size | bitrate | on file
"""
def parseCodec(mediaCodec, audioDataList, videoDataList, isDecoder,onFile):
    if isDecoder:
        codec = "decoder"
    else:
        codec = "encoder"

    try :
        type = mediaCodec.getAttribute("type")
        name = mediaCodec.getAttribute("name")
        isAudio=True
        if type.lower().find("audio")>=0:
            isAudio=True
        elif type.lower().find("video")>=0:
            isAudio = False
        else:
            return -1
        
        if isAudio:
            channelCount = ""
            sampleRate = ""
            bitRate = ""
            for limit in mediaCodec.childNodes:
                try :
                    limitNmae = limit.getAttribute("name")
                    if limitNmae == "channel-count":
                        channelCount = limit.getAttribute("max")
                        pass
                    elif limitNmae == "sample-rate":
                        sampleRate = limit.getAttribute("ranges")
                        pass
                    elif limitNmae == "bitrate":
                        bitRate = limit.getAttribute("range")
                        pass
                    else:
                        pass
                except AttributeError:
                    continue
            audioDataList.append([codec, name, type, channelCount, sampleRate, bitRate, onFile])
        else:
            bitRate = ""
            maxSize = ""
            minSzie = ""
            for limit in mediaCodec.childNodes:
                try :
                    limitNmae = limit.getAttribute("name")
                    if limitNmae == "size":
                        maxSize = limit.getAttribute("max")
                        minSzie = limit.getAttribute("min")
                    elif limitNmae == "bitrate":
                        bitRate = limit.getAttribute("range")
                        pass
                    else:
                        pass
                except AttributeError:
                    continue
            videoDataList.append([codec, name, type, maxSize, minSzie, bitRate, onFile])
    except AttributeError:
        return -1
    
    return 0

"""
parse "codec.xml". parameter "onFile" is the xml file in adb device
"""
def parseXml(audioDataList, videoDataList, onFile):
    osRet = os.system("adb pull " + xmlPah + " codec.xml")
    if osRet != 0:
            print("error : fail to download" + xmlPah)
            exit(-1)
    
    domTree = xml.dom.minidom.parse("codec.xml")
    root = domTree.documentElement
    decodersList = root.getElementsByTagName("Decoders")
    for decoders in decodersList:
        for mediaCodec in decoders.childNodes:
            parseCodec(mediaCodec, audioDataList, videoDataList, True, onFile)
    
    decodersList = root.getElementsByTagName("Encoders")
    for decoders in decodersList:
        for mediaCodec in decoders.childNodes:
            parseCodec(mediaCodec, audioDataList, videoDataList, False, onFile)
    
    return 1
    
    

if __name__ == "__main__":
    # execute only if run as a script
    if checkAdb() != True:
        exit(-1)
    os.system("adb root")
    
    xmlList = []
    fileList = []
    getCodecXmlList("/etc/", xmlList)
    for xmlFile in xmlList:
        fileList.append("/etc/"+xmlFile)
    xmlList.clear()

    getCodecXmlList("/vendor/etc/", xmlList)
    for xmlFile in xmlList:
        fileList.append("/vendor/etc/"+xmlFile)
    xmlList.clear()
    
    print("find fines:", end="")
    print(fileList)

    audioCodec=[]
    videoCodec=[]
    for xmlPah in fileList:
        parseXml(audioCodec, videoCodec, xmlPah)
    
    audioPd = pd.DataFrame(audioCodec, columns=
    ["decoder/encoder", "name", "type", "channel count", "sample rate", "bitrate", "on file"], dtype=str)
    audioPd.sort_values(by=["decoder/encoder", "type", "name", "on file"])
    audioPd.to_csv("audio_codecs.csv")

    videoPd = pd.DataFrame(videoCodec, columns=
    ["decoder/encoder", "name", "type", "max size", "min size", "bitrate", "on file"], dtype=str)
    videoPd.sort_values(by=["decoder/encoder", "type", "name", "on file"])
    videoPd.to_csv("video_codecs.csv")

    print("parse file success:")
    for xmlPah in fileList:
        print(xmlPah)
     
    exit(0)
        