// Context dependent global functions for Android
package info.MLCA.MSDict

import java.io.IOException
import java.io.InputStream

import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.ActivityInfo
import android.graphics.Color
import android.preference.PreferenceManager
import android.util.DisplayMetrics
import android.util.Log
import android.view.Gravity
import android.view.Surface
import android.view.WindowManager
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

class MyGlobals(private val mActivity: Activity) {
    private val mContext: Context
    private val mWindowManager: WindowManager
    private var mSharedPrefs: SharedPreferences? = null
    private var mEditor: SharedPreferences.Editor? = null

    private val screenDimensions: DualInts
        get() {
            val dm = DisplayMetrics()
            mWindowManager.defaultDisplay.getMetrics(dm)
            return DualInts(dm.widthPixels, dm.heightPixels)
        }

    init {
        Log.d(TAG, "MyGlobals onCreate!")
        mContext = mActivity.applicationContext
        mWindowManager = mActivity.windowManager
    }

    private fun determineOrientation(rotation: Int, width: Int, height: Int): Int {
        // If the device's natural orientation is portrait
        return if ((rotation == Surface.ROTATION_0 || rotation == Surface.ROTATION_180) && height > width || (rotation == Surface.ROTATION_90 || rotation == Surface.ROTATION_270) && width > height) {
            when (rotation) {
                Surface.ROTATION_0 -> ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                Surface.ROTATION_90 -> ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
                Surface.ROTATION_180 -> ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT
                Surface.ROTATION_270 -> ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE
                else -> {
                    Log.e(TAG, "Unknown screen orientation. Defaulting to " + "portrait.")
                    ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                }
            }
        } else {
            when (rotation) {
                Surface.ROTATION_0 -> ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
                Surface.ROTATION_90 -> ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
                Surface.ROTATION_180 -> ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE
                Surface.ROTATION_270 -> ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT
                else -> {
                    Log.e(TAG, "Unknown screen orientation. Defaulting to " + "landscape.")
                    ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
                }
            }
        }// If the device's natural orientation is landscape
        //	or if the device is square:
    }

    /*private int getScreenOrientation() {
		// From
		// http://stackoverflow.com/questions/10380989/how-do-i-get-the-current-orientation-activityinfo-screen-orientation-of-an-a
		int rotation = mWindowManager.getDefaultDisplay().getRotation();
		DualInts screenDimensions = getScreenDimensions();
		int width = screenDimensions.getInt1();
		int height = screenDimensions.getInt2();
		return determineOrientation(rotation, width, height);
	}*/

    private fun saveScreenOrientation(): Int {
        //Log.d(TAG,"saveScreenOrientation");
        val rotation = mWindowManager.defaultDisplay.rotation
        val screenDimensions = screenDimensions
        val width = screenDimensions.int1
        val height = screenDimensions.int2
        val orientation = determineOrientation(rotation, width, height)
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(PREFS_NAME, 0)
        mEditor = mSharedPrefs!!.edit()
        mEditor!!.putInt("screenWidth", width)
        mEditor!!.putInt("screenHeight", height)
        mEditor!!.putInt("screenOrientation", orientation)
        mEditor!!.commit()
        return orientation
    }

    fun setCurrentDict(newDictType: String): String {
        Log.d(TAG, "setCurrentDict to " + newDictType)
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(PREFS_NAME, 0)
        if (mEditor == null)
            mEditor = mSharedPrefs!!.edit()
        mEditor!!.putString("currentDict", newDictType)
        mEditor!!.commit() // Save the setting
        return newDictType
    }

    fun loadAssetTextFile(filename: String): String? {
        // Given the name of a text file in the assets folder,
        // reads it all into a string and returns the string.
        var resultString: String? = null
        try {
            val `is` = mContext.assets.open(filename)
            val size = `is`.available()
            val buffer = ByteArray(size)
            `is`.read(buffer)
            `is`.close()
            resultString = String(buffer, "UTF-8")
        } catch (e: IOException) {
            Log.e(TAG, "loadAssetTextFile load exception", e)
            // e.printStackTrace();
            return null
        }

        return resultString
    }

    fun loadJSONObjectFromAssetFile(filename: String): JSONObject? {
        // Given the name of a JSON file in the assets folder,
        // reads it all into a string and then converts it
        // to a JSONObject and returns the pointer (or null).
        //Log.d(TAG,"loadJSONObjectFromAssetFile "+filename);
        var resultObject: JSONObject? = null
        try {
            resultObject = JSONObject(loadAssetTextFile(filename))
            // Log.d(TAG, "Got JSON " + resultArray);
        } catch (e: JSONException) {
            Log.e(TAG, "loadJSONObjectFromAssetFile JSON array exception", e)
            // e.printStackTrace();
        }

        return resultObject
    }

    fun loadJSONArrayFromAssetFile(filename: String): JSONArray? {
        // Given the name of a JSON file in the assets folder,
        // reads it all into a string and then converts it
        // to a JSONArray and returns the pointer (or null).
        //Log.d(TAG,"loadJSONArrayFromAssetFile "+filename);
        var resultArray: JSONArray? = null
        try {
            resultArray = JSONArray(loadAssetTextFile(filename))
            // Log.d(TAG, "Got JSON " + resultArray);
        } catch (e: JSONException) {
            Log.e(TAG, "loadJSONArrayFromAssetFile JSON array exception", e)
            // e.printStackTrace();
        }

        return resultArray
    }

    fun loadStartupInfo() {
        // Get our standard start-up info (e.g., screen size and orientation)
        //	and saves it in our preferences
        //Log.d(TAG,"loadStartupInfo");
        saveScreenOrientation() // sets up mEditor
    }

    fun displayErrorToast(text: String) {
        //Log.d(TAG,"displayErrorToast "+text);
        // Create a LinearLayout and Views
        val lLayout = LinearLayout(mActivity)
        lLayout.setBackgroundColor(Color.RED)
        //layout.setBackgroundResource(R.color.LightOrange);

        val tv = TextView(mActivity)
        tv.text = text
        tv.textSize = 25f
        tv.setTextColor(Color.WHITE)
        tv.gravity = Gravity.CENTER_VERTICAL

        val img = ImageView(mActivity)
        img.setImageResource(R.drawable.ic_launcher)

        // Add both the Views TextView and ImageView in layout
        lLayout.addView(tv) // left
        lLayout.addView(img) // right

        // Set the layout as Toast View
        val toast = Toast(mActivity)
        toast.view = lLayout

        // Set toast position
        toast.setGravity(Gravity.CENTER, 0, 0)
        // toast.setGravity(Gravity.TOP|Gravity.CENTER_HORIZONTAL, 0, 0);
        //toast.setGravity(Gravity.BOTTOM, 0, 50); // 50 dp from bottom

        toast.duration = Toast.LENGTH_SHORT
        toast.show()
    }

    /* public DualBooleans getDictEnabledFlags() {
		//Log.d(TAG, "getDictEnabledFlags");
		if (mSharedPrefs == null)
			mSharedPrefs = mActivity.getSharedPreferences(PREFS_NAME, 0);
		boolean mdEnabledFlag = mSharedPrefs.getBoolean("mdEnabled", true);
		boolean sdEnabledFlag = mSharedPrefs.getBoolean("sdEnabled", true);
		return new DualBooleans( mdEnabledFlag, sdEnabledFlag );
	} */

    private fun getUserPreferences() {
        Log.d(TAG, "getUserPreferences")
    }

    fun displayOurSavedValues() {
        // Used for debugging
        Log.d(TAG, "displayOurSavedValues")
        if (mSharedPrefs == null)
            mSharedPrefs = mActivity.getSharedPreferences(PREFS_NAME, 0)

        val sw = mSharedPrefs!!.getInt("screenWidth", 0)
        val sh = mSharedPrefs!!.getInt("screenHeight", 0)
        val so = mSharedPrefs!!.getInt("screenOrientation", 0)
        Log.d(TAG, "Screen " + sw + "x" + sh + " " + so)

        //DualBooleans enabledFlags = getDictEnabledFlags();
        //boolean mdEnabledFlag = enabledFlags.getBoolean1();
        //boolean sdEnabledFlag = enabledFlags.getBoolean2();
        //boolean mdEnabledFlag = mSharedPrefs.getBoolean("mdEnabled", true);
        //boolean sdEnabledFlag = mSharedPrefs.getBoolean("sdEnabled", true);
        //Log.d(TAG, "Dicts enabled: MD="+mdEnabledFlag+" SD="+sdEnabledFlag);
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(mActivity)
        val mdEnabledFlag = defaultSharedPrefs.getBoolean("mdEnabled", true)
        val sdEnabledFlag = defaultSharedPrefs.getBoolean("sdEnabled", true)
        val lgViewFlag = defaultSharedPrefs.getBoolean("linguisticView", false)
        Log.d(TAG, " User prefs MD:$mdEnabledFlag SD:$sdEnabledFlag LV:$lgViewFlag")

        if (mdEnabledFlag) {
            val dt = "MD"
            val dfv = mSharedPrefs!!.getInt(dt + "dataFormatVersion", -1)
            val cd = mSharedPrefs!!.getString(dt + "conversionDate", "")
            val numChunks = mSharedPrefs!!.getInt(dt + "numChunks", -1)
            Log.d(TAG, "$dt: $dfv $cd $numChunks")
            for (chunkNumber in 1..numChunks) {
                val wordLimit = mSharedPrefs!!.getInt(dt + "C" + chunkNumber, -1)
                Log.d(TAG, " $dt chunk $chunkNumber $wordLimit")
            }
        }
        if (sdEnabledFlag) {
            val dt = "SD"
            val dfv = mSharedPrefs!!.getInt(dt + "dataFormatVersion", -1)
            val cd = mSharedPrefs!!.getString(dt + "conversionDate", "")
            val numChunks = mSharedPrefs!!.getInt(dt + "numChunks", -1)
            Log.d(TAG, "$dt: $dfv $cd $numChunks")
            for (chunkNumber in 1..numChunks) {
                val wordLimit = mSharedPrefs!!.getInt(dt + "C" + chunkNumber, -1)
                Log.d(TAG, " $dt chunk $chunkNumber $wordLimit")
            }
        }

        val wrd = mSharedPrefs!!.getString("searchWord", "")
        val vf = mSharedPrefs!!.getBoolean("vernacularFlag", false)
        Log.d(TAG, "Word $wrd $vf")

        val currentDict = mSharedPrefs!!.getString("currentDict", "")
        val rf = mSharedPrefs!!.getBoolean("reverseFlag", false)
        Log.d(TAG, "CurrentDict $currentDict $rf")

        val indexNum = mSharedPrefs!!.getInt("indexNum", -1)
        val fileOffset = mSharedPrefs!!.getLong("fileOffset", -1)
        val recordLength = mSharedPrefs!!.getInt("recordLength", -1)
        Log.d(TAG, "ix $indexNum $fileOffset:$recordLength")

        val reverseIndexNum = mSharedPrefs!!.getInt("reverseIndexNum", -1)
        Log.d(TAG, "rix $reverseIndexNum $fileOffset:$recordLength")
    }

    companion object {
        val TAG = "MS-Dict"
        val PREFS_NAME = TAG + "-Prefs"
    }
}