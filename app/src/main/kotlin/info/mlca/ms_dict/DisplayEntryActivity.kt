package info.MLCA.MSDict

import junit.framework.Assert
import info.MLCA.MSDict.SimpleGestureFilter.SimpleGestureListener

import android.os.Bundle
import android.app.Activity
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.MotionEvent
import android.webkit.WebView
import android.support.v4.app.NavUtils
import android.annotation.TargetApi
import android.content.Intent
import android.content.SharedPreferences
import android.os.Build
import android.preference.PreferenceManager

class DisplayEntryActivity : Activity(), SimpleGestureListener {

    private var mMyGlobals: MyGlobals? = null
    private var mCombinedDict: CombinedDict? = null
    private var mSharedPrefs: SharedPreferences? = null

    private var gestureDetector: SimpleGestureFilter? = null
    private var mMyWebView: WebView? = null

    private var mIx = -1
    private var mRIx = -1
    private var mCurrentDict: String? = null
    private var mVernacularFlag: Boolean = false
    private var mReverseFlag: Boolean = false
    private var mLgViewFlag: Boolean = false
    private var mSearchWord: String? = null

    private// If the example is followed by a translation, move them closer together
            // simple view
            // If a sense number is followed by a POS, put them side-by-side
            //styles += ".SenseNumber, .POS {display:inline;}";
            //styles += "SenseNumber:before { content:\" \"; }";
            //styles += "SenseNumber:after { content:\"  \"; }";
            // simple view
            // If the example is followed by a translation, move them closer together
            // Other fields to hide
            // simple view
    val mainDictStylesheet: String
        get() {
            var styles = ""
            styles += "p.TopWord {font-size:300%; color:orange;}"
            styles += "h1 {font-size:300%; color:blue;}"
            styles += "p.Pronunciation {font-size:120%;}"
            styles += "span.Pronunciation {font-style:oblique;}"

            if (mLgViewFlag) {
                styles += "p.LexemePOS {font-size:90%;}"
                styles += "span.LexemePOS {font-weight:bold; color:grey;}"
                styles += "p.LexemeGloss {font-size:90%;}"
                styles += "span.LexemeGloss {font-weight:bold; color:grey;}"
                styles += ".LexemePOS + .LexemeGloss {margin-top:-5px;}"
            } else {
                styles += "p.Phonemic {display:none;}"
                styles += "p.LexemePOS {display:none;}"
                styles += "p.LexemeGloss {display:none;}"
            }
            styles += "section.Sense {border-top-style:solid;}"
            styles += "span.SenseNumber {font-size:200%; font-weight:bold; color:blue; margin-right:20px;}"
            styles += "p.POS {font-size:150%; border-top-style:dotted;}"
            styles += "span.POS {font-weight:bold; color:red;}"
            styles += "p.ScientificName {color:purple;}"
            styles += "span.ScientificName {font-style:oblique;}"

            styles += "p.Gloss {font-size:140%; color:blue}"
            styles += "span.GlossIntroduction {font-size:120%; font-weight:bold; font-style:oblique;}"
            styles += "span.MainGloss {font-size:140%; font-weight:bold;}"
            if (mLgViewFlag) {
                styles += "span.Case {font-size:80%; color:purple;}"
                styles += "span.Affixation {font-size:80%; color:orange;}"
                styles += "span.InflectedForm {font-size:80%; color:black}"
                styles += "span.Variant {font-size:80%; font-style:oblique; color:grey}"
            } else {
                styles += "span.Extra {display:none;}"
                styles += "span.Case {display:none;}"
                styles += "span.Affixation {display:none;}"
                styles += "span.InflectedForm {display:none;}"
                styles += "span.Variant {display:none;}"
            }

            styles += "p.MatigsalugDefinition {font-size:140%;}"
            styles += "span.MatigsalugDefinition {font-weight:bold;}"
            styles += "p.MatigsalugExampleSentence {font-size:120%;}"
            styles += "p.EnglishTranslationSentence {font-size:120%;}"
            styles += ".MatigsalugExampleSentence + .EnglishTranslationSentence {margin-top:-5px;}"

            styles += "span.EnglishIndex {font-weight:bold; color:brown;}"

            if (!mLgViewFlag) {
                styles += "p.ProtoForm {display:none;}"
                styles += "p.GrammarNote {display:none;}"
                styles += "p.Morphophonemic {display:none;}"
            }

            if (mLgViewFlag) {
                styles += "p.SemanticClass {font-size:90%; color:purple;}"
                styles += "span.SemanticClass {font-weight:bold;}"
                styles += "p.UsageLevel {font-size:80%; color:green;}"
                styles += "span.UsageLevel {font-weight:bold;}"
                styles += "p.CreationDate {font-size:50%; color:grey;}"
                styles += "span.CreationDate {font-weight:bold;}"
                styles += "p.EditDate {font-size:50%; color:grey;}"
                styles += "span.EditDate {font-weight:bold;}"
            } else {
                styles += "p.SemanticClass {display:none;}"
                styles += "p.UsageLevel {display:none;}"
                styles += "p.CreationDate {display:none;}"
                styles += "p.EditDate {display:none;}"
            }
            return styles
        }

    private// If a sense number is followed by a POS, put them side-by-side
            //styles += "SenseNumber:before { content:\" \"; }";
            //styles += "SenseNumber:after { content:\"  \"; }";
            // If the example is followed by a translation, move them closer together
            // simple view
    val studentDictStylesheet: String
        get() {
            var styles = ""
            styles += "p.TopWord {font-size:300%; color:orange;}"
            styles += "h1 {font-size:300%; color:blue;}"
            styles += "p.Pronunciation {font-size:120%;}"
            styles += "span.Pronunciation {font-style:oblique;}"
            styles += ".SenseNumber, .POS {display:inline;}"
            styles += "section.Sense {border-top-style:solid;}"
            styles += "span.SenseNumber {font-size:200%; font-weight:bold; color:blue; margin-right:20px;}"
            styles += "p.POS {font-size:150%;}"
            styles += "span.POS {font-weight:bold; color:red;}"
            styles += "span.MatigsalugDefinition {font-weight:bold;}"
            styles += "p.EnglishDefinition {font-size:140%;}"
            styles += "p.EnglishExampleSentence {font-size:120%;}"
            styles += "p.MatigsalugExampleSentence {font-size:120%;}"
            styles += ".EnglishExampleSentence + .MatigsalugExampleSentence {margin-top:-5px;}"
            if (mLgViewFlag) {
                styles += "p.SemanticDomain {font-size:90%; color:purple;}"
                styles += "span.SemanticDomain {font-weight:bold;}"
                styles += "p.Status {font-size:60%; color:green;}"
                styles += "span.Status {font-weight:bold;}"
                styles += "p.EditDate {font-size:50%; color:grey;}"
                styles += "span.EditDate {font-weight:bold;}"
            } else {
                styles += "p.SemanticDomain {display:none;}"
                styles += "p.Status {display:none;}"
                styles += "p.EditDate {display:none;}"
            }
            return styles
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d(TAG, "onCreate!")
        super.onCreate(savedInstanceState)
        gestureDetector = SimpleGestureFilter(this, this)
        setContentView(R.layout.activity_display_entry)
        mMyGlobals = MyGlobals(this)
        if (mCombinedDict == null)
            mCombinedDict = CombinedDict(this, mMyGlobals)
        mSharedPrefs = getSharedPreferences(MyGlobals.PREFS_NAME, 0)
        setupActionBar() // Show the Up button in the action bar
        mMyWebView = findViewById(R.id.DictView) as WebView
        mMyWebView!!.settings.builtInZoomControls = true
        //mMyWebView.getSettings().setSupportZoom(true); // Doesn't seem to be required
        loadAndFormatCurrentEntry()
    }

    /**
     * Set up the [android.app.ActionBar], if the API is available.
     */
    @TargetApi(Build.VERSION_CODES.HONEYCOMB)
    private fun setupActionBar() {
        //if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
        //	getActionBar().setDisplayHomeAsUpEnabled(true);
        //}
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.display_entry, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            android.R.id.home -> {
                // This ID represents the Home or Up button. In the case of this
                // activity, the Up button is shown. Use NavUtils to allow users
                // to navigate up one level in the application structure. For
                // more details, see the Navigation pattern on Android Design:
                //
                // http://developer.android.com/design/patterns/navigation.html#up-vs-back
                //
                NavUtils.navigateUpFromSameTask(this)
                return true
            }

            R.id.action_settings -> {
                val i = Intent(this, DisplaySettingsActivity::class.java)
                startActivityForResult(i, RESULT_SETTINGS)
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent) {
        super.onActivityResult(requestCode, resultCode, data)

        when (requestCode) {
            RESULT_SETTINGS -> loadAndFormatCurrentEntry() // using the new settings
        }
    }


    override fun dispatchTouchEvent(me: MotionEvent): Boolean {
        this.gestureDetector!!.onTouchEvent(me)
        return super.dispatchTouchEvent(me)
    }

    private fun getCurrentDictInfo() {
        Log.d(TAG, "getCurrentDictInfo()")
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(this)
        mLgViewFlag = defaultSharedPrefs.getBoolean("linguisticView", false)
        Log.d(TAG, "lgView:" + mLgViewFlag)
        mVernacularFlag = mSharedPrefs!!.getBoolean("vernacularFlag", false)
        mCurrentDict = mSharedPrefs!!.getString("currentDict", "")
        mSearchWord = mSharedPrefs!!.getString("searchWord", "")
        mReverseFlag = mSharedPrefs!!.getBoolean("reverseFlag", false)
        mIx = mSharedPrefs!!.getInt("indexNum", -1)
        if (mReverseFlag) mRIx = mSharedPrefs!!.getInt("reverseIndexNum", -1)
    }

    private fun loadCurrentEntry(): String? {
        // Looks in the app's preferences to find the current entry
        // then loads the actual dictionary record
        Log.d(TAG, "loadCurrentEntry " + mCurrentDict!!)
        val indexNum = mSharedPrefs!!.getInt("indexNum", -1)
        val fileOffset = mSharedPrefs!!.getLong("fileOffset", -1)
        val recordLength = mSharedPrefs!!.getInt("recordLength", -1)
        return mCombinedDict!!.loadEntry(mCurrentDict, indexNum, fileOffset, recordLength)
    }

    private fun loadAndFormatCurrentEntry() {
        // Takes the result of loadCurrentEntry()
        // and adds CSS style information
        // then loads the result into the WebView field.
        Log.d(TAG, "loadAndFormatCurrentEntry")
        getCurrentDictInfo() // Get updated info
        mMyGlobals!!.displayOurSavedValues()
        //String title = "<title>" + searchWord + "</title>";
        val title = ""
        var stylesheet = "<style>"
        if (mCurrentDict == "MD")
            stylesheet += mainDictStylesheet
        else if (mCurrentDict == "SD") stylesheet += studentDictStylesheet
        stylesheet += "</style>"
        val header = "<head>$stylesheet$title</head>"
        var top = ""
        if (mReverseFlag || mSearchWord!!.contains("→"))
            top = "<p class=\"TopWord\">$mSearchWord</p>"
        val body = "<body>" + top + loadCurrentEntry() + "</body>"
        val htmlString = "<html>$header$body</html>"
        mMyWebView!!.loadDataWithBaseURL(null, htmlString, "text/html", "UTF-8", null)
    }

    private fun displayPreviousRecord() {
        Log.d(TAG, "displayPreviousRecord")
        getCurrentDictInfo()
        Assert.assertTrue(mIx != -1)
        //if (mCurrentDict.equals("MD"))
        if (mReverseFlag) {
            Assert.assertTrue(mRIx != -1)
            if (mRIx > 0) {
                mRIx -= 1
                mCombinedDict!!.commitBrowseParameters(mReverseFlag, mRIx)
            } else
                mMyGlobals!!.displayErrorToast(resources.getString(
                        R.string.noPrevious_ms))
        } else { // not using reverse index
            Assert.assertTrue(mRIx == -1)
            if (mIx > 0) {
                mIx -= 1
                mCombinedDict!!.commitBrowseParameters(mReverseFlag, mIx)
            } else
                mMyGlobals!!.displayErrorToast(resources.getString(
                        R.string.noPrevious_ms))
        }
        loadAndFormatCurrentEntry()
    }

    private fun displayNextRecord() {
        Log.d(TAG, "displayNextRecord")
        getCurrentDictInfo()
        Assert.assertTrue(mIx != -1)
        if (mReverseFlag) {
            Assert.assertTrue(mRIx != -1)
            if (mRIx < mCombinedDict!!.length - 1) {
                mRIx += 1
                mCombinedDict!!.commitBrowseParameters(mReverseFlag, mRIx)
            } else
                mMyGlobals!!.displayErrorToast(resources.getString(
                        R.string.noNext_ms))
        } else { // not using reverse index
            Assert.assertTrue(mRIx == -1)
            if (mIx < mCombinedDict!!.length - 1) {
                mIx += 1
                mCombinedDict!!.commitBrowseParameters(mReverseFlag, mIx)
            } else
                mMyGlobals!!.displayErrorToast(resources.getString(
                        R.string.noNext_ms))
        }
        loadAndFormatCurrentEntry()
    }

    override fun onSwipe(direction: Int) {
        var myEvent = -1
        var str = ""
        when (direction) {

            SimpleGestureFilter.SWIPE_RIGHT -> {
                myEvent = 1
                str = "Swipe right"
            }
            SimpleGestureFilter.SWIPE_LEFT -> {
                myEvent = 2
                str = "Swipe left"
            }
            SimpleGestureFilter.SWIPE_DOWN -> {
                myEvent = 3
                str = "Swipe down"
            }
            SimpleGestureFilter.SWIPE_UP -> {
                myEvent = 4
                str = "Swipe up"
            }
        }
        Log.d(TAG, str)
        // Toast.makeText(this, str, Toast.LENGTH_SHORT).show();
        if (myEvent == 1)
            displayPreviousRecord()
        else if (myEvent == 2) displayNextRecord()
    }

    override fun onDoubleTap() {
        Log.d(TAG, "DoubleTap!")
        //Toast.makeText(this, "Double Tap", Toast.LENGTH_SHORT).show();
        val i = Intent(this, BrowseActivity::class.java)
        startActivity(i)
    }

    companion object {
        private val TAG = MyGlobals.TAG + " DisplayEntry"
        private val RESULT_SETTINGS = 1
    }

}
