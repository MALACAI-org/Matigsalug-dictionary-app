package info.MLCA.MSDict

import java.io.InputStream
import java.util.ArrayList

import junit.framework.Assert

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import android.preference.PreferenceManager
import android.util.Log

class CombinedDict(//private String mDictType;
        private val mActivity: Activity, // private WindowManager mWindowManager;
        private val mMyGlobals: MyGlobals) {
    private val mContext: Context
    private var mSharedPrefs: SharedPreferences? = null
    private var mEditor: SharedPreferences.Editor? = null

    private val gotMDHeader = false
    private val gotSDHeader = false
    private var mMDMainIndex: MainIndex? = null
    private var mSDMainIndex: MainIndex? = null
    private var mMDReverseIndex: ReverseIndex? = null
    private var mSDReverseIndex: ReverseIndex? = null
    private var mMDJsonCompressionDict: JSONArray? = null
    private var mSDJsonCompressionDict: JSONArray? = null
    private var mMDEnabledFlag: Boolean = false
    private var mSDEnabledFlag: Boolean = false
    private var mReverseFlag: Boolean = false
    private var mCurrentDict: String? = null
    private var mLgViewFlag: Boolean = false // temp

    // Used to find how many entries in the index
    //	so we first have to determine which index they mean
    // never used
    val length: Int
        get() {
            mCurrentDict = mSharedPrefs!!.getString("currentDict", "")
            mReverseFlag = mSharedPrefs!!.getBoolean("reverseFlag", false)
            Log.d(TAG, "getLength for $mCurrentDict $mReverseFlag")

            if (mCurrentDict == "MD") {
                if (mReverseFlag) {
                    if (mMDReverseIndex == null)
                        mMDReverseIndex = ReverseIndex("MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                    return mMDReverseIndex!!.length
                } else {
                    if (mMDMainIndex == null)
                        mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                    return mMDMainIndex!!.length
                }
            }
            if (mCurrentDict == "SD") {
                if (mReverseFlag) {
                    if (mSDReverseIndex == null)
                        mSDReverseIndex = ReverseIndex("SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                    return mSDReverseIndex!!.length
                } else {
                    if (mSDMainIndex == null)
                        mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                    return mSDMainIndex!!.length
                }
            }
            return -1
        } // end of getLength

    init {
        Log.d(TAG, "constructor")
        mContext = mActivity.applicationContext
    }// mWindowManager = mActivity.getWindowManager();
    // end of constructor

    fun loadDictHeader(dictType: String) {
        Log.d(TAG, "loadDictHeader " + dictType)
        val mJsonHeader = mMyGlobals.loadJSONObjectFromAssetFile(headerFilenameTemplate.replace("dd", dictType))
        var dataFormatVersion = -1
        var numChunks = 0
        var conversionDate: String? = null
        try {
            dataFormatVersion = mJsonHeader!!.getInt("Data format version")
            conversionDate = mJsonHeader.getString("Conversion date")
            numChunks = mJsonHeader.getInt("Number of chunks")
        } catch (e: JSONException) {
            Log.e(TAG, "json object exception", e)
            e.printStackTrace()
        }

        //Log.d(TAG, "dataFormatVersion is "+dataFormatVersion);
        //Log.d(TAG, "conversionDate is "+conversionDate);
        //Log.d(TAG, "numChunks is "+numChunks);
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        if (mEditor == null)
            mEditor = mSharedPrefs!!.edit()
        mEditor!!.putInt(dictType + "dataFormatVersion", dataFormatVersion)
        mEditor!!.putString(dictType + "conversionDate", conversionDate)
        mEditor!!.putInt(dictType + "numChunks", numChunks)
        // Now get the actual chunk details
        var wordLimit: Int
        for (chunkNumber in 1..numChunks) {
            wordLimit = -1
            try {
                wordLimit = mJsonHeader!!.getInt("Chunk" + chunkNumber)
            } catch (e: JSONException) {
                Log.e(TAG, "json chunk object exception", e)
                e.printStackTrace()
            }

            //Log.d(TAG, "C"+chunkNumber+" is "+wordLimit);
            mEditor!!.putInt(dictType + "C" + chunkNumber, wordLimit)
        }
        mEditor!!.commit()
    } // end of loadDictHeader

    private fun getUserPreferences() {
        Log.d(TAG, "getUserPreferences")
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(mActivity)
        mMDEnabledFlag = defaultSharedPrefs.getBoolean("mdEnabled", true)
        mSDEnabledFlag = defaultSharedPrefs.getBoolean("sdEnabled", true)
        mLgViewFlag = defaultSharedPrefs.getBoolean("linguisticView", false)
        Log.d(TAG, " User prefs MD:$mMDEnabledFlag SD:$mSDEnabledFlag LV:$mLgViewFlag")
    }

    private fun getDictEnabledFlags() {
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        //mMDEnabledFlag = mSharedPrefs.getBoolean("mdEnabled", true);
        //mSDEnabledFlag = mSharedPrefs.getBoolean("sdEnabled", true);
        getUserPreferences()
        if (mMDEnabledFlag && !gotMDHeader) loadDictHeader("MD")
        if (mSDEnabledFlag && !gotSDHeader) loadDictHeader("SD")
    } // end of getDictEnabledFlags

    protected fun getIndexEntry(ix: Int): JSONArray? {
        // Log.d(TAG, "getIndexEntry "+ix + " " + reverseFlag);
        mCurrentDict = mSharedPrefs!!.getString("currentDict", "")
        mReverseFlag = mSharedPrefs!!.getBoolean("reverseFlag", false)
        //Log.d(TAG,"getIndexEntry for "+mCurrentDict+" "+mReverseFlag);

        if (mCurrentDict == "MD") {
            if (mReverseFlag) {
                return mMDReverseIndex!!.getIndexEntry(ix)
            } else {
                if (mMDMainIndex == null)
                    mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                return mMDMainIndex!!.getIndexEntry(ix)
            }
        }
        if (mCurrentDict == "SD") {
            if (mReverseFlag) {
                return mSDReverseIndex!!.getIndexEntry(ix)
            } else {
                if (mSDMainIndex == null)
                    mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                return mSDMainIndex!!.getIndexEntry(ix)
            }
        }
        return null // never used
    } // end of getIndexEntry

    fun findInIndex(vernacularFlag: Boolean, searchString: String): DualInts? {
        // Assuming we know the intended language of the search string,
        // 	searches in the available indexes for the given word (or part word)
        // Returns null if not found
        // Returns (indexNumber, reverseIndexNumber or -1) if a match was found
        Log.d(TAG, "findInIndex vf=$vernacularFlag '$searchString'")
        getDictEnabledFlags() // They might have changed
        //if (mSharedPrefs == null)
        //	mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0);
        //mReverseFlag = mSharedPrefs.getBoolean("reverseFlag", false);

        if (vernacularFlag) {
            if (mMDEnabledFlag) {
                Log.d(TAG, " MD findInIndex")
                if (mMDMainIndex == null)
                    mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                val result = mMDMainIndex!!.findInIndex(searchString)
                if (result != -1) {
                    val mCurrentDict = mMyGlobals.setCurrentDict("MD")
                    return DualInts(result, -1)
                }
            }
            if (mSDEnabledFlag) {
                Log.d(TAG, " SD reverse findInIndex")
                if (mSDReverseIndex == null)
                    mSDReverseIndex = ReverseIndex("SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                val result = mSDReverseIndex!!.findInIndex(searchString)
                if (result != null) {
                    val mCurrentDict = mMyGlobals.setCurrentDict("SD")
                    return result
                }
            }
        } else { // not a vernacular search
            if (mSDEnabledFlag) {
                Log.d(TAG, " SD findInIndex")
                if (mSDMainIndex == null)
                    mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                val result = mSDMainIndex!!.findInIndex(searchString)
                if (result != -1) {
                    val mCurrentDict = mMyGlobals.setCurrentDict("SD")
                    return DualInts(result, -1)
                }
            }
            if (mMDEnabledFlag) {
                Log.d(TAG, " MD reverse findInIndex")
                if (mMDReverseIndex == null)
                    mMDReverseIndex = ReverseIndex("MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                val result = mMDReverseIndex!!.findInIndex(searchString)
                if (result != null) {
                    val mCurrentDict = mMyGlobals.setCurrentDict("MD")
                    return result
                }
            }
        }
        return null
    } // end of findInIndex1

    fun findInIndex(searchString: String): DualInts? {
        // If we don't know the intended language of the search string,
        // Searches in the available indexes for the given word (or part word)
        // 	Returns null if not found
        //	Returns (indexNumber, reverseIndexNumber or -1) if a match was found
        Log.d(TAG, "findInIndex '$searchString'")
        getDictEnabledFlags() // They might have changed
        //if (mSharedPrefs == null)
        //	mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0);
        //mReverseFlag = mSharedPrefs.getBoolean("reverseFlag", false);

        if (mMDEnabledFlag) {
            Log.d(TAG, " MD findInIndex")
            if (mMDMainIndex == null)
                mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
            val result = mMDMainIndex!!.findInIndex(searchString)
            if (result != -1) {
                val mCurrentDict = mMyGlobals.setCurrentDict("MD")
                return DualInts(result, -1)
            }
        }
        if (mSDEnabledFlag) {
            Log.d(TAG, " SD findInIndex")
            if (mSDMainIndex == null)
                mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
            val result = mSDMainIndex!!.findInIndex(searchString)
            if (result != -1) {
                val mCurrentDict = mMyGlobals.setCurrentDict("SD")
                return DualInts(result, -1)
            }
        }
        if (mMDEnabledFlag) {
            Log.d(TAG, " MD reverse findInIndex")
            if (mMDReverseIndex == null)
                mMDReverseIndex = ReverseIndex("MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
            val result = mMDReverseIndex!!.findInIndex(searchString)
            if (result != null) {
                val mCurrentDict = mMyGlobals.setCurrentDict("MD")
                return result
            }
        }
        if (mSDEnabledFlag) {
            Log.d(TAG, " SD reverse findInIndex")
            if (mSDReverseIndex == null)
                mSDReverseIndex = ReverseIndex("SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
            val result = mSDReverseIndex!!.findInIndex(searchString)
            if (result != null) {
                val mCurrentDict = mMyGlobals.setCurrentDict("SD")
                return result
            }
        }
        return null
    } // end of findInIndex2

    fun loadFirstLetters(vernacularFlag: Boolean, list: ArrayList<String>): Boolean {
        // Load the first letters into the given array list
        //	and return the reverse flag
        Log.d(TAG, "loadFirstLetters " + vernacularFlag)
        getDictEnabledFlags() // They might have changed

        if (vernacularFlag) {
            if (mMDEnabledFlag) {
                if (mMDMainIndex == null)
                    mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                mMDMainIndex!!.loadFirstLetters(list)
                mCurrentDict = mMyGlobals.setCurrentDict("MD")
                mReverseFlag = false
            } else if (mSDEnabledFlag) {
                if (mSDReverseIndex == null)
                    mSDReverseIndex = ReverseIndex("SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                mSDReverseIndex!!.loadFirstLetters(list)
                mCurrentDict = mMyGlobals.setCurrentDict("SD")
                mReverseFlag = true
            }
        } else { // not vernacularFlag
            if (mSDEnabledFlag) {
                if (mSDMainIndex == null)
                    mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                mSDMainIndex!!.loadFirstLetters(list)
                mCurrentDict = mMyGlobals.setCurrentDict("SD")
                mReverseFlag = false
            } else if (mMDEnabledFlag) {
                if (mMDReverseIndex == null)
                    mMDReverseIndex = ReverseIndex("MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                mMDReverseIndex!!.loadFirstLetters(list)
                mCurrentDict = mMyGlobals.setCurrentDict("MD")
                mReverseFlag = true
            }
        }
        // Save the dictionary info
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        if (mEditor == null)
            mEditor = mSharedPrefs!!.edit()
        mEditor!!.putString("currentDict", mCurrentDict)
        mEditor!!.putBoolean("reverseFlag", mReverseFlag)
        Log.d(TAG, "loadFirst letters set rf=$mReverseFlag cd=$mCurrentDict")
        return mReverseFlag
    } // end of loadFirstLetters

    fun loadWordsForLetter(firstLetter: String, list: ArrayList<String>): Int {
        Log.d(TAG, "loadWordsForLetter '$firstLetter'")
        val vernacularFlag = mSharedPrefs!!.getBoolean("vernacularFlag", false)
        mCurrentDict = mSharedPrefs!!.getString("currentDict", "")

        if (vernacularFlag) {
            if (mCurrentDict == "MD") return mMDMainIndex!!.loadWordsForLetter(firstLetter, list)
            if (mCurrentDict == "SD") return mSDReverseIndex!!.loadWordsForLetter(firstLetter, list)
        } else { // not vernacular
            if (mCurrentDict == "SD") return mSDMainIndex!!.loadWordsForLetter(firstLetter, list)
            if (mCurrentDict == "MD") return mMDReverseIndex!!.loadWordsForLetter(firstLetter, list)
        }
        return -1
    } // end of loadWordsForLetter

    fun commitSearchParameters(searchWord: String, ix: Int, rix: Int) {
        var searchWord = searchWord
        // Assumes that currentDict is already set
        Log.d(TAG, "commitSearchParameters '$searchWord' $ix $rix")

        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        if (mEditor == null)
            mEditor = mSharedPrefs!!.edit()
        mReverseFlag = rix != -1
        mEditor!!.putBoolean("reverseFlag", mReverseFlag)

        // Possibly the found word was only part of the search word
        var indexWord = searchWord
        mCurrentDict = mSharedPrefs!!.getString("currentDict", "")
        if (mCurrentDict == "MD") {
            if (mReverseFlag) {
                val indexEntry = mMDReverseIndex!!.getIndexEntry(rix)
                try {
                    indexWord = indexEntry!!.getString(0)
                } catch (e: JSONException) {
                    Log.e(TAG, "Couldn't read MD reverse index", e)
                    // e.printStackTrace();
                }

            } else {
                if (mMDMainIndex == null)
                    mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                val indexEntry = mMDMainIndex!!.getIndexEntry(ix)
                try {
                    indexWord = indexEntry!!.getString(0)
                } catch (e: JSONException) {
                    Log.e(TAG, "Couldn't read MD main index", e)
                    // e.printStackTrace();
                }

            }
        }
        if (mCurrentDict == "SD") {
            if (mReverseFlag) {
                val indexEntry = mSDReverseIndex!!.getIndexEntry(rix)
                try {
                    indexWord = indexEntry!!.getString(0)
                } catch (e: JSONException) {
                    Log.e(TAG, "Couldn't read SD reverse index", e)
                    // e.printStackTrace();
                }

            } else {
                if (mSDMainIndex == null)
                    mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                val indexEntry = mSDMainIndex!!.getIndexEntry(ix)
                try {
                    indexWord = indexEntry!!.getString(0)
                } catch (e: JSONException) {
                    Log.e(TAG, "Couldn't read SD main index", e)
                    // e.printStackTrace();
                }

            }
        }
        if (indexWord != searchWord)
            searchWord += " → " + indexWord
        mEditor!!.putString("searchWord", searchWord)

        mEditor!!.putInt("indexNum", ix)
        mEditor!!.putInt("reverseIndexNum", rix) // -1 if not applicable
        var fileReference: FileReference? = null
        if (mCurrentDict == "MD") {
            if (mMDMainIndex == null)
                mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
            fileReference = mMDMainIndex!!.getFileReference(ix)
        } else if (mCurrentDict == "SD") {
            if (mSDMainIndex == null)
                mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
            fileReference = mSDMainIndex!!.getFileReference(ix)
        }
        mEditor!!.putLong("fileOffset", fileReference!!.offset)
        mEditor!!.putInt("recordLength", fileReference.length)
        mEditor!!.commit() // Commit the changes
    } // end of commitSearchParameters

    fun commitBrowseParameters(reverseFlag: Boolean, xIx: Int) {
        Log.d(TAG, "commitBrowseParameters $reverseFlag $xIx")
        mReverseFlag = reverseFlag

        Assert.assertTrue(xIx != -1)
        var ix = -1
        var rix = -1
        if (reverseFlag)
            rix = xIx
        else
            ix = xIx // not using reverse index
        Assert.assertTrue(ix == -1 || rix == -1)

        val mCurrentDict = mSharedPrefs!!.getString("currentDict", null)
        Assert.assertNotNull(mCurrentDict)

        /*if (mCurrentDict.equals("MD") ) {
			if ( mReverseFlag ) {
				if ( mMDReverseIndex == null)
					mMDReverseIndex = new ReverseIndex( "MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals);
			} else { // not reverse index
				if ( mMDMainIndex == null)
					mMDMainIndex = new MainIndex( "MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals);
			}
		} else if (mCurrentDict.equals("SD") ) {
			if ( mReverseFlag ) {
				if ( mSDReverseIndex == null)
					mSDReverseIndex = new ReverseIndex( "SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals);
			} else { // not reverse index
				if ( mSDMainIndex == null)
					mSDMainIndex = new MainIndex( "SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals);
			}
		}*/

        var indexWord: String? = null
        if (mReverseFlag) { // got to do a bit extra here
            Assert.assertTrue(rix != -1)
            var indexEntry: JSONArray? = null
            if (mCurrentDict == "MD") {
                if (mMDReverseIndex == null)
                    mMDReverseIndex = ReverseIndex("MD", reverseIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
                indexEntry = mMDReverseIndex!!.getIndexEntry(rix)
            } else if (mCurrentDict == "SD") {
                if (mSDReverseIndex == null)
                    mSDReverseIndex = ReverseIndex("SD", reverseIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
                indexEntry = mSDReverseIndex!!.getIndexEntry(rix)
            }
            Log.d(TAG, "commitBrowseParameters(reverse) got ie " + indexEntry!!)
            try {
                indexWord = indexEntry.getString(0)
                ix = indexEntry.getInt(1)
            } catch (e: JSONException) {
                Log.e(TAG, "Couldn't read main index", e)
                // e.printStackTrace();
            }

        }

        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        if (mEditor == null)
            mEditor = mSharedPrefs!!.edit()
        mEditor!!.putString("searchWord", indexWord)
        mEditor!!.putInt("indexNum", ix)
        mEditor!!.putInt("reverseIndexNum", rix) // -1 if not applicable
        var fileReference: FileReference? = null
        if (mCurrentDict == "MD") {
            if (mMDMainIndex == null)
                mMDMainIndex = MainIndex("MD", mainIndexFilenameTemplate.replace("dd", "MD"), mMyGlobals)
            fileReference = mMDMainIndex!!.getFileReference(ix)
        } else if (mCurrentDict == "SD") {
            if (mSDMainIndex == null)
                mSDMainIndex = MainIndex("SD", mainIndexFilenameTemplate.replace("dd", "SD"), mMyGlobals)
            fileReference = mSDMainIndex!!.getFileReference(ix)
        }
        mEditor!!.putLong("fileOffset", fileReference!!.offset)
        mEditor!!.putInt("recordLength", fileReference.length)
        mEditor!!.commit() // Commit the changes
    } // end of commitBrowseParameters

    private fun loadRawEntry(dictType: String, indexNum: Int, fileOffset: Long, recordLength: Int): String? {
        // Log.d(TAG,"loadRawEntry from "+indexNum+" "+fileOffset+":"+recordLength);
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(MyGlobals.PREFS_NAME, 0)

        // First, we have to find what chunk it's in
        val numChunks = mSharedPrefs!!.getInt(dictType + "numChunks", -1)
        var chunkNumber: Int
        chunkNumber = 1
        while (chunkNumber <= numChunks) {
            val wordLimit = mSharedPrefs!!.getInt(dictType + "C" + chunkNumber, -1)
            // Log.d(TAG,"For chunk"+chunkNumber+" got "+wordLimit);
            if (indexNum < wordLimit) {
                // Log.d(TAG,
                // "Break at "+chunkNumber+" "+wordLimit+" for "+indexNum);
                break
            }
            chunkNumber++
        }
        // Log.d(TAG,"For "+indexNum+" got chunk: "+chunkNumber);
        val dictFilename = dictionaryFilenameTemplate
                .replace("dd", dictType)
                .replace("x", chunkNumber.toString())
        // Log.d(TAG,"For "+indexNum+" got filename: "+dictFilename);

        // Now load the compressed entry
        // from the right portion of the right file
        var rawEntry: String? = null
        try {
            val iS = mContext.assets.open(dictFilename)
            iS.skip(fileOffset)
            val buffer = ByteArray(recordLength)
            iS.read(buffer)
            iS.close()
            rawEntry = String(buffer, "UTF-8")
            // Log.d(TAG, "got "+rawEntry);
        } catch (e: Exception) {
            Log.e(TAG, "loadRawEntry read exception", e)
            // e.printStackTrace();
        }

        return rawEntry
    } // end of loadRawEntry

    private fun loadCompressionDict(dictType: String): JSONArray? {
        Log.d(TAG, "loadCompressionDict " + dictType)
        if (dictType == "MD") {
            if (mMDJsonCompressionDict == null)
                mMDJsonCompressionDict = mMyGlobals.loadJSONArrayFromAssetFile(compressionDictFilenameTemplate.replace("dd", dictType))
            return mMDJsonCompressionDict
        } else if (dictType == "SD") {
            if (mSDJsonCompressionDict == null)
                mSDJsonCompressionDict = mMyGlobals.loadJSONArrayFromAssetFile(compressionDictFilenameTemplate.replace("dd", dictType))
            return mSDJsonCompressionDict
        }
        Log.e(TAG, "loadCompressionDict failed")
        return null
    } // end of loadCompressionDict

    private fun decompressEntry(dictType: String, compressedEntry: String?): String? {
        // Given a compressed entry string, decompresses the text
        // by a series of string replacements
        Log.d(TAG, "decompressEntry " + dictType)
        val compressionDict = loadCompressionDict(dictType)
        var expandedEntry = compressedEntry
        for (rix in 0 until compressionDict!!.length()) {
            var compressionEntry: JSONArray? = null
            try {
                compressionEntry = compressionDict!!.getJSONArray(rix)
                // Log.d(TAG,"decompressEntry got "+compressionEntry);
            } catch (e: JSONException) {
                Log.e(TAG, "jsonCompressionIndex read exception", e)
                // e.printStackTrace();
            }

            var shortString: String? = null
            var longString: String? = null
            try {
                shortString = compressionEntry!!.getString(0)
                // Log.d(TAG,"decompressEntry got '"+shortString+"'");
                longString = compressionEntry.getString(1)
                // Log.d(TAG,"decompressEntry got '"+longString+"'");
            } catch (e: JSONException) {
                Log.e(TAG, "jsonCompressionIndex entry read exception", e)
                // e.printStackTrace();
            }

            if (shortString != null && longString != null)
                expandedEntry = expandedEntry!!.replace(shortString, longString)
        }
        // Log.d(TAG, "Got "+expandedEntry);
        return expandedEntry
    } // end of decompressEntry

    fun loadEntry(dictType: String, indexNum: Int, fileOffset: Long, recordLength: Int): String? {
        return decompressEntry(dictType, loadRawEntry(dictType, indexNum, fileOffset, recordLength))
    } // end of loadEntry

    companion object {
        private val TAG = MyGlobals.TAG + " CombinedDict"
        private val headerFilenameTemplate = "MS-dd.json"
        private val mainIndexFilenameTemplate = "MS-dd-ix-html.json"
        private val reverseIndexFilenameTemplate = "MS-dd-rev-ix.json"
        private val dictionaryFilenameTemplate = "MS-dd.x.html"
        private val compressionDictFilenameTemplate = "MS-dd-cmpr.json"
    }

}
