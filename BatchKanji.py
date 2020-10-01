# coding=utf-8
import sys, os, platform, re, subprocess, json, urllib.request, urllib.parse, urllib.error
import ssl
from difflib import SequenceMatcher
import re
import genanki

answerformat = '<div class=jp> {{furigana:Reading}} </div>\n <hr id=answer>\n<div class=jptiny align=right>({{Chapter Number}})</div>\n<div class=jp>{{Meaning}}</div>\n<p><span class=jpmid>{{furigana:Comment}}</span></p>'

styling = '.card {font-family: arial;   font-size: 20px;    text-align: center;    color: black;    background-color: white;    }    .jp { font-size: 30px }    .win .jp { font-family: "MS Mincho", "ＭＳ 明朝"; }    .mac .jp { font-family: "Hiragino Mincho Pro", "ヒラギノ明朝 Pro"; }    .linux .jp { font-family: "TakaoPGothic"; }    .mobile .jp { font-family: myfont;}    .jpmid { font-size: 20px }    .win .jpmid { font-family: "MS Mincho", "ＭＳ 明朝"; }    .mac .jpmid { font-family: "Hiragino Mincho Pro", "ヒラギノ明朝 Pro"; }    .linux .jpmid { font-family: "TakaoPGothic";}    .mobile .jpmid { font-family: myfont; }    .jptiny { font-size: 10px }    .win .jptiny { font-family: "MS Mincho", "ＭＳ 明朝"; }    .mac .jptiny { font-family: "Hiragino Mincho Pro", "ヒラギノ明朝 Pro"; }    .linux .jptiny { font-family: "TakaoPGothic";}    .mobile .jptiny { font-family: myfont; }    @font-face { font-family: myfont; src: url("_TakaoPGothic.ttf"); }'

def extract_unicode_block(unicode_block, string):
    ''' extracts and returns all texts from a unicode block from string argument.
    Note that you must use the unicode blocks defined above, or patterns of similar form '''
    return re.findall( unicode_block, string)

def remove_unicode_block(unicode_block, string):
    ''' removes all chaacters from a unicode block and returns all remaining texts from string argument.
    Note that you must use the unicode blocks defined above, or patterns of similar form '''
    return re.sub( unicode_block, '', string)

hiragana_full = r'[ぁ-ゟ]+'
katakana_full = r'[゠-ヿ]+'
kanji_full = r'[㐀-䶵一-鿋豈-頻]+'
#radicals = r'[⺀-⿕]'
#katakana_half_width = r'[｟-ﾟ]'


#This defines the card formatting that will be created.  
japanwordsmodel = genanki.Model(160227392319, 'Japanese Word Recognition',css=styling,
              fields=[
                      {'name': 'Expression'},
                      {'name': 'Reading'},
                      {'name': 'Meaning'},
#                      {'name': 'Comment'},
                            ],
                templates=[

                 {'name': 'Reading+Word -> Meaning', 
                          'qfmt': '<div class=jp> {{furigana:Reading}} </div>' ,
                          'afmt': answerformat,
                          'styling': styling},

                 {'name': 'Word ->  Meaning+Reading', 
                          'qfmt': '<div class=jp> {{Expression}} </div>',
                          'afmt': answerformat,
                          'styling': styling},
                          ]
                )


#========================================================================================
def batchcreate(srcTxt, commononly=True):
    searchtxt = srcTxt.strip()
    my_deck = genanki.Deck(
                 2059400110,
                'Node Kanji'
                )


    #Itterates over the characters in the
    for char in searchtxt:
        # result holders for API call
        word = ''
        definition = ''
        definition2 = ''
        partOfSpeech = ''
        reading = ''
        tags = ''
        restrictions = ''
        antonyms = ''
        info = ''
        
        baseUrl = 'http://jisho.org/api/v1/search/words?keyword='

        print("Common Only: {}".format(commononly))
        print(char)

        searchString = "*"+char+"*"
        if commononly:
            searchString = searchString + " #common"

#        searchString = searchString + " #kanji"
        print("Searching Jisho with the string: {}".format(searchString))

        #The following code is modified from Nick Youngblood's <osunightfall@gmail.com>
        #Anki extention. 
        # See http://ankiweb.net/shared/info/1545080191 for original extention code.

        # Make url conform to ASCII 
        encodedUrl = baseUrl + urllib.parse.quote(searchString.encode('utf8'))
        context = ssl._create_unverified_context()
        try:
            response = urllib.request.urlopen(encodedUrl, context=context).read()
            parsed_json = json.loads(response.decode('utf-8'))
        except IOError as e:
            return 


        # Make url conform to ASCII 
        encodedUrl = baseUrl + urllib.parse.quote(searchString.encode('utf8'))
        context = ssl._create_unverified_context()
        try:
            response = urllib.request.urlopen(encodedUrl, context=context).read()
            parsed_json2 = json.loads(response.decode('utf-8'))
        except IOError as e:
            return 

        parsed_json.update(parsed_json2)



        # Exit if nothing useful came back
        try: 
            responseHasResults = parsed_json['data'][0]
        except IndexError:
            print("Jisho.org returned no data for search term '%s'"%(searchString))
            return 

        for word in parsed_json["data"]:

            try: # Get proper word if it was typed with kana and should have kanji, or 
                properspelling = word['japanese'][0]['word']
            except (IndexError, KeyError):
                try: # Katakana search terms put the word elsewhere
                    properspelling = word['japanese'][0]['reading']
                except (IndexError, KeyError):
                    pass


            # Get the first definition if it exists
            try:
                definitionList = word['senses'][0]['english_definitions']
                definition = ''
                for defWord in definitionList:
                    if (len(definition) > 0):
                        definition = definition + ', '
                    definition = definition + defWord
         
            except (IndexError, KeyError):
                pass

            # Get the second definition if it exists
            try:
                definition2List = word['senses'][1]['english_definitions']
                for defWord in definition2List:
                    if (len(definition2) > 0):
                        definition2 = definition2 + ', '
                    definition2 = definition2 + defWord
            except (IndexError, KeyError):
                pass

            # Get the part of speech string if it exists
            try:
                partOfSpeech = word['senses'][0]['parts_of_speech'][0]
            except (IndexError, KeyError):
                pass    

            # Get the reading string if it exists
            try:
                reading = word['japanese'][0]['reading']
            except (IndexError, KeyError):
                pass    

            # Get the tags string if it exists
            try:
                tags = word['senses'][0]['tags'][0]
            except (IndexError, KeyError):
                pass    

            # Get the restrictions string if it exists
            try:
                restrictions = word['senses'][0]['restrictions'][0]
            except (IndexError, KeyError):
                pass    

            # Get the antonyms string if it exists
            try:
                antonyms = word['senses'][0]['antonyms'][0]
            except (IndexError, KeyError):
                pass    

            # Get the info string if it exists
            try:
                info = word['senses'][0]['info'][0]
            except (IndexError, KeyError):
                pass

            #This code is designed to automatically generate the furigana strings
            #and place them at the proper location. IE if you have a word
            #with a hiragana tail, it will place the furigana before the tail
            #so that it appears above the Kanji in question. There may
            #be a few bugs with this, but so far it works for a lot of basic words.
            hiragana = extract_unicode_block(hiragana_full, properspelling)
            katakana = extract_unicode_block(katakana_full, properspelling)
            kanji = extract_unicode_block(kanji_full, properspelling)
            rawspelling = properspelling
            newstr = reading
            for substr in sorted(hiragana, reverse=True):
                newstr = re.sub(substr, " ", newstr)
            for substr in sorted(katakana, reverse=True):
                newstr = re.sub(substr, " ", newstr)
            for substr in sorted(kanji, reverse=True):
                properspelling = re.sub(substr, substr+"%s", properspelling)

            furigana = ["["+x+"]" for x in newstr.split()]

#            print(properspelling)
#            print(furigana)
            try:
                outreading = properspelling%(tuple(furigana))
            except:
                try:
                    outreading = properspelling%("["+reading+"]")
                except:
                    continue

            print(outreading)
            my_note = genanki.Note(
                    model=japanwordsmodel,
                    fields=[properspelling.replace("%s", ""), outreading, definition])
            my_deck.add_note(my_note)
        genanki.Package(my_deck).write_to_file('output.apkg')


#===============================================================================
if __name__ == "__main__":
    import sys
    try:
        instr = sys.argv[1]
        try:
            commonflag = sys.argv[2]
        except IndexError:
            commonflag = True

    except IndexError:
        print("Please Enter a Kanji or Word to Begin:")
        instr = input()
        print("Common Words Only? (y/n):")
        ans = input()
        if ans.lower().strip() == "n":
            commonflag = False
        else:
            commonflag = True


    batchcreate(instr, commonflag)

