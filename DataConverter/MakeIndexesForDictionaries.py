#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MakeIndexesForDictionaries.py
#
# Handles processing the two dictionary files to pre-format them for the Android app
#
# Copyright (C) 2014-2017 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This program preformats Matigsalug dictionary entries into HTML
    and then writes them (one line per entry) to a file.

It also creates an index to the above file, storing the lexeme, the file position, and the entry length.

It also recreates a reverse index to the above index entries, just storing the matching lexeme.
"""

from gettext import gettext as _

LastModifiedDate = '2017-06-10' # by RJH
ShortProgName = "MakeIndexesForDictionaries"
ProgName = "Make Indexes For Dictionaries"
ProgVersion = '0.40'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )


import sys, os, logging
import json, re
from datetime import datetime
from collections import OrderedDict

BibleOrgSysFolder = "/mnt/SSD/AutoProcesses/BibleOrgSys"
sys.path.append( BibleOrgSysFolder ) # Path to copy of BibleOrgSys modules
                                     # automatically updated from Git by a cron job
from SFMFile import SFMRecords


# Global file paths
studentDictSourceFilepath = 'Dictionary.txt'
studentDictKey = 'lx'

mainDictSourceFilepath = 'MBT_Root.dic'
mainDictKey = 'og'

outputFolder = 'MS-Dict_assets/'



def indexExistingStudentDict():
    """
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( "\nindexExistingStudentDict..." )

    destinationFilepath = os.path.join( outputFolder, 'MS-SD-index-txt.json' )

    chunkSize = 128 # Must be longer than the longest line
    binaryBuffer = b''

    lineCount = nextBufferOffset = nextDataOffset = 0
    createdIndex = []
    with open( studentDictSourceFilepath, 'rb' ) as dictFile: # Automatically closes the file when done
        while True:
            if len(binaryBuffer) < chunkSize:
                currentBufferOffset = nextBufferOffset;
                #print( "Read bytes..." )
                binaryNew = dictFile.read( 2 * chunkSize )
                nextBufferOffset += len( binaryNew )
                binaryBuffer += binaryNew
            if not binaryBuffer: break # at the end of the file
            ixLF = binaryBuffer.index( b'\n' )
            #print( "ixLF", ixLF )
            #print( len(binaryBuffer), binaryBuffer )
            dataBits, binaryBuffer = binaryBuffer[:ixLF+1], binaryBuffer[ixLF+1:]
            currentDataOffset = nextDataOffset
            nextDataOffset += len(dataBits )
            #print( len(dataBits), dataBits, len(binaryBuffer), binaryBuffer )
            line = dataBits.decode( 'utf-8' )
            #print( len(line), line )

            lineCount += 1
            if lineCount==1 and line[0]==chr(65279): #U+FEFF
                logging.info( "      indexExistingStudentDict.load: Detected UTF-16 Byte Order Marker" )
                line = line[1:] # Remove the UTF-8 Byte Order Marker
            while line and line[-1] in ('\r','\n',): line=line[:-1] # Removing trailing newline characters
            if not line: continue # Just discard blank lines
            lastLine = line
            #print ( currentBufferOffset, 'Student dict file line is "' + line + '"' )

            if line[0]!='\\': # Not a SFM line
                #if len(result)==0: # We don't have any SFM data lines yet
                    #if BibleOrgSysGlobals.verbosityLevel > 2:
                        #logging.error( "Non-SFM line in " + sfm_filename + " -- line ignored at #" + str(lineCount) )
                #else: # Append this continuation line
                    #if marker not in ignoreSFMs:
                        #oldmarker, oldtext = result.pop()
                        ##print ("Popped",oldmarker,oldtext)
                        ##print ("Adding", line, "to", oldmarker, oldtext)
                        #result.append( (oldmarker, oldtext+' '+line) )
                    #continue
                logging.info( "Non-SFM line in " + studentDictSourceFilepath + " -- line ignored at #" + str(lineCount) + ' for ' + marker )
                assert( marker != studentDictKey )
            else:
                lineAfterBackslash = line[1:]
                si1 = lineAfterBackslash.find( ' ' )
                si2 = lineAfterBackslash.find( '\\' )
                if si2!=-1 and (si1==-1 or si2<si1): # Marker stops at a backslash
                    marker = lineAfterBackslash[:si2]
                    text = lineAfterBackslash[si2:]
                elif si1!=-1: # Marker stops at a space
                    marker = lineAfterBackslash[:si1]
                    text = lineAfterBackslash[si1+1:] # We drop the space
                else: # The line is only the marker
                    marker = lineAfterBackslash
                    text = ''

                if marker==studentDictKey and text[0]!='~':
                    #print( currentDataOffset, text )
                    createdIndex.append( (text, currentDataOffset) )

    if createdIndex:
        print( "  {} index entries created.".format( len(createdIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "  indexExistingStudentDict " +  _("Exporting index to {}...").format( destinationFilepath ) )
        with open( destinationFilepath, 'wt' ) as jsonFile:
            json.dump( createdIndex, jsonFile, indent=2 )
    # end of indexExistingStudentDict



def indexExistingMainDict():
    """
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( "\nindexExistingStudentDict..." )

    destinationFilepath = os.path.join( outputFolder, 'MS-MD-index-txt.json' )

    chunkSize = 128 # Must be longer than the longest line
    binaryBuffer = b''

    lineCount = nextBufferOffset = nextDataOffset = 0
    createdIndex = []
    with open( mainDictSourceFilepath, 'rb' ) as dictFile: # Automatically closes the file when done
        while True:
            if len(binaryBuffer) < chunkSize:
                currentBufferOffset = nextBufferOffset;
                #print( "Read bytes..." )
                binaryNew = dictFile.read( 2 * chunkSize )
                nextBufferOffset += len( binaryNew )
                binaryBuffer += binaryNew
            if not binaryBuffer: break # at the end of the file
            ixLF = binaryBuffer.index( b'\n' )
            #print( "ixLF", ixLF )
            #print( len(binaryBuffer), binaryBuffer )
            dataBits, binaryBuffer = binaryBuffer[:ixLF+1], binaryBuffer[ixLF+1:]
            currentDataOffset = nextDataOffset
            nextDataOffset += len(dataBits )
            #print( len(dataBits), dataBits, len(binaryBuffer), binaryBuffer )
            line = dataBits.decode( 'utf-8' )
            #print( len(line), line )

            lineCount += 1
            if lineCount==1 and line[0]==chr(65279): #U+FEFF
                logging.info( "      indexMainDict.load: Detected UTF-16 Byte Order Marker" )
                line = line[1:] # Remove the UTF-8 Byte Order Marker
            while line and line[-1] in ('\r','\n',): line=line[:-1] # Removing trailing newline characters
            if not line: continue # Just discard blank lines
            lastLine = line
            #print ( currentBufferOffset, 'Main dict file line is "' + line + '"' )

            if line[0]!='\\': # Not a SFM line
                #if len(result)==0: # We don't have any SFM data lines yet
                    #if BibleOrgSysGlobals.verbosityLevel > 2:
                        #logging.error( "Non-SFM line in " + sfm_filename + " -- line ignored at #" + str(lineCount) )
                #else: # Append this continuation line
                    #if marker not in ignoreSFMs:
                        #oldmarker, oldtext = result.pop()
                        ##print ("Popped",oldmarker,oldtext)
                        ##print ("Adding", line, "to", oldmarker, oldtext)
                        #result.append( (oldmarker, oldtext+' '+line) )
                    #continue
                logging.info( "Non-SFM line in " + mainDictSourceFilepath + " -- line ignored at #" + str(lineCount) + ' for ' + marker )
                assert( marker != mainDictKey )
            else:
                lineAfterBackslash = line[1:]
                si1 = lineAfterBackslash.find( ' ' )
                si2 = lineAfterBackslash.find( '\\' )
                if si2!=-1 and (si1==-1 or si2<si1): # Marker stops at a backslash
                    marker = lineAfterBackslash[:si2]
                    text = lineAfterBackslash[si2:]
                elif si1!=-1: # Marker stops at a space
                    marker = lineAfterBackslash[:si1]
                    text = lineAfterBackslash[si1+1:] # We drop the space
                else: # The line is only the marker
                    marker = lineAfterBackslash
                    text = ''

                if marker==studentDictKey and text[0]!='~':
                    #print( currentDataOffset, text )
                    createdIndex.append( (text, currentDataOffset) )

    if createdIndex:
        print( "  {} index entries created.".format( len(createdIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "  indexExistingMainDict " +  _("Exporting index to {}...").format( destinationFilepath ) )
        with open( destinationFilepath, 'wt' ) as jsonFile:
            json.dump( createdIndex, jsonFile, indent=2 )
    # end of indexExistingMainDict



def reformatAndIndexStudentDict():
    """
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( "\nReformat and Index Student Dict..." )

    keyMarker = 'lx'
    ignoreSFMs= 'so'

    SDDataFormatVersion = 1
    jsonIndent = 0 # Keep files small for small phones
    maxChunkBytes = 470000; # Max bytes for the HTML chunk files
    destinationHeaderFilepath = os.path.join( outputFolder, 'MS-SD.json' )
    destinationHTMLFilepathTemplate = os.path.join( outputFolder, 'MS-SD.{}.html' ) # Missing a chunk number
    destinationIndexFilepath = os.path.join( outputFolder, 'MS-SD-ix-html.json' )
    destinationReverseIndexFilepath = os.path.join( outputFolder, 'MS-SD-rev-ix.json' )
    compressionFilepath = os.path.join( outputFolder, 'MS-SD-cmpr.json' )

    segCounts1, segCounts2, segCounts3 = {}, {}, {}

    SDCompressions = (
        ('@A','<h1 class="Lexeme">'),
        ('@a','</h1>'),
        #('@B','<h2 class="HomonymNumber">'),
        #('@b','</h2>'),
        ('@C','<p class="Variant">Variant: <span class="Variant">'),
        ('@D','<p class="MainEntry">See: <span class="MainEntry">'),
        ('@E','<p class="Pronunciation">Pronunciation: <span class="Pronunciation">'),
        ('@F','<p class="POS">Part of speech: <span class="POS">'),
        ('@G','<section class="Sense" id="'),
        ('@H','"><span class="SenseNumber">'),
        ('@I','<p class="MatigsalugDefinition">Matigsalug definition/word(s): <span class="MatigsalugDefinition">'),
        ('@J','<p class="MatigsalugDefinitionDF">DF Matigsalug definition: <span class="MatigsalugDefinitionDF">'),
        ('@K','<p class="MatigsalugDefinitionRF">RF Matigsalug definition: <span class="MatigsalugDefinitionRF">'),
        ('@L','<p class="EnglishDefinition">Usage: <span class="EnglishDefinition">'),
        ('@M','<p class="GeneralNote">Note: <span class="GeneralNote">'),
        ('@N','<p class="GrammarNote">Grammar note: <span class="GrammarNote">'),
        ('@O','<p class="EnglishExampleSentenceZO">ZO Sentence: <span class="EnglishExampleSentenceZO">'),
        ('@P','<p class="EnglishExampleSentence">Sentence: <span class="EnglishExampleSentence">'),
        ('@Q','<p class="MatigsalugExampleSentence">Translation: <span class="MatigsalugExampleSentence">'),
        ('@R','<p class="Plural">Plural is: <span class="Plural">'),
        ('@S','<p class="SeeAlso">See also: <span class="SeeAlso">'),
        ('@T','<p class="CompareWith">Compare with: <span class="CompareWith">'),
        ('@U','<p class="Usage">Usage: <span class="Usage">'),
        ('@V','<p class="ParadigmLabel">Paradigm label: <span class="ParadigmLabel">'),
        ('@W','<p class="ParadigmForm">Paradigm form: <span class="ParadigmForm">'),
        ('@X','<p class="SemanticDomain">Semantic domain: <span class="SemanticDomain">'),
        ('@Y','<p class="Status">Status: <span class="Status">'),
        ('@Z','<p class="EditDate">Edited: <span class="EditDate">'),

        #('@p','</p>'),
        #('@s','</span>'),
        ('@t','/</span>'), # For sense numbers
        ('@e','</section>'),
        ('@f','</section><hr>'), # After last sense in entry

        ('@c','</span></p>'),
        #('@[','<sub>'),
        #('@]','</sub>'),
        ('@{','<b>'),
        ('@}','</b>'),
        #('@g','<i>'),
        #('@h','</i>'),

        ('^',' something'),
        ('*',' te '),
        ('@0',' the '),
        ('@1',' you '),
        ('@2',' ne '),
        ('@3',' that '),
        ('@4',' to '),
        ('@5',' is '),
        ('@6',' of '),
        ('@7','/201'),
        ('@8','ready'),
        ('@9','thing'),
        ('@+',' or '),
        ('@-','egpa'),
        ('@=',' an '),
        ('@_',' wey '),

        ('@m','/Jan'),
        ('@n','/Feb'),
        ('@o','/Mar'),
        ('@p','/Apr'),
        ('@q','/May'),
        ('@r','/Jun'),
        ('@u','/Jul'),
        ('@v','/Aug'),
        ('@w','/Sep'),
        ('@x','/Oct'),
        ('@y','/Nov'),
        ('@z','/Dec'),

        ('~~','@'), # Must be last
        )

    usageCount = {}
    codeSet, dataSet, reversedCompressions = [], [], []
    for shortString, longString in SDCompressions:
        usageCount[shortString] = 0
        if shortString in codeSet: # check for duplicates
            logging.critical( "Duplicate {} in compression dict".format( repr(shortString) ) )
            print( shortString, codeSet )
            halt
        codeSet.append( shortString )
        if longString in dataSet: # check for duplicates
            logging.critical( "Duplicate {} in compression dict".format( repr(longString) ) )
            print( longString, dataSet )
            halt
        dataSet.append( longString )
        if longString != '@':
            reversedCompressions.append( (longString,shortString,) )
    reversedCompressions = sorted( reversedCompressions, key=lambda s: -len(s[0]) ) # Longest string length first
    #print( len(reversedCompressions), reversedCompressions )


    def writeSDHeader( chunks ):
        """
        """
        headerDict = OrderedDict()
        headerDict['Data format version'] = SDDataFormatVersion
        headerDict['Conversion date'] = datetime.today().strftime("%Y-%m-%d")
        headerDict['Conversion program'] = ProgNameVersion
        headerDict['Number of chunks'] = len( chunks )
        for chunkNum, chunkEntries in chunks:
            #print( chunkNum, chunkEntries )
            headerDict['Chunk{}'.format(chunkNum)] = chunkEntries
        #print( headerDict )

        with open( destinationHeaderFilepath, 'wt' ) as jsonFile:
            json.dump( headerDict, jsonFile, indent=2 )
    # end of reformatAndIndexStudentDict.writeSDHeader


    def writeCompressions():
        """
        """
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Writing compression entries..." )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    indexExistingStudentDict " +  _("Exporting index to {}...").format( compressionFilepath ) )
        with open( compressionFilepath, 'wt' ) as jsonFile:
            #for compression in SDCompressions:
                #compFile.write( compression[0] + compression[1] + '\n' )
            json.dump( SDCompressions, jsonFile, indent=jsonIndent )
        print( "    {} compression entries written.".format( len(SDCompressions) ) )
    # end of reformatAndIndexStudentDict.writeCompressions


    bytesRaw = bytesCompressed = 0
    def compress( entry ):
        """
        """
        nonlocal bytesRaw, bytesCompressed
        #print( repr(entry) ); halt
        bytesRaw += len( entry.encode('UTF8') )
        result = entry
        if '@' in result:
            result = result.replace( '@', '~~' )
            usageCount['~~'] += 1
        for longString, shortString in reversedCompressions:
            if longString in result:
                result = result.replace( longString, shortString )
                usageCount[shortString] += 1
        bytesCompressed += len( result.encode('UTF8') )
        return result
    # end of reformatAndIndexStudentDict.compress


    def decompress( entry ):
        """
        """
        result = entry
        for shortString, longString in SDCompressions:
            result = result.replace( shortString, longString )
        return result
    # end of reformatAndIndexStudentDict.decompress


    def formatRecord( thisRecord ):
        """
        """
        assert( len(thisRecord) > 4 )
        assert( thisRecord[0][0] == keyMarker )
        assert( thisRecord[0][1][0] != '~' )
        htmlString = ""
        word = lastMarker = lastHTML = ''
        endSenseHTML = '</section>'
        inASense = False
        validFieldCount = 0
        for originalMarker, originalText in thisRecord:
            marker, text = originalMarker, originalText

            if marker == keyMarker:
                assert( text )
                lexeme = text
                word = text
                #print( "\n{}".format( lexeme ) )
            #print( marker, repr(text) )
            assert( marker )
            if marker in ('lx1',): assert( not text ) # This field marks "online only" entries
            else:
                if not text:
                    logging.error( _("StudentDictionary: Missing text for {} in {}").format( repr(marker), repr(lexeme) ) )
                    continue
                if marker.endswith('1'): marker = marker[:-1] # Remove the markers for online dictionary only
            if text in ('à è ì ù','æ ə',):
                #print( "Ignored", repr(text), "for", marker, "for", repr(lexeme) )
                continue # Just ignore this whole field

            # Exception characters for compression
            for shortString,longString in SDCompressions:
                #if shortString[0] in text:
                if shortString in text:
                    logging.critical( "{}:{} contains {}".format( marker, repr(text), repr(shortString) ) )
                    halt

            # Handle XML special characters
            text = text.replace( '"', '&quot;' )
            text = text.replace( '&', '&amp;' )
            text = text.replace( '<', '&lt;' )
            text = text.replace( '>', '&gt;' )

            # Handle some special MDF codes
            text = text.replace( '|{emdash}', '—' )
            text = text.replace( '|{endash}', '–' )
            text = text.replace( '|{~}', ' ' )

            # Handling bolding of some MDF fields
            text = re.sub( r'\|u{(.+?)}', r'<u>\1</u>', text )
            text = re.sub( r'\|fb{(.+?)}', r'<b>\1</b>', text )
            text = re.sub( r'fb:(.+?)([ .,/])', r'<b>\1</b>\2', text )
            text = re.sub( r'fb:(.+?)$', r'<b>\1</b>', text )
            if 'fb:' in text or 'fb{' in text: halt
            if '{' in text or '}' in text: halt
            #if '&' in text: halt # These seem to be displayed ok

            if 0: # Record word count stats -- do any text sequences in the given range of lengths
                minL, maxL = 3,40
                txtL = len(text)
                if txtL >= minL:
                    #print( txtL, repr(text) )
                    for ix in range( 0, txtL):
                        for length in range( minL, maxL+1 ):
                            if (ix+length) <= txtL:
                                seg = text[ix:ix+length]
                                #print( ' ', len(seg), repr(seg) )
                                if seg in segCounts1: segCounts1[seg] += 1
                                else: segCounts1[seg] = 1

            thisHTML = ''
            if marker == 'lx':
                thisHTML = '<h1 class="Lexeme">{}</h1>'.format( text )
            elif marker == 'lx1':
                continue # It just marks this entry as for online apps only (not the printed dict)
            elif marker == 'hm':
                assert( lastMarker == 'lx' )
                #thisHTML = '<h2 class="HomonymNumber">{}</h2>'.format( text )
                assert( lastHTML.endswith( '</h1>' ) )
                lastHTML = lastHTML[:-5] # Remove the h1 close tag
                thisHTML = '<sub>{}</sub></h1>'.format( text )
            elif marker == 'va':
                thisHTML = '<p class="Variant">Variant: <span class="Variant">{}</span></p>'.format( text )
            elif marker == 'mn':
                thisHTML = '<p class="MainEntry">See: <span class="MainEntry">{}</span></p>'.format( text )
            elif marker == 'ph':
                thisHTML = '<p class="Pronunciation">Pronunciation: <span class="Pronunciation">{}</span></p>'.format( text )
            elif marker == 'ps':
                thisHTML = '<p class="POS">Part of speech: <span class="POS">{}</span></p>'.format( text )

            elif marker == 'sn':
                #FAILS on battle: assert( inASense or lastMarker == 'ps' ) # Follows PoS
                senseStuff = '<section class="Sense" id="{}"><span class="SenseNumber">{}/</span>'.format( text,text )
                if lastMarker == 'ps': # Put the sense number BEFORE the ps
                    if inASense:
                        htmlString += endSenseHTML
                    htmlString += senseStuff # POS is still in lastHTML
                else: # Not sure what we're following, so just do the normal thing
                    if inASense:
                        thisHTML = endSenseHTML
                    thisHTML += senseStuff
                inASense = True
            elif marker == 're': # Used for reverse index only
                pass # ignore
            elif marker == 'dn':
                pass # Can't work out what this field is for
            elif marker == 'de':
                thisHTML = '<p class="MatigsalugDefinition">Matigsalug definition/word(s): <span class="MatigsalugDefinition">{}</span></p>'.format( text )
            elif marker == 'df':
                thisHTML = '<p class="MatigsalugDefinitionDF">DF Matigsalug definition: <span class="MatigsalugDefinitionDF">{}</span></p>'.format( text )
                logging.critical( "StudentDictionary: {} has a df field: {}".format( repr(lexeme), repr(originalText) ) )
            elif marker == 'rf':
                thisHTML = '<p class="MatigsalugDefinitionRF">RF Matigsalug definition: <span class="MatigsalugDefinitionRF">{}</span></p>'.format( text )
                logging.critical( "StudentDictionary: {} has a rf field: {}".format( repr(lexeme), repr(originalText) ) )
            elif marker == 'dv':
                thisHTML = '<p class="EnglishDefinition">Usage: <span class="EnglishDefinition">{}</span></p>'.format( text )
            elif marker == 'nt':
                thisHTML = '<p class="GeneralNote">Note: <span class="GeneralNote">{}</span></p>'.format( text )
            elif marker == 'ng':
                thisHTML = '<p class="GrammarNote">Grammar note: <span class="GrammarNote">{}</span></p>'.format( text )
            elif marker == 'zo':
                thisHTML = '<p class="EnglishExampleSentenceZO">ZO Sentence: <span class="EnglishExampleSentenceZO">{}</span></p>'.format( text )
                logging.critical( "StudentDictionary: {} has a zo field: {}".format( repr(lexeme), repr(originalText) ) )
            elif marker == 'xv':
                thisHTML = '<p class="EnglishExampleSentence">Sentence: <span class="EnglishExampleSentence">{}</span></p>'.format( text )
            elif marker == 'xe':
                thisHTML = '<p class="MatigsalugExampleSentence">Translation: <span class="MatigsalugExampleSentence">{}</span></p>'.format( text )
            elif marker == 'pl':
                thisHTML = '<p class="Plural">Plural is: <span class="Plural">{}</span></p>'.format( text )
            elif marker == 'se':
                thisHTML = '<p class="SeeAlso">See also: <span class="SeeAlso">{}</span></p>'.format( text )
            elif marker == 'cf':
                thisHTML = '<p class="CompareWith">Compare with: <span class="CompareWith">{}</span></p>'.format( text )
            elif marker == 'ue':
                thisHTML = '<p class="Usage">Usage: <span class="Usage">{}</span></p>'.format( text )
            elif marker == 'pdl':
                if inASense:
                    thisHTML = endSenseHTML + '<hr>'
                    inASense = False
                thisHTML += '<p class="ParadigmLabel">Paradigm label: <span class="ParadigmLabel">{}</span></p>'.format( text )
            elif marker == 'pdv':
                if inASense:
                    thisHTML = endSenseHTML + '<hr>'
                    inASense = False
                thisHTML += '<p class="ParadigmForm">Paradigm form: <span class="ParadigmForm">{}</span></p>'.format( text )
            elif marker == 'sd':
                if inASense:
                    thisHTML = endSenseHTML + '<hr>'
                    inASense = False
                thisHTML += '<p class="SemanticDomain">Semantic domain: <span class="SemanticDomain">{}</span></p>'.format( text )
            elif marker == 'st':
                if inASense:
                    thisHTML = endSenseHTML + '<hr>'
                    inASense = False
                thisHTML += '<p class="Status">Status: <span class="Status">{}</span></p>'.format( text )
            elif marker == 'dt':
                if inASense:
                    thisHTML = endSenseHTML + '<hr>'
                    inASense = False
                thisHTML += '<p class="EditDate">Edited: <span class="EditDate">{}</span></p>'.format( text )
            else:
                logging.critical( "  Didn't process {} {} for {} yet".format( repr(marker), repr(originalText), repr(lexeme) ) )
                if BibleOrgSysGlobals.debugFlag: halt

            htmlString += lastHTML
            lastMarker = marker
            lastHTML = thisHTML
            if marker not in ('lx','st','dt'): # then it's actually some information
                validFieldCount += 1

        htmlString += lastHTML
        if inASense:
            htmlString += endSenseHTML
            inASense = False
        if validFieldCount < 1:
            #print( "questionable", validFieldCount, lexeme, htmlString )
            return None
        #print( lexeme, htmlString )
        return lexeme, htmlString
    # end of reformatAndIndexStudentDict.formatRecord

    def createReverseEntries( thisRecord ):
        """
        """
        results = set()
        for marker, text in thisRecord:
            #print( marker, text )
            if marker == keyMarker:
                assert( text )
                lexeme = text
                #print( "\n{}".format( lexeme ) )
            elif marker == 're':
                #assert( text )
                if text and text != 'à è ì ù':
                    results.add( text ) # This is a set so duplicates are automatically removed
                    adjText = text.lower().replace('à','a').replace('è','e').replace('ì','i') \
                        .replace('ò','o').replace('ó','o').replace('ô','o').replace('õ','o').replace('ö','o') \
                        .replace('ù','u').replace('æ','ae')
                    results.add( adjText )
                    for field in ('pegka','pegke','peg-','peg','egka','egke','eg-','eg',):
                        # Also enter word with suffixes removed
                        #print( '1', repr(text), repr(adjText), repr(field) )
                        if text.startswith( field ) and len(text)>len(field)+2: # e.g., eg-awe
                            #print( '2', repr(text), repr(adjText), repr(field) )
                            results.add( text[len(field):] )
                            results.add( adjText[len(field):] )
                            break
        #print( "results", results )
        return results
    # end of reformatAndIndexStudentDict.createReverseEntries

    # Read the existing records into memory
    recordsDB = SFMRecords()
    recordsDB.read( studentDictSourceFilepath, keyMarker, ignoreSFMs=ignoreSFMs )
    print( "  {} records read from {}".format( len(recordsDB.records), studentDictSourceFilepath ) )
    if 0: # Display some sample records
        for i, r in enumerate(recordsDB.records):
            print ( i, r)
            if i>3: break
        print( '...\n',len(recordsDB.records)-1, recordsDB.records[-1]) # Display the last record

    # Format each record into HTML and write it into a new file, along with an index entry
    createdIndex, reverseIndex = [], []
    fileOffset = chunkCount = 0
    chunkNumber, chunkList = 1, []
    dictHTMLFile = open( destinationHTMLFilepathTemplate.format( chunkNumber ), 'wb' )
    for record in recordsDB.records:
        if record[0][0] != keyMarker: continue # Ignore header record
        if record[0][1][0] == '~': continue # Ignore special records

        formatRecordResult = formatRecord( record )
        if formatRecordResult is None: continue
        lexeme, formattedRecord = formatRecordResult
        if 0:
            minL, maxL = 10,70
            txtL = len(formattedRecord)
            if txtL >= minL:
                for ix in range( 0, txtL):
                    for length in range( minL, maxL+1 ):
                        if (ix+length) <= txtL:
                            seg = formattedRecord[ix:ix+length]
                            if seg in segCounts2: segCounts2[seg] += 1
                            else: segCounts2[seg] = 1

        compressedRecord = compress( formattedRecord )
        checkRecord = decompress( compressedRecord )
        if checkRecord != formattedRecord: halt
        if 0:
            minL, maxL = 4,60
            txtL = len(compressedRecord)
            if txtL >= minL:
                for ix in range( 0, txtL):
                    for length in range( minL, maxL+1 ):
                        if (ix+length) <= txtL:
                            seg = compressedRecord[ix:ix+length]
                            if seg in segCounts3: segCounts3[seg] += 1
                            else: segCounts3[seg] = 1

        if BibleOrgSysGlobals.debugFlag: compressedRecord += '\n'
        bytesWritten = dictHTMLFile.write( compressedRecord.encode('UTF8') )
        #print( repr(lexeme), len(formattedRecord), len(compressedRecord), bytesWritten )
        chunkCount += 1

        lLexeme = lexeme.lower()
        indexEntry = lLexeme,fileOffset,bytesWritten
        createdIndex.append( indexEntry )
        for word in createReverseEntries( record ):
            reverseIndex.append( (word.lower(),indexEntry) )

        fileOffset += bytesWritten
        if fileOffset >= maxChunkBytes:
            dictHTMLFile.close()
            chunkList.append( (chunkNumber,chunkCount,) )
            fileOffset = 0
            chunkNumber += 1
            dictHTMLFile = open( destinationHTMLFilepathTemplate.format( chunkNumber ), 'wb' )
    dictHTMLFile.close()
    chunkList.append( (chunkNumber,chunkCount,) ) # How many entries in each chunk
    #print( "  Chunk list:", chunkList )
    print( "  {} compressed HTML chunks written".format( len(chunkList) ) )
    writeSDHeader( chunkList )

    if createdIndex: # Sort the main index and write it
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Sorting and writing main index..." )
        createdIndex = sorted(createdIndex)
        print( "    {} index entries created.".format( len(createdIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    reformatAndIndexStudentDict: " +  _("Exporting index to {}...").format( destinationIndexFilepath ) )
        with open( destinationIndexFilepath, 'wt' ) as jsonFile:
            json.dump( createdIndex, jsonFile, indent=jsonIndent )

    if reverseIndex: # Sort the reverse index and write it
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Sorting and writing reverse index..." )
        reverseIndex = sorted(reverseIndex)
        newReverseIndex = []
        for word,indexEntry in reverseIndex:
            #print( repr(word), indexEntry )
            found = False
            for ix in range(0, len(createdIndex) ):
                if createdIndex[ix] == indexEntry: found = True; break
            if found: newReverseIndex.append( (word,ix) )
            else: halt
        print( "    {} reverse index entries created.".format( len(newReverseIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    reformatAndIndexStudentDict: " +  _("Exporting reverse index to {}...").format( destinationReverseIndexFilepath ) )
        with open( destinationReverseIndexFilepath, 'wt' ) as jsonFile:
            json.dump( newReverseIndex, jsonFile, indent=jsonIndent )

    writeCompressions()
    if BibleOrgSysGlobals.verbosityLevel > 1:
        for key,count in usageCount.items():
            if count == 0: logging.error( "Compression code {} is unused".format( key ) )
            elif count < 20: logging.warning( "Compression code {} is rarely used".format( key ) )
            elif count < 100: logging.warning( "Compression code {} is under-used".format( key ) )

    if BibleOrgSysGlobals.verbosityLevel > 1:
        if segCounts1:
            print( "\n  Longest and most common words (with bytes to be saved in last column)" )
            got = []
            sortedWordCountList = sorted( segCounts1.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            printCount = 0
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                if not isSubstring:
                    print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                    printCount += 1
                got.append( word )
                if printCount > 50: break
        if segCounts2:
            print( "\n  Longest and most common sequences (before compression)" )
            got = []
            sortedWordCountList = sorted( segCounts2.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                got.append( word )
                if j > 50: break
        if segCounts3:
            print( "\n  Longest and most common sequences (after compression)" )
            got = []
            sortedWordCountList = sorted( segCounts3.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                got.append( word )
                if j > 50: break

        print( "  Compression ratio: " + str( round( bytesCompressed / bytesRaw, 3 ) ) )
        print( "    Raw bytes: " + str(bytesRaw) )
        print( "    Compressed bytes: " + str(bytesCompressed) )
    """
    private void loadAndFormatCurrentEntry() {
            Log.d("MSDict", "loadAndFormatCurrentEntry");
            String[] entryLines = loadCurrentEntry();
            //Log.d("MSDict", "got" + entryLines);
            String thisEntry = "";
            boolean haveNumberedList = false;
            for (int ix = 0; ix < entryLines.length; ix++) {
                    String thisLine = entryLines[ix];
                    int is = thisLine.indexOf(" ");
                    //Log.d("MSDict", "Line '" + thisLine + "'");
                    //Log.d("MSDict", "got index " + is);
                    String marker, text;
                    if (is==-1)
                    {
                            marker = thisLine;
                            text = "";
                    }
                    else {
                            marker = thisLine.substring(0, is);
                            text = thisLine.substring(is+1);
                    }
                    Log.d("MSDict", "got marker '" + marker + "'");
                    Log.d("MSDict", "got text '" + text + "'");
                    if (marker.equals("lx"))
                            thisEntry += "<h1><font size='32'>" + text + "</font></h1>";
                    else if (marker.equals("ph"))
                            thisEntry += "<br /><font size='20' color='olive'>/<i>" + text + "</i>/</font>";
                    else if (marker.equals("ps"))
                            thisEntry += "<br /><font size='20' color='red'>Part of speech: <b>" + text + "</b></font><br />";
                    else if (marker.equals("sn")) {
                            if (!haveNumberedList){
                                    haveNumberedList = true;
                            }
                            thisEntry += "<h2><font size='20' color='blue'>" + text + ".</h2>";
                    }
                    else if (marker.equals("de"))
                            thisEntry += "<br /><font size='20' color='magenta'>MS: <b>" + text + "</b></font>";
                    else if (marker.equals("re"))
                            /*thisEntry += "<br /><font size='20' color='red'>Not needed: <b>" + text + "</b></font>"*/;
                    else if (marker.equals("dv")) {
                            String thisField = "<br /><font size='20' color='blue'>Definition: <b>" + text + "</b></font>";
                            thisField = thisField.replaceAll("fb:(.+?)([ .])", "<u>$1</u>$2" );
                            thisEntry += thisField;
                    }
                    else if (marker.equals("xv1"))
                            thisEntry += "<br /><font size='20' color='silver'>Example sentence: <b>" + text + "</b></font>";
                    else if (marker.equals("xe1"))
                            thisEntry += "<br /><font size='20' color='orange'>Translation: <b>" + text + "</b></font>";
                    else if (marker.equals("sd"))
                            thisEntry += "<br /><font size='20' color='olive'>Source: <b>" + text + "</b></font>";
                    else if (marker.equals("nt"))
                            thisEntry += "<br /><font size='20' color='teal'>Note: <b>" + text + "</b></font>";
                    else if (marker.equals("so"))
                            thisEntry += "<br /><font size='20' color='purple'>Source: <b>" + text + "</b></font>";
                    else if (marker.equals("st"))
                            thisEntry += "<br /><font size='20' color='gray'>Status: <b>" + text + "</b></font>";
                    else if (marker.equals("dt"))
                            thisEntry += "<br /><font size='8' color='navy'>Last updated: <b>" + text + "</b></font>";
                    else {
                            Log.e("MSDict", "Unknown marker: '" + marker + "'");
                            thisEntry += "<br /><font size='40' color='red'>" + text + "</font>";
                    }
            }
            TextView myTextView = (TextView) findViewById(R.id.textView1);
            //myTextView.getSettings().setBuiltInZoomControls(true);
            Spanned sp = Html.fromHtml(thisEntry);
            myTextView.setText( sp );
            //myTextView.setText( thisEntry ); // Use this to reveal HTML codes
    """
    # end of reformatAndIndexStudentDict



def reformatAndIndexMainDict():
    """
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( "\nReformat and Index Main Dict..." )

    keyMarker = 'og'
    ignoreSFMs= 'ub'

    MDDataFormatVersion = 1
    jsonIndent = 0 # Keep files small for small phones
    maxChunkBytes = 650000; # Max bytes for the HTML chunk files (560 gives 4 relatively equal chunks)
    destinationHeaderFilepath = os.path.join( outputFolder, 'MS-MD.json' )
    destinationHTMLFilepathTemplate = os.path.join( outputFolder, 'MS-MD.{}.html' ) # Missing a chunk number
    destinationIndexFilepath = os.path.join( outputFolder, 'MS-MD-ix-html.json' )
    destinationReverseIndexFilepath = os.path.join( outputFolder, 'MS-MD-rev-ix.json' )
    compressionFilepath = os.path.join( outputFolder, 'MS-MD-cmpr.json' )

    segCounts1, segCounts2, segCounts3 = {}, {}, {}

    MDCompressions = (
        ('@A','<h1 class="Lexeme">'),
        ('@B','<p class="Variant">Variant: <span class="Variant">'),
        ('@C','<p class="Variant1">Variant 1: <span class="Variant1">'),
        ('@D','<p class="Variant2">Variant 2: <span class="Variant2">'), # under-used
        ('@E','<p class="VariantNote">Variant note: <span class="VariantNote">'), # rarely used
        ('@F','<p class="Phonemic">Phonemic: <span class="Phonemic">'),
        ('@G','<p class="Pronunciation">Pronunciation: <span class="Pronunciation">'), # under-used
        ('@H','<p class="LexemePOS">Lexeme part of speech: <span class="LexemePOS">'),
        ('@I','<p class="LexemeGloss">Lexeme gloss: <span class="LexemeGloss">'),

        ('@J','<p class="DonatedCebuano">From Cebuano: <span class="DonatedCebuano">'),
        ('@K','<p class="DonatedCebuano">From Cebuano</p>'), # under-used
        ('@L','<p class="DonatedEnglish">From English: <span class="DonatedEnglish">'),
        ('@M','<p class="DonatedSpanish">From Spanish: <span class="DonatedSpanish">'), # rarely used
        ('@N','<p class="DonatedSpanish">From Spanish</p>'), # under-used
        ('@O','<p class="ProtoForm">Proto form: <span class="ProtoForm">'),

        ('@P','<section class="Sense" id="'),
        ('@Q','"><span class="SenseNumber">'),
        ('@R','<p class="POS">Part of speech: <span class="POS">'),
        ('@S','<p class="ScientificName">Scientific name: <span class="ScientificName">'),

        ('@T','<p class="Gloss">'),
        #('@V','<span class="GlossIntroduction">'),
        ('~v','<p class="Gloss"><span class="GlossIntroduction">'),
        ('@W','<span class="MainGloss">'),
        ('~w','</span><span class="Extra">)</span> <span class="MainGloss">'),
        ('@X','<span class="CaseZ">'), # under-used
        ('@Y','<span class="Case">'), # under-used
        ('~y','</span><span class="Extra"> (</span><span class="Case">'),
        ('@Z','<span class="Affixation">'),
        ('~t','<span class="Extra">'),
        ('~u','<span class="Extra"> '),
        ('~z','</span><span class="Extra"> (</span><span class="Affixation">'),
        ('~p','<p class="Gloss"><span class="Extra">(</span><span class="Affixation">'),
        ('@x',' </span><span class="InflectedForm">'),
        ('~q','(</span><span class="InflectedForm">'),
        ('@y','/</span><span class="Variant">'),

        ('@b','<p class="MatigsalugDefinition">Matigsalug definition: <span class="MatigsalugDefinition">'),
        ('@c','<p class="GrammarNote">Grammar note: <span class="GrammarNote">'),
        ('@d','<p class="CulturalNote">Cultural note: <span class="CulturalNote">'),
        ('@e','<p class="Morphophonemics">Morphophonemics: <span class="Morphophonemics">'), # under-used

        ('@f','<p class="MatigsalugExampleSentence">Sentence: <span class="MatigsalugExampleSentence">'),
        ('@g','<p class="EnglishTranslationSentence">Translation: <span class="EnglishTranslationSentence">'),

        ('@V','<p class="EnglishIndex">English word(s): <span class="EnglishIndex">'),
        ('~r','; <span class="EnglishIndex">'),

        ('@h','<p class="SeeAlso">See also: <span class="SeeAlso">'),
        ('@i','<p class="Synonym">Synonym: <span class="Synonym">'),
        ('@j','<p class="OverlappingSynonym">Overlapping synonym: <span class="OverlappingSynonym">'),
        ('@k','<p class="Antonym">Antonym: <span class="Antonym">'),

        ('@l','<p class="SemanticClass">Semantic class: <span class="SemanticClass">'),
        ('@m','<p class="SemanticClass">DDP semantic class: <span class="SemanticClass">'),
        ('~s','; <span class="SemanticClass">'),

        ('@n','<p class="DataQuestion">Data question: <span class="DataQuestion">'),
        ('@o','<p class="Comment">Comment: <span class="Comment">'),
        ('@p','<p class="CreationDate">Created: <span class="CreationDate">'),
        ('@q','<p class="EditDate">Edited: <span class="EditDate">'),
        ('@r','<p class="UsageLevel">Usage level: <span class="UsageLevel">'),

        ('@s','</h1>'),
        #('@t','</p>'),
        ('@u','</span>'),
        ('@v','</section>'),
        ('@w','</span></p>'),

        ('@[','<sub>'),
        ('@]','</sub>'), # under-used
        ('~N','</sub></h1>'),
        ('`','<b>'),
        ('@}','</b>'),
        ('#','</b> '),
        ('~Z','</b> <b>'),
        ('@(','<i>'),
        ('@)','</i>'),
        ('~O','</i> '),

        ('^','eg&gt;&lt;'),
        ('*','&gt;&lt;ø-'),
        ('~o','for someone'),
        ('~P',' te '),
        ('~Q',' something'),
        ('~R','or something'),
        ('@1',' the '),
        ('@2',' ne '),
        ('@3',' ka'),
        ('@4','ing '),
        ('@5','/2009'),
        ('@.','/200'),
        ('@;','/201'),
        ('@6',' because '),
        ('@7','to '),
        ('~a','agent'),
        ('@8','an '),
        ('@9',' diyè te '),
        ('@+',' eg'),
        ('@-',' of '),
        ('@=','ang'),
        ('@_',' wey '),
        ('@!','location'),
        ('@0',' a '),
        ('~M',' and '),
        ('~S',' ne eg'),
        ('~T',' seini '),
        ('~U',' su '),
        ('~V',' iyan sika se '),
        ('~W',' seini ne lalag'),
        ('~X','to be'),
        ('~Y','egka'),

        ('~A','/Jan'),
        ('~B','/Feb'),
        ('~C','/Mar'),
        ('~D','/Apr'),
        ('~E','/May'),
        ('~F','/Jun'),
        ('~G','/Jul'),
        ('~H','/Aug'),
        ('~I','/Sep'),
        ('~J','/Oct'),
        ('~K','/Nov'),
        ('~L','/Dec'),
        )

    usageCount = {}
    codeSet, dataSet, reversedCompressions = [], [], []
    for shortString, longString in MDCompressions:
        usageCount[shortString] = 0
        if shortString in codeSet: # check for duplicates
            logging.critical( "Duplicate {} in compression dict".format( repr(shortString) ) )
            print( shortString, codeSet )
            halt
        codeSet.append( shortString )
        if longString in dataSet: # check for duplicates
            logging.critical( "Duplicate {} in compression dict".format( repr(longString) ) )
            print( longString, dataSet )
            halt
        dataSet.append( longString )
        if longString != '@':
            reversedCompressions.append( (longString,shortString,) )
    reversedCompressions = sorted( reversedCompressions, key=lambda s: -len(s[0]) ) # Longest string length first
    #print( len(reversedCompressions), reversedCompressions )


    def writeMDHeader( chunks ):
        """
        """
        headerDict = OrderedDict()
        headerDict['Data format version'] = MDDataFormatVersion
        headerDict['Conversion date'] = datetime.today().strftime("%Y-%m-%d")
        headerDict['Conversion program'] = ProgNameVersion
        headerDict['Number of chunks'] = len( chunks )
        for chunkNum, chunkEntries in chunks:
            #print( chunkNum, chunkEntries )
            headerDict['Chunk{}'.format(chunkNum)] = chunkEntries
        #print( headerDict )

        with open( destinationHeaderFilepath, 'wt' ) as jsonFile:
            json.dump( headerDict, jsonFile, indent=2 )
    # end of reformatAndIndexMainDict.writeSDHeader


    def writeCompressions():
        """
        """
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Writing compression entries..." )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    indexExistingMainDict " +  _("Exporting index to {}...").format( compressionFilepath ) )
        with open( compressionFilepath, 'wt' ) as jsonFile:
            #for compression in MDCompressions:
                #compFile.write( compression[0] + compression[1] + '\n' )
            json.dump( MDCompressions, jsonFile, indent=jsonIndent )
        print( "    {} compression entries written.".format( len(MDCompressions) ) )
    # end of reformatAndIndexMainDict.writeCompressions


    bytesRaw = bytesCompressed = 0
    def compress( entry ):
        """
        """
        nonlocal bytesRaw, bytesCompressed
        #print( repr(entry) ); halt
        assert( '@' not in entry )
        assert( '~' not in entry )
        #if '@' in entry:
            #result = result.replace( '@', '~~' )
            #usageCount['~~'] += 1

        bytesRaw += len( entry.encode('UTF8') ) # Keep a count
        result = entry
        for longString, shortString in reversedCompressions:
            if longString in result:
                result = result.replace( longString, shortString )
                usageCount[shortString] += 1
        bytesCompressed += len( result.encode('UTF8') )
        return result
    # end of reformatAndIndexMainDict.compress


    def decompress( entry ):
        """
        """
        result = entry
        for shortString, longString in MDCompressions:
            result = result.replace( shortString, longString )
        return result
    # end of reformatAndIndexMainDict.decompress


    def formatRecord( thisRecord ):
        """
        """
        assert( len(thisRecord) > 4 )
        assert( thisRecord[0][0] == keyMarker )
        assert( thisRecord[0][1][0] != '~' )
        htmlString = ""
        lastMarker = lastHTML = ''
        inASense = hadPOSOutsideSense = False
        senseNumber = 0
        endSenseHTML = '</section>'
        validFieldCount = 0
        word = gloss = glossParenthesis = saveForEnd = ""
        for originalMarker, originalText in thisRecord:
            marker, text = originalMarker, originalText

            if marker == keyMarker:
                assert( text )
                lexeme = text
                #print( "\n{}".format( lexeme ) )
            #if lexeme=='keen':
                #print( word, marker, repr(text), repr(gloss) )
            #print( word, marker, repr(text) )
            assert( marker )

            if marker in ('mn','mb','aMU','aMW','cp','loc','cu','o',):
                continue # We completely ignore these old CARLA fields

            if not text and marker not in ('ms','ds','dc',):
                logging.error( _("MainDictionary: Missing text for {} in {}").format( repr(marker), repr(lexeme) ) )
                halt

            # Exception characters for compression
            for shortString,longString in MDCompressions:
                if shortString[0] in text:
                #if shortString in text:
                    logging.critical( "{}:{} contains {}".format( marker, repr(text), repr(shortString) ) )
                    halt

            # Handle XML special characters
            text = text.replace( '"', '&quot;' )
            text = text.replace( '&', '&amp;' )
            text = text.replace( '<', '&lt;' )
            text = text.replace( '>', '&gt;' )

            # Handle some special MDF codes
            text = text.replace( '|{emdash}', '—' )
            text = text.replace( '|{endash}', '–' )
            text = text.replace( '|{~}', ' ' )

            # Handling bolding of some MDF fields
            text = re.sub( r'\|u{(.+?)}', r'<u>\1</u>', text )
            text = re.sub( r'\|fb{(.+?)}', r'<b>\1</b>', text )
            text = re.sub( r'fb:(.+?)([ .,/])', r'<b>\1</b>\2', text )
            text = re.sub( r'fb:(.+?)$', r'<b>\1</b>', text )
            if 'fb:' in text or 'fb{' in text: halt
            if '{' in text or '}' in text: halt
            #if '&' in text: halt # These seem to be displayed ok

            # Handle formatting of some character fields -- too lazy to test that these fields are in the correct order
            text = text.replace( '|d', '<sub>' ).replace( '|u', '</sub>' )
            text = text.replace( '|v', '<i>' ).replace( '|r', '</i>' )
            text = re.sub( r'\+(.+?)([ .,])', r'<b>\1</b>\2', text ) # +words in example sentences, etc.

            if 0: # Record word count stats -- do any text sequences in the given range of lengths
                minL, maxL = 3,25
                txtL = len(text)
                if txtL >= minL:
                    #print( txtL, repr(text) )
                    for ix in range( 0, txtL):
                        for length in range( minL, maxL+1 ):
                            if (ix+length) <= txtL:
                                seg = text[ix:ix+length]
                                #print( ' ', len(seg), repr(seg) )
                                if seg in segCounts1: segCounts1[seg] += 1
                                else: segCounts1[seg] = 1

            thisHTML = beforeText = ''
            if marker == 'og':
                pass # Ignore -- we only use this for the index
            elif marker == 'lx':
                word = text
                thisHTML = '<h1 class="Lexeme">{}</h1>'.format( word )
            elif marker == 'va':
                if gloss:
                    if lastMarker in ('oi','va','vd1','vd2','pn',):
                        beforeText = '/'
                    else: # shouldn't actually happen
                        assert( False )
                        beforeText = ' '
                        if not glossParenthesis:
                            beforeText += '('
                            glossParenthesis = '('
                    if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                    gloss += '<span class="Variant">{}</span>'.format( text )
                else: # not in a gloss field
                    thisHTML = '<p class="Variant">Variant: <span class="Variant">{}</span></p>'.format( text )
            elif marker == 'vd1':
                if gloss:
                    if lastMarker in ('oi','va','vd1','vd2','pn',):
                        beforeText = '/'
                    else: # shouldn't actually happen
                        assert( False )
                        beforeText = ' '
                        if not glossParenthesis:
                            beforeText += '('
                            glossParenthesis = '('
                    if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                    gloss += '<span class="Variant">{}</span>'.format( text )
                else: # not in a gloss field
                    thisHTML = '<p class="Variant1">Variant 1: <span class="Variant1">{}</span></p>'.format( text )
            elif marker == 'vd2':
                if gloss:
                    if lastMarker in ('oi','va','vd1','vd2','pn',):
                        beforeText = '/'
                    else: # shouldn't actually happen
                        assert( False )
                        beforeText = ' '
                        if not glossParenthesis:
                            beforeText += '('
                            glossParenthesis = '('
                    if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                    gloss += '<span class="Variant">{}</span>'.format( text )
                else: # not in a gloss field
                    thisHTML = '<p class="Variant2">Variant 2: <span class="Variant2">{}</span></p>'.format( text )
            elif marker == 've':
                thisHTML = '<p class="VariantNote">Variant note: <span class="VariantNote">{}</span></p>'.format( text )

            elif marker == 'ph':
                thisHTML = '<p class="Phonemic">Phonemic: <span class="Phonemic">{}</span></p>'.format( text )
            elif marker == 'pn':
                if gloss:
                    if lastMarker in ('oi','va','vd1','vd2','pn',):
                        beforeText = '/'
                    else: # shouldn't actually happen
                        assert( False )
                        beforeText = ' '
                        if not glossParenthesis:
                            beforeText += '('
                            glossParenthesis = '('
                    if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                    gloss += '<span class="Variant">{}</span>'.format( text )
                else: # not in a gloss field
                    thisHTML = '<p class="Pronunciation">Pronunciation: <span class="Pronunciation">{}</span></p>'.format( text )

            elif marker == 'lp':
                thisHTML = '<p class="LexemePOS">Lexeme part of speech: <span class="LexemePOS">{}</span></p>'.format( text )
            elif marker == 'lg':
                thisHTML = '<p class="LexemeGloss">Lexeme gloss: <span class="LexemeGloss">{}</span></p>'.format( text )

            elif marker == 'dc':
                if text:
                    thisHTML = '<p class="DonatedCebuano">From Cebuano: <span class="DonatedCebuano">{}</span></p>'.format( text )
                else:
                    thisHTML = '<p class="DonatedCebuano">From Cebuano</p>'
            elif marker == 'de':
                thisHTML = '<p class="DonatedEnglish">From English: <span class="DonatedEnglish">{}</span></p>'.format( text )
            elif marker == 'ds':
                if text:
                    thisHTML = '<p class="DonatedSpanish">From Spanish: <span class="DonatedSpanish">{}</span></p>'.format( text )
                else:
                    thisHTML = '<p class="DonatedSpanish">From Spanish</p>'

            elif marker == 'ms': # Main sense
                if inASense:
                    thisHTML += endSenseHTML
                    inASense = False
                if text: logging.error( "MS field for {} shouldn't have text {}".format( repr(word), repr(text) ) )
                if hadPOSOutsideSense: logging.error( "Word {} had some ps fields before the ms".format( repr(word) ) )
                senseNumber += 1
                thisHTML += '<section class="Sense" id="{}"><span class="SenseNumber">{}</span>'.format( senseNumber,senseNumber )
                inASense = True

            elif marker == 'ps':
                if not inASense: hadPOSOutsideSense = True
                thisHTML = '<p class="POS">Part of speech: <span class="POS">{}</span></p>'.format( text )

            elif marker in ('wg','ie','it','ic','ii','ixWBM','ixTIG','ixBKD','ixDIB','ixCAG','ixKIN','ixSAR','ixTAG',
                            'ixILN','ixOBO','ixCTM','ixTSY',):
                # pass # ignore -- used for reverse indexes only
                if gloss:
                    thisHTML = '<p class="Gloss">' + gloss + ('<span class="Extra">)</span>' if glossParenthesis=='(' else '') + '</p>'
                    gloss = glossParenthesis = ""
                if marker == 'ie':
                    if lastMarker == 'ie':
                        assert( lastHTML.endswith( '</p>' ) )
                        lastHTML = lastHTML[:-4] # Remove the p close tag
                        thisHTML += '; <span class="EnglishIndex">{}</span></p>'.format( text )
                    else:
                        thisHTML += '<p class="EnglishIndex">English word(s): <span class="EnglishIndex">{}</span></p>'.format( text )
            elif marker == 'sp':
                thisHTML = '<p class="ProtoForm">Proto form: <span class="ProtoForm">{}</span></p>'.format( text )
            elif marker == 'sn':
                thisHTML = '<p class="ScientificName">Scientific name: <span class="ScientificName">{}</span></p>'.format( text )

            elif marker == 'gli':
                assert( not gloss )
                gloss += '<span class="GlossIntroduction">{}</span>'.format( text )
            elif marker == 'gl':
                if glossParenthesis=='(':
                    gloss += '<span class="Extra">)</span>'
                    glossParenthesis = ""
                if gloss: gloss += ' '
                gloss += '<span class="MainGloss">{}</span>'.format( text )
            elif marker == 'oz':
                if gloss:
                    if not glossParenthesis:
                        beforeText += ' ('
                        glossParenthesis = '('
                else: # this is the first field in the gloss
                    beforeText += '('
                    glossParenthesis = '('
                if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                gloss += '<span class="CaseZ">{}</span>'.format( text )
            elif marker == 'oc':
                if gloss:
                    if not glossParenthesis:
                        beforeText += ' ('
                        glossParenthesis = '('
                    elif lastMarker == 'oz': beforeText += ' '
                    elif lastMarker in ('oi','va','vd1','vd2','pn',): beforeText += ' / '
                else: # this is the first field in the gloss
                    beforeText += '('
                    glossParenthesis = '('
                if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                gloss += '<span class="Case">{}</span>'.format( text )
            elif marker == 'oa':
                if gloss:
                    if not glossParenthesis:
                        beforeText += ' ('
                        glossParenthesis = '('
                    elif lastMarker == 'oc': beforeText += ' '
                    elif lastMarker in ('oi','va','vd1','vd2','pn',): beforeText += ' / '
                else: # this is the first field in the gloss
                    beforeText += '('
                    glossParenthesis = '('
                if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                gloss += '<span class="Affixation">{}</span>'.format( text )
            elif marker == 'oi':
                if gloss:
                    if not glossParenthesis:
                        beforeText += ' ('
                        glossParenthesis = '('
                    elif lastMarker == 'oa': beforeText += ' '
                    elif lastMarker in ('oi','va','vd1','vd2','pn',): beforeText += ' / '
                else: # this is the first field in the gloss
                    beforeText += '('
                    glossParenthesis = '('
                if beforeText: gloss += '<span class="Extra">{}</span>'.format( beforeText )
                gloss += '<span class="InflectedForm">{}</span>'.format( text )

            elif marker == 'df':
                if gloss:
                    thisHTML = '<p class="Gloss">' + gloss + ('<span class="Extra">)</span>' if glossParenthesis=='(' else '') + '</p>'
                    gloss = glossParenthesis = ""
                thisHTML += '<p class="MatigsalugDefinition">Matigsalug definition: <span class="MatigsalugDefinition">{}</span></p>'.format( text )

            elif marker == 'ex':
                if gloss:
                    thisHTML = '<p class="Gloss">' + gloss + ('<span class="Extra">)</span>' if glossParenthesis=='(' else '') + '</p>'
                    gloss = glossParenthesis = ""
                thisHTML += '<p class="MatigsalugExampleSentence">Sentence: <span class="MatigsalugExampleSentence">{}</span></p>'.format( text )
            elif marker == 'tr':
                thisHTML = '<p class="EnglishTranslationSentence">Translation: <span class="EnglishTranslationSentence">{}</span></p>'.format( text )
            elif marker == 't2':
                thisHTML = '<p class="TagalogTranslationSentence">Translation: <span class="TagalogTranslationSentence">{}</span></p>'.format( text )
            elif marker == 't3':
                thisHTML = '<p class="CebuanoTranslationSentence">Translation: <span class="CebuanoTranslationSentence">{}</span></p>'.format( text )
            elif marker == 't4':
                thisHTML = '<p class="IlocanoTranslationSentence">Translation: <span class="IlocanoTranslationSentence">{}</span></p>'.format( text )

            elif marker == 'eg':
                thisHTML = '<p class="GrammarNote">Grammar note: <span class="GrammarNote">{}</span></p>'.format( text )
            elif marker == 'ec':
                thisHTML = '<p class="CulturalNote">Cultural note: <span class="CulturalNote">{}</span></p>'.format( text )

            elif marker == 're':
                thisHTML = '<p class="SeeAlso">See also: <span class="SeeAlso">{}</span></p>'.format( text )
            elif marker == 'rf':
                thisHTML = '<p class="SeeAlso">See also: <span class="SeeAlso">{}</span></p>'.format( text )
            elif marker == 'ra':
                thisHTML = '<p class="Antonym">Antonym: <span class="Antonym">{}</span></p>'.format( text )
            elif marker == 'rs':
                thisHTML = '<p class="Synonym">Synonym: <span class="Synonym">{}</span></p>'.format( text )
            elif marker == 'ro':
                thisHTML = '<p class="OverlappingSynonym">Overlapping synonym: <span class="OverlappingSynonym">{}</span></p>'.format( text )
            elif marker == 'co':
                thisHTML = '<p class="Comment">Comment: <span class="Comment">{}</span></p>'.format( text )
            elif marker == 'rm': # What's this???
                pass # Just ignore
            elif marker == 'rg': # What's this???
                pass # Just ignore
            elif marker == 'li': # What's this???
                pass # Just ignore

            elif marker == 'mo':
                thisHTML = '<p class="Morphophonemics">Morphophonemics: <span class="Morphophonemics">{}</span></p>'.format( text )

            elif marker == 'sc':
                if lastMarker == 'sc':
                    assert( lastHTML.endswith( '</p>' ) )
                    lastHTML = lastHTML[:-4] # Remove the p close tag
                    thisHTML += '; <span class="SemanticClass">{}</span></p>'.format( text )
                else:
                    thisHTML = '<p class="SemanticClass">Semantic class: <span class="SemanticClass">{}</span></p>'.format( text )
            elif marker == 'ddp':
                if lastMarker == 'ddp':
                    assert( lastHTML.endswith( '</p>' ) )
                    lastHTML = lastHTML[:-4] # Remove the p close tag
                    thisHTML += '; <span class="SemanticClass">{}</span></p>'.format( text )
                else:
                    thisHTML = '<p class="SemanticClass">DDP semantic class: <span class="SemanticClass">{}</span></p>'.format( text )
            elif marker == 'ul':
                thisHTML = '<p class="UsageLevel">Usage level: <span class="UsageLevel">{}</span></p>'.format( text )

            elif marker == 'dq':
                thisHTML += '<p class="DataQuestion">Data question: <span class="DataQuestion">{}</span></p>'.format( text )

            elif marker == 'cd':
                saveForEnd += '<p class="CreationDate">Created: <span class="CreationDate">{}</span></p>'.format( text )
            elif marker == 'ud':
                saveForEnd += '<p class="EditDate">Edited: <span class="EditDate">{}</span></p>'.format( text )

            elif marker == 'ng': # What's this???
                pass # Just ignore
            elif marker == 'zo':
                # pass # Just ignore
                if gloss:
                    thisHTML = '<p class="Gloss">' + gloss + ('<span class="Extra">)</span>' if glossParenthesis=='(' else '') + '</p>'
                    gloss = glossParenthesis = ""
            else:
                logging.critical( "Didn't process {} {} for {} yet".format( repr(marker), repr(originalText), repr(lexeme) ) )
                if BibleOrgSysGlobals.debugFlag: halt

            htmlString += lastHTML
            lastMarker = marker
            lastHTML = thisHTML
            if marker not in ('lx','st','dt'): # then it's actually some information
                validFieldCount += 1

        # Do some checking
        if gloss: print( repr(word), repr(gloss) )
        assert( not gloss ) # Should be none left at the end
        if senseNumber == 1: logging.warning( "Word {} only has one sense".format( repr(word) ) )
        #assert( senseNumber != 1 )

        # Do the finishing off
        htmlString += lastHTML + saveForEnd
        #if lexeme=='keen': print( htmlString ); halt
        if inASense:
            htmlString += endSenseHTML
            inASense = False
        if validFieldCount < 1:
            #print( "questionable", validFieldCount, lexeme, htmlString )
            return None
        #print( lexeme, htmlString )
        return lexeme, htmlString
    # end of reformatAndIndexMainDict.formatRecord

    def createReverseEntries( thisRecord ):
        """
        """
        results = set()
        for marker, text in thisRecord:
            #print( marker, text )
            if marker == keyMarker:
                assert( text )
                lexeme = text
                #print( "\n{}".format( lexeme ) )
            elif marker == 'ie':
                #assert( text )
                if text:
                    results.add( text ) # This is a set so duplicates are automatically removed
                    adjText = text.lower()
                    results.add( adjText )
        #print( "results", results )
        return results
    # end of reformatAndIndexMainDict.createReverseEntries

    # Read the existing records into memory
    recordsDB = SFMRecords()
    recordsDB.read( mainDictSourceFilepath, keyMarker, ignoreSFMs=ignoreSFMs )
    print( "  {} records read from {}".format( len(recordsDB.records), mainDictSourceFilepath ) )
    if 0: # Display some sample records
        for i, r in enumerate(recordsDB.records):
            print ( i, r)
            if i>3: break
        print( '...\n',len(recordsDB.records)-1, recordsDB.records[-1]) # Display the last record

    # Format each record into HTML and write it into a new file, along with an index entry
    createdIndex, reverseIndex = [], []
    fileOffset = chunkCount = 0
    chunkNumber, chunkList = 1, []
    dictHTMLFile = open( destinationHTMLFilepathTemplate.format( chunkNumber ), 'wb' )
    for record in recordsDB.records:
        if record[0][0] != keyMarker: continue # Ignore header record
        if record[0][1][0] == '~': continue # Ignore special records
        if record[0][1].startswith( 'z.' ): continue # Ignore these

        formatRecordResult = formatRecord( record )
        if formatRecordResult is None: continue
        lexeme, formattedRecord = formatRecordResult
        if 0:
            minL, maxL = 10,70
            txtL = len(formattedRecord)
            if txtL >= minL:
                for ix in range( 0, txtL):
                    for length in range( minL, maxL+1 ):
                        if (ix+length) <= txtL:
                            seg = formattedRecord[ix:ix+length]
                            if seg in segCounts2: segCounts2[seg] += 1
                            else: segCounts2[seg] = 1

        compressedRecord = compress( formattedRecord )
        checkRecord = decompress( compressedRecord )
        if checkRecord != formattedRecord:
            logging.critical( "MainDict: compression error!" )
            print( '\nCompressed', len(compressedRecord), repr(compressedRecord) )
            print( '\nDecompressed', len(checkRecord), repr(checkRecord) )
            print( '\nOriginal', len(formattedRecord), repr(formattedRecord) )
            for ix in range( 0, min( len(checkRecord), len(formattedRecord) ) ):
                if checkRecord[ix] != formattedRecord[ix]: break
            print( '\nDecompressed before', len(checkRecord[:ix]), repr(checkRecord[:ix]) )
            print( '\nOriginal before', len(formattedRecord[:ix]), repr(formattedRecord[:ix]) )
            print( '\nDecompressed error', len(checkRecord[ix:]), repr(checkRecord[ix:]) )
            print( '\nOriginal error', len(formattedRecord[ix:]), repr(formattedRecord[ix:]) )
            halt
        if 0:
            minL, maxL = 4,60
            txtL = len(compressedRecord)
            if txtL >= minL:
                for ix in range( 0, txtL):
                    for length in range( minL, maxL+1 ):
                        if (ix+length) <= txtL:
                            seg = compressedRecord[ix:ix+length]
                            if seg in segCounts3: segCounts3[seg] += 1
                            else: segCounts3[seg] = 1

        if BibleOrgSysGlobals.debugFlag: compressedRecord += '\n'
        bytesWritten = dictHTMLFile.write( compressedRecord.encode('UTF8') )
        #print( repr(lexeme), len(formattedRecord), len(compressedRecord), bytesWritten )
        chunkCount += 1

        lLexeme = lexeme.lower()
        indexEntry = lLexeme,fileOffset,bytesWritten
        createdIndex.append( indexEntry )
        for word in createReverseEntries( record ):
            reverseIndex.append( (word.lower(),indexEntry) )

        fileOffset += bytesWritten
        if fileOffset >= maxChunkBytes:
            dictHTMLFile.close()
            chunkList.append( (chunkNumber,chunkCount,) )
            fileOffset = 0
            chunkNumber += 1
            dictHTMLFile = open( destinationHTMLFilepathTemplate.format( chunkNumber ), 'wb' )
    dictHTMLFile.close()
    chunkList.append( (chunkNumber,chunkCount,) ) # How many entries in each chunk
    print( "  {} compressed HTML chunks written".format( len(chunkList) ) )
    #print( "  Chunk list:", chunkList )
    writeMDHeader( chunkList )

    if createdIndex: # Sort the main index and write it
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Sorting and writing main index..." )
        createdIndex = sorted(createdIndex)
        print( "    {} index entries created.".format( len(createdIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    reformatAndIndexMainDict: " +  _("Exporting index to {}...").format( destinationIndexFilepath ) )
        with open( destinationIndexFilepath, 'wt' ) as jsonFile:
            json.dump( createdIndex, jsonFile, indent=jsonIndent )

    if reverseIndex: # Sort the reverse index and write it
        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( "  Sorting and writing reverse index..." )
        reverseIndex = sorted(reverseIndex)
        newReverseIndex = []
        for word,indexEntry in reverseIndex:
            #print( repr(word), indexEntry )
            found = False
            for ix in range(0, len(createdIndex) ):
                if createdIndex[ix] == indexEntry: found = True; break
            if found: newReverseIndex.append( (word,ix) )
            else: halt
        print( "    {} reverse index entries created.".format( len(newReverseIndex) ) )
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "    reformatAndIndexMainDict: " +  _("Exporting reverse index to {}...").format( destinationReverseIndexFilepath ) )
        with open( destinationReverseIndexFilepath, 'wt' ) as jsonFile:
            json.dump( newReverseIndex, jsonFile, indent=jsonIndent )

    writeCompressions()
    if BibleOrgSysGlobals.verbosityLevel > 1:
        for key,count in usageCount.items():
            if count == 0: logging.error( "Compression code {} is unused".format( key ) )
            elif count < 20: logging.warning( "Compression code {} is rarely used".format( key ) )
            elif count < 100: logging.warning( "Compression code {} is under-used".format( key ) )

    if BibleOrgSysGlobals.verbosityLevel > 1:
        if segCounts1:
            print( "\n  Longest and most common words (with bytes to be saved in last column)" )
            got = []
            sortedWordCountList = sorted( segCounts1.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            printCount = 0
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                if not isSubstring:
                    print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                    printCount += 1
                got.append( word )
                if printCount > 80: break
        if segCounts2:
            print( "\n  Longest and most common sequences (before compression)" )
            got = []
            sortedWordCountList = sorted( segCounts2.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                got.append( word )
                if j > 80: break
        if segCounts3:
            print( "\n  Longest and most common sequences (after compression)" )
            got = []
            sortedWordCountList = sorted( segCounts3.items(), key=lambda s: (len(s[0])-2)*s[1] if len(s[0])>2 else 0, reverse=True )
            for j, (word,count) in enumerate( sortedWordCountList ):
                isSubstring = False
                for gotWord in got:
                    if word in gotWord: isSubstring = True; break
                print( '    ' if isSubstring else '  ', j, repr(word), count, (len(word)-2)*count )
                got.append( word )
                if j > 80: break

        print( "  Compression ratio: " + str( round( bytesCompressed / bytesRaw, 3 ) ) )
        print( "    Raw bytes: " + str(bytesRaw) )
        print( "    Compressed bytes: " + str(bytesCompressed) )
    # end of reformatAndIndexMainDict


def main():
    """ Run the main script
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( "\nStarting " + ProgNameVersion + '...' )
    if BibleOrgSysGlobals.debugFlag: print( "\nStarting " + ProgNameVersion + ' in debug mode...' )

    if BibleOrgSysGlobals.verbosityLevel > 2:
        print( '  This program comes with ABSOLUTELY NO WARRANTY.' )
        print( '  It is free software, and you are welcome to redistribute it under certain conditions.' )
        print( "  See the license in file 'gpl-3.0.txt' for more details.\n" )

    #indexExistingStudentDict()
    #indexExistingMainDict()

    reformatAndIndexStudentDict()
    reformatAndIndexMainDict()
# end of main

if __name__ == '__main__':
    import BibleOrgSysGlobals

    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    main()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of MakeIndexesForDictionaries.py
