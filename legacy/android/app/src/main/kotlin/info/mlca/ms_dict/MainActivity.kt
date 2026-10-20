package info.MLCA.MSDict

import android.os.Bundle
import android.preference.PreferenceManager
import android.app.Activity
import android.content.Intent
import android.content.SharedPreferences
import android.util.Log
import android.view.KeyEvent
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.view.WindowManager
import android.view.inputmethod.EditorInfo
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.TextView.OnEditorActionListener

class MainActivity : Activity() {

    private var mMyGlobals: MyGlobals? = null
    private var mCombinedDict: CombinedDict? = null
    private var mSharedPrefs: SharedPreferences? = null
    private var mEditor: SharedPreferences.Editor? = null
    private var mEditText: EditText? = null
    private var mMDEnabledFlag: Boolean = false
    private var mSDEnabledFlag: Boolean = false
    private var mLgViewFlag: Boolean = false
    private val mEnableMDButton: Button? = null
    private val mEnableSDButton: Button? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        // Called when activity starts
        // or restarts when orientation or screen-size changes
        Log.d(TAG, "onCreate!")
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        mMyGlobals = MyGlobals(this)
        mMyGlobals!!.loadStartupInfo()
        if (mCombinedDict == null)
            mCombinedDict = CombinedDict(this, mMyGlobals)
        // Only load our data the first time
        // (DOESN'T WORK COZ ACTIVITY IS RECREATED)
        if (mSharedPrefs == null)
            mSharedPrefs = getSharedPreferences(MyGlobals.PREFS_NAME, 0)

        mEditText = findViewById(R.id.editText) as EditText
        setupDictEnabledButtons()
        mEditText!!.setOnEditorActionListener { v, actionId, event ->
            val result = actionId and EditorInfo.IME_MASK_ACTION
            when (result) {
                EditorInfo.IME_ACTION_DONE -> {
                    Log.d(TAG, "Keyboard DONE!")
                    doSearchBoth(v)
                }
                EditorInfo.IME_ACTION_NEXT -> Log.e(TAG, "Keyboard NEXT!")
                EditorInfo.IME_ACTION_SEARCH -> {
                    Log.d(TAG, "Keyboard SEARCH!")
                    doSearchBoth(v)
                }
            }
            false
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onResume() {
        super.onResume()
        // Try to make the keyboard pop-up when they come back from dict view
        window.setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE)
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
            RESULT_SETTINGS -> setupDictEnabledButtons()
        }
    }

    /*   private void showUserSettings() {
		Log.d(TAG, "showUserSettings" );
    	getUserPreferences();
        Log.d("MD","is "+mMDEnabledFlag);
        Log.d("SD","is "+mSDEnabledFlag);
        Log.d("LV","is "+mLgViewFlag);
        //StringBuilder builder = new StringBuilder();
        //builder.append("\n Username: " + sharedPrefs.getString("prefUsername", "NULL"));
        //builder.append("\n Send report:" + sharedPrefs.getBoolean("prefSendReport", false));
        //builder.append("\n Sync Frequency: " + sharedPrefs.getString("prefSyncFrequency", "NULL"));
        //TextView settingsTextView = (TextView) findViewById(R.id.textUserSettings);
        //settingsTextView.setText(builder.toString());
    } */

    private fun getUserPreferences() {
        Log.d(TAG, "getUserPreferences")
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(this)
        mMDEnabledFlag = defaultSharedPrefs.getBoolean("mdEnabled", true)
        mSDEnabledFlag = defaultSharedPrefs.getBoolean("sdEnabled", true)
        mLgViewFlag = defaultSharedPrefs.getBoolean("linguisticView", false)
        Log.d(TAG, " User prefs MD:$mMDEnabledFlag SD:$mSDEnabledFlag LV:$mLgViewFlag")
    }

    private fun setDictControlButtons(enableFlag: Boolean) {
        Log.d(TAG, "setDictControlButtons " + enableFlag)
        // Enable or disable buttons and fields as required
        findViewById(R.id.buttonBrowseEnglish).isEnabled = enableFlag
        findViewById(R.id.buttonBrowseVernacular).isEnabled = enableFlag
        findViewById(R.id.buttonSearchEnglish).isEnabled = enableFlag
        findViewById(R.id.buttonSearchVernacular).isEnabled = enableFlag
        mEditText!!.isEnabled = enableFlag
    }

    private fun setupDictEnabledButtons() {
        Log.d(TAG, "setupDictEnabledButtons")
        getUserPreferences()
        setDictControlButtons(mMDEnabledFlag || mSDEnabledFlag)
    }

    private fun doSearch(vernacularFlag: Boolean): Boolean {
        Log.d(TAG, "doSearch " + vernacularFlag)
        val searchString = mEditText!!.text.toString().trim { it <= ' ' }.toLowerCase()
        if (mEditor == null) mEditor = mSharedPrefs!!.edit()
        mEditor!!.putBoolean("vernacularFlag", vernacularFlag)

        var indexNum = -1
        var reverseIndexNum = -1
        val results = mCombinedDict!!.findInIndex(vernacularFlag, searchString)
        if (results == null) {
            Log.e(TAG, "Word not found '$searchString'")
            mMyGlobals!!.displayErrorToast(resources.getString(
                    R.string.notFound_ms))
            return false
        }
        Log.d(TAG, "Got vernacular doSearch result")
        indexNum = results.int1
        reverseIndexNum = results.int2
        if (indexNum == -1) {
            Log.e(TAG, "Word not found2 '$searchString'")
            mMyGlobals!!.displayErrorToast(resources.getString(
                    R.string.notFound_ms))
            return false
        }
        mCombinedDict!!.commitSearchParameters(searchString, indexNum, reverseIndexNum)
        Log.d(TAG, "Going to display '$searchString'")
        return true
    }

    private fun doSearchBoth(): Boolean {
        Log.d(TAG, "doSearchBoth")
        val searchString = mEditText!!.text.toString().trim { it <= ' ' }
                .toLowerCase()

        var indexNum = -1
        var reverseIndexNum = -1
        val results: DualInts?
        if (mEditor == null) mEditor = mSharedPrefs!!.edit()

        // Search the main index(es) first
        //boolean vernacularFlag = true;
        results = mCombinedDict!!.findInIndex(searchString)
        if (results != null) {
            Log.d(TAG, "Got main doSearch result")
            indexNum = results.int1
            reverseIndexNum = results.int2
        }
        if (indexNum == -1 && reverseIndexNum == -1) {
            Log.e(TAG, "Word not found '$searchString'")
            mMyGlobals!!.displayErrorToast(resources.getString(
                    R.string.notFound_ms))
            return false
        }
        mCombinedDict!!.commitSearchParameters(searchString, indexNum, reverseIndexNum)
        Log.d(TAG, "Going to display '$searchString'")
        return true
    }

    fun doClearText(view: View) {
        Log.d(TAG, "doClearText!")
        mEditText!!.setText("")
        // Try to make sure that the keyboard pops up
        window.setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE)
    }

    fun doBrowseEnglish(view: View) {
        Log.d(TAG, "doBrowseEnglish!")
        if (mEditor == null) mEditor = mSharedPrefs!!.edit()
        mEditor!!.putBoolean("vernacularFlag", false)
        mEditor!!.commit() // Commit the setting
        val i = Intent(this, BrowseActivity::class.java)
        startActivity(i)
    }

    fun doBrowseVernacular(view: View) {
        Log.d(TAG, "doBrowseVernacular!")
        if (mEditor == null) mEditor = mSharedPrefs!!.edit()
        mEditor!!.putBoolean("vernacularFlag", true)
        mEditor!!.commit() // Commit the setting
        val i = Intent(this, BrowseActivity::class.java)
        startActivity(i)
    }

    fun doSearchEnglish(view: View) {
        Log.d(TAG, "doSearchEnglish!")
        if (doSearch(false)) { // also commits preferences
            val i = Intent(this, DisplayEntryActivity::class.java)
            startActivity(i)
        }
    }

    fun doSearchVernacular(view: View) {
        Log.d(TAG, "doSearchVernacular!")
        if (doSearch(true)) { // also commits preferences
            val i = Intent(this, DisplayEntryActivity::class.java)
            startActivity(i)
        }
    }

    fun doSearchBoth(view: View) {
        Log.d(TAG, "doSearchBoth!")
        if (doSearchBoth()) { // also commits preferences
            val i = Intent(this, DisplayEntryActivity::class.java)
            startActivity(i)
        }
    }

    companion object {
        private val TAG = MyGlobals.TAG + " Main"
        private val RESULT_SETTINGS = 1
    }
}
