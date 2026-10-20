package info.MLCA.MSDict

import java.util.ArrayList

import org.json.JSONArray
import org.json.JSONException

import android.util.Log

class ReverseIndex(private val mDictType: String, private val mIndexFilename: String, //private Activity mActivity;
        //private Context mContext;
        //private WindowManager mWindowManager;
        //private SharedPreferences settings = null;
                   private val mMyGlobals: MyGlobals // Used for loading index from assets
) {

    private var mJsonIndex: JSONArray? = null

    val length: Int
        get() {
            loadIndexIfNecessary()
            return mJsonIndex!!.length()
        }

    init {
        Log.d(TAG, "constructor $mDictType $mIndexFilename")
        TAG = MyGlobals.TAG + " " + mDictType + " ReverseIndex"
    }//mActivity = activity;
    //mContext = mActivity.getApplicationContext();
    //mWindowManager = mActivity.getWindowManager();

    private fun loadIndexIfNecessary() {
        // Loads the dictionary index into a JSONArray IF NECESSARY
        if (mJsonIndex == null) {
            Log.d(TAG, "loadIndex")
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
            // Log.d(TAG,"RI got "+indexEntry);
        } catch (e: JSONException) {
            Log.e(TAG, "jsonReverseIndex read exception", e)
            mMyGlobals.displayOurSavedValues()
            return null
        }

    }

    /*private String getIndexWord(int ix) {
		// Log.d( TAG,"getIndexWord "+ix);
		JSONArray indexEntry = getIndexEntry(ix);
		try {
			return indexEntry.getString(0);
		} catch (JSONException e) {
			Log.e(TAG, "getIndexWord exception", e);
			e.printStackTrace();
			return null;
		}
	}*/

    fun findInIndex(searchString: String): DualInts? {
        Log.d(TAG, "findInIndex $mIndexFilename '$searchString'")
        loadIndexIfNecessary()
        var nextBest: DualInts? = null
        for (rix in 0 until mJsonIndex!!.length()) {
            val indexEntry = getIndexEntry(rix)
            try {
                val indexWord = indexEntry!!.getString(0)
                val compare = indexWord.compareTo(searchString)
                if (compare == 0) {
                    val ix = indexEntry.getInt(1)
                    Log.d(TAG, "'" + searchString + "' found " + ix + " at "
                            + rix)
                    return DualInts(ix, rix)
                } else {
                    if (nextBest == null && indexWord.startsWith(searchString)) {
                        val ix = indexEntry.getInt(1)
                        Log.d(TAG, "'$searchString' saved $ix at $rix")
                        nextBest = DualInts(ix, rix)
                    }
                    if (compare > 0) break // Gone past
                }
            } catch (e: JSONException) {
                Log.e(TAG, "jsonIndexEntry compare exception", e)
                mMyGlobals.displayOurSavedValues()
            }

        }
        Log.d(TAG, "Unable to find reverse '$searchString'")
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
                    //list.add(word + " " + ix);
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

    companion object {
        private var TAG = MyGlobals.TAG + " ReverseIndex"
    }

}
