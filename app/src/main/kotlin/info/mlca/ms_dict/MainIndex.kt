package info.MLCA.MSDict

import java.util.ArrayList

import org.json.JSONArray
import org.json.JSONException

import android.util.Log

class MainIndex// Constructor
(private val mDictType: String, private val mIndexFilename: String, // private Activity mActivity;
        // private Context mContext;
        // private WindowManager mWindowManager;
        // private SharedPreferences settings = null;
 private val mMyGlobals: MyGlobals) {

    private var mJsonIndex: JSONArray? = null

    val length: Int
        get() {
            loadIndexIfNecessary()
            return mJsonIndex!!.length()
        }

    init {
        Log.d(TAG, "constructor $mDictType $mIndexFilename")
        TAG = MyGlobals.TAG + " " + mDictType + " MainIndex"
    }// mActivity = activity;
    // mContext = mActivity.getApplicationContext();
    // mWindowManager = mActivity.getWindowManager();
    // Used for loading index from assets

    private fun loadIndexIfNecessary() {
        // Loads the dictionary index into a JSONArray IF NECESSARY
        if (mJsonIndex == null) {
            Log.d(TAG, "loadIndex " + mIndexFilename)
            mJsonIndex = mMyGlobals.loadJSONArrayFromAssetFile(mIndexFilename)
        }
        // Log.d(TAG, "Got JSON " + jsonIndex);
        // Log.d(TAG,"Loaded main index");
    }

    fun getIndexEntry(ix: Int): JSONArray? {
        // Log.d( TAG,"getIndexEntry "+ix);
        loadIndexIfNecessary()
        try {
            return mJsonIndex!!.getJSONArray(ix)
        } catch (e: JSONException) {
            Log.e(TAG, "jsonMainIndex read exception", e)
            mMyGlobals.displayOurSavedValues()
            return null
        }

    }

    private fun getIndexWord(ix: Int): String? {
        // Assumes that the index is already loaded
        // Log.d( TAG,"getIndexWord "+ix);
        val indexEntry = getIndexEntry(ix)
        try {
            return indexEntry!!.getString(0)
        } catch (e: JSONException) {
            Log.e(TAG, "getIndexWord exception", e)
            mMyGlobals.displayOurSavedValues()
            return null
        }

    }

    fun findInIndex(searchString: String): Int {
        // Given a word, search for it in the index
        // and return the index number of the best entry
        // or -1 if nothing found
        Log.d(TAG, "findInIndex $mIndexFilename '$searchString'")
        loadIndexIfNecessary()
        var nextBest = -1
        for (ix in 0 until mJsonIndex!!.length()) {
            val indexWord = getIndexWord(ix)
            val compare = indexWord!!.compareTo(searchString)
            if (compare == 0) {
                Log.d(TAG, "'$searchString' returned $ix")
                return ix
            } else {
                if (nextBest == -1 && indexWord.startsWith(searchString)) {
                    Log.d(TAG, "'$searchString' saved $ix")
                    nextBest = ix
                }
                if (compare > 0) break // Gone past
            }
        }
        Log.d(TAG, "Unable to find " + searchString)
        return nextBest
    }

    fun loadFirstLetters(list: ArrayList<String>) {
        Log.d(TAG, "loadFirstLetters")
        loadIndexIfNecessary()
        var lastLetter = ""
        var letterCount = 0
        for (ix in 0 until mJsonIndex!!.length()) {
            val indexEntry = getIndexEntry(ix)
            val word: String
            try {
                word = indexEntry!!.getString(0)
                val letter = word.substring(0, 1)
                letterCount += 1
                // Log.d(TAG,letter+lastLetter+" "+word+" "+letterCount);
                if (letter != lastLetter) {
                    if (lastLetter != "") {
                        list.add("$lastLetter ($letterCount)")
                        letterCount = 0
                    }
                    lastLetter = letter
                }
            } catch (e: JSONException) {
                Log.e(TAG, "jsonIndexEntry load exception", e)
                mMyGlobals.displayOurSavedValues()
            }

        }
        list.add(lastLetter + " (" + (letterCount + 1) + ")")
    }

    fun loadWordsForLetter(firstLetter: String, list: ArrayList<String>): Int {
        // Assumes that the index is already loaded
        Log.d(TAG, "loadWordsForLetter '$firstLetter'")
        //loadIndexIfNecessary();
        var indexOffset = -1
        for (ix in 0 until mJsonIndex!!.length()) {
            val indexEntry = getIndexEntry(ix)
            val word: String
            try {
                word = indexEntry!!.getString(0)
                val letter = word.substring(0, 1)
                if (letter == firstLetter) {
                    // Log.d(TAG, "Adding " + word);
                    // list.add(word + " " + ix);
                    list.add(word)
                    if (indexOffset == -1) {
                        Log.d(TAG, "Index offset is " + ix)
                        indexOffset = ix
                    }
                } else {
                    if (indexOffset != -1)
                        break
                }
            } catch (e: JSONException) {
                Log.e(TAG, "jsonIndexEntry load exception", e)
                mMyGlobals.displayOurSavedValues()
            }

        }
        return indexOffset
    }

    protected fun getFileReference(indexEntry: JSONArray?): FileReference? {
        // Given the index entry for a word,
        // get the HTML file offset and entry length
        // or return null
        // Assumes that the index is already loaded
        // 	(ReverseIndex doesn't have this function)
        Log.d(TAG, "getFileReference " + indexEntry!!)
        try {
            val offset = indexEntry.getLong(1)
            // Log.d(TAG, "Offset is "+offset);
            val length = indexEntry.getInt(2)
            // Log.d(TAG, "Length is "+length);
            return FileReference(offset, length)
        } catch (e: JSONException) {
            Log.e(TAG, "jsonIndexEntry getLong exception", e)
            mMyGlobals.displayOurSavedValues()
        }

        return null
    }

    fun getFileReference(ix: Int): FileReference? {
        // Given the index of a word in the index,
        // get the HTML file offset and entry length
        // or return null
        // 	(ReverseIndex doesn't have this function)
        Log.d(TAG, "getFileReference " + ix)
        //loadIndexIfNecessary();
        return getFileReference(getIndexEntry(ix))
    }

    companion object {
        private var TAG = MyGlobals.TAG + " MainIndex"
    }
}
