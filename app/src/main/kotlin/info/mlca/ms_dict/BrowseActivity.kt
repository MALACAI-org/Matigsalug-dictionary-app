package info.MLCA.MSDict

import java.util.ArrayList
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.preference.PreferenceManager
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.ListView

class BrowseActivity : Activity() {

    private var mMyGlobals: MyGlobals? = null
    private var mSharedPrefs: SharedPreferences? = null

    private var mCombinedDict: CombinedDict? = null

    //private boolean mVernacularFlag, mReverseFlag;
    private var mMDEnabledFlag: Boolean = false
    private var mSDEnabledFlag: Boolean = false
    private var mLgViewFlag: Boolean = false

    private var ourList: ArrayList<String>? = null
    private var mStatus: String? = null // ""=getting first letter
    private var mIndexOffset: Int = 0

    /*private void commitParameters(boolean reverseFlag, String searchWord,
			int ix, int rix) {
		SharedPreferences.Editor editor = mSettings.edit();
		editor.putBoolean("reverseFlag", reverseFlag);
		editor.putString("searchWord", searchWord);
		editor.putInt("indexNum", ix);
		editor.putInt("reverseIndexNum", rix); // -1 if not applicable
		FileReference fileReference = mStudentDict.getFileReference(ix, false);
		editor.putLong("fileOffset", fileReference.getOffset());
		editor.putInt("recordLength", fileReference.getLength());
		editor.commit(); // Commit the changes
	}*/

    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d(TAG, "BrowseActivity onCreate!")
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_browse)
        mMyGlobals = MyGlobals(this)

        if (mSharedPrefs == null)
            mSharedPrefs = getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        val vernacularFlag = mSharedPrefs!!.getBoolean("vernacularFlag", false)

        Log.d(TAG, "Browse fill arrays! " + vernacularFlag)
        ourList = ArrayList()
        if (mCombinedDict == null)
            mCombinedDict = CombinedDict(this, mMyGlobals)
        val reverseFlag = mCombinedDict!!.loadFirstLetters(vernacularFlag, ourList)
        Log.d(TAG, "Added entries " + ourList!!.size)
        mStatus = ""

        val adapter = ArrayAdapter(this,
                android.R.layout.simple_list_item_1, ourList!!)
        val listview = findViewById(R.id.listview) as ListView
        listview.adapter = adapter
        listview.onItemClickListener = AdapterView.OnItemClickListener { parent, view, position, id ->
            val item = parent.getItemAtPosition(position) as String
            if (mStatus == "") { // we have the first letter of a word
                Log.d(TAG, "Chose letter " + item + " at position "
                        + position)
                mStatus = item.substring(0, 1)
                Log.d(TAG, "First letter is " + mStatus!!)
                Log.d(TAG, "Browse refill arrays!")
                //Log.d(TAG, "Had entries " + ourList.size());
                ourList!!.clear()
                mIndexOffset = mCombinedDict!!.loadWordsForLetter(mStatus, ourList)
                //Log.d(TAG, "Readded entries " + ourList.size());
                adapter.notifyDataSetChanged()
            } else { // we selected a word
                Log.d(TAG, "Chose word $item at position $position")
                mCombinedDict!!.commitBrowseParameters(reverseFlag, mIndexOffset + position)
                val i = Intent(this@BrowseActivity,
                        DisplayEntryActivity::class.java)
                startActivity(i)
            }
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.browse, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {

            R.id.action_settings -> {
                val i = Intent(this, MainSettingsActivity::class.java)
                startActivityForResult(i, RESULT_SETTINGS)
            }
        }
        return true
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent) {
        super.onActivityResult(requestCode, resultCode, data)

        when (requestCode) {
            RESULT_SETTINGS -> {
                getUserPreferences()
                if (mSharedPrefs == null)
                    mSharedPrefs = getSharedPreferences(MyGlobals.PREFS_NAME, 0)
                val currentDict = mSharedPrefs!!.getString("currentDict", "")
                // See if we now have an invalid situation
                if (currentDict == "MD" && !mMDEnabledFlag || currentDict == "SD" && !mSDEnabledFlag) {
                    Log.d(TAG, "Dictionary loaded now invalid " + currentDict)
                    val i = Intent(this, MainActivity::class.java)
                    startActivity(i)
                }
            }
        }
    }

    private fun getUserPreferences() {
        Log.d(TAG, "getUserPreferences")
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(this)
        mMDEnabledFlag = defaultSharedPrefs.getBoolean("mdEnabled", true)
        mSDEnabledFlag = defaultSharedPrefs.getBoolean("sdEnabled", true)
        mLgViewFlag = defaultSharedPrefs.getBoolean("linguisticView", false)
        Log.d(TAG, " User prefs MD:$mMDEnabledFlag SD:$mSDEnabledFlag LV:$mLgViewFlag")
    }

    companion object {
        val TAG = MyGlobals.TAG + " Browse"
        private val RESULT_SETTINGS = 1
    }
}
