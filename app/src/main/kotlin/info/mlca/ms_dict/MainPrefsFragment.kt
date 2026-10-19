package info.MLCA.MSDict

import android.annotation.SuppressLint
import android.os.Bundle
import android.preference.PreferenceFragment
import android.util.Log

@SuppressLint("NewApi")
class MainPrefsFragment : PreferenceFragment() {

    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d("MainPrefsFragment", "onCreate!")
        super.onCreate(savedInstanceState)

        // Load the preferences from an XML resource
        addPreferencesFromResource(R.xml.main_preferences)
    }
}