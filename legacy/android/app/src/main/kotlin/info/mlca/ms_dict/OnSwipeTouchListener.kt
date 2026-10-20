// Now unused!!!
// from http://stackoverflow.com/questions/4139288/android-how-to-handle-right-to-left-swipe-gestures
package info.MLCA.MSDict

import android.content.Context
import android.util.Log
import android.view.GestureDetector
import android.view.GestureDetector.SimpleOnGestureListener
import android.view.MotionEvent
import android.view.View
import android.view.View.OnTouchListener

class OnSwipeTouchListener
//private final GestureDetector mGestureDetector;

(ctx: Context) : OnTouchListener {
    init {
        Log.d(TAG, "onSwipeTouchListener create!")
        val gestureDetector = GestureDetector(ctx, GestureListener())
        //mGestureDetector = new GestureDetector(ctx, new GestureListener());
    }

    private inner class GestureListener : SimpleOnGestureListener() {

        override fun onDown(e: MotionEvent): Boolean {
            return true
        }

        override fun onFling(e1: MotionEvent, e2: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
            val result = false
            try {
                val diffY = e2.y - e1.y
                val diffX = e2.x - e1.x
                if (Math.abs(diffX) > Math.abs(diffY)) {
                    if (Math.abs(diffX) > SWIPE_THRESHOLD && Math.abs(velocityX) > SWIPE_VELOCITY_THRESHOLD) {
                        if (diffX > 0) {
                            onSwipeRight()
                        } else {
                            onSwipeLeft()
                        }
                    }
                } else {
                    if (Math.abs(diffY) > SWIPE_THRESHOLD && Math.abs(velocityY) > SWIPE_VELOCITY_THRESHOLD) {
                        if (diffY > 0) {
                            onSwipeBottom()
                        } else {
                            onSwipeTop()
                        }
                    }
                }
            } catch (exception: Exception) {
                exception.printStackTrace()
            }

            return result
        }

        companion object {

            private val SWIPE_THRESHOLD = 100
            private val SWIPE_VELOCITY_THRESHOLD = 100
        }
    }

    fun onSwipeRight() {}

    fun onSwipeLeft() {}

    fun onSwipeTop() {}

    fun onSwipeBottom() {}

    override fun onTouch(v: View, event: MotionEvent): Boolean {
        // TODO Auto-generated method stub
        return false
    }

    companion object {
        private val TAG = MyGlobals.TAG + " OnSwipeTouchListener"
    }
}