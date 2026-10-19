package info.MLCA.MSDict

import android.annotation.SuppressLint
import android.content.SharedPreferences
import android.os.Bundle
import android.preference.CheckBoxPreference
import android.preference.PreferenceFragment
import android.preference.PreferenceManager
import android.util.Log

@SuppressLint("NewApi")
class DisplayPrefsFragment : PreferenceFragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d("DisplayPrefsFragment", "onCreate!")
        super.onCreate(savedInstanceState)

        // Load the preferences from an XML resource
        addPreferencesFromResource(R.xml.display_preferences)

        // Handle interface language changes
        val defaultSharedPrefs = PreferenceManager.getDefaultSharedPreferences(activity)
        val mDisplayMSFlag = defaultSharedPrefs.getBoolean("nativeLanguageDisplay", true)
        val cbp: CheckBoxPreference

        cbp = findPreference("linguisticView") as CheckBoxPreference
        cbp.setSummary(if (mDisplayMSFlag) R.string.summary_linguistic_preference_ms else R.string.summary_linguistic_preference_en)
        cbp.setTitle(if (mDisplayMSFlag) R.string.title_linguistic_preference_ms else R.string.title_linguistic_preference_en)
    }
}