// from http://misha.beshkin.lv/android-swipe-gesture-implementation
package info.MLCA.MSDict

import android.app.Activity
import android.util.Log
import android.view.GestureDetector
import android.view.GestureDetector.SimpleOnGestureListener
import android.view.MotionEvent

class SimpleGestureFilter(private val mActivity: Activity, private val mListener: SimpleGestureListener) : SimpleOnGestureListener() {
    var swipeMinDistance = 100 // originally 100
    var swipeMaxDistance = 1200 // originally 350
    var swipeMinVelocity = 120 // originally 100

    var mode = MODE_DYNAMIC
    private var mRunningFlag = true
    private var mTapFlag = false
    private val mDetector: GestureDetector

    init {
        Log.d(TAG, "SimpleGestureFilter create!")
        this.mDetector = GestureDetector(mActivity, this)
    }

    fun onTouchEvent(event: MotionEvent) {

        if (!this.mRunningFlag)
            return

        val result = this.mDetector.onTouchEvent(event)

        if (this.mode == MODE_SOLID)
            event.action = MotionEvent.ACTION_CANCEL
        else if (this.mode == MODE_DYNAMIC) {

            if (event.action == ACTION_FAKE)
                event.action = MotionEvent.ACTION_UP
            else if (result)
                event.action = MotionEvent.ACTION_CANCEL
            else if (this.mTapFlag) {
                event.action = MotionEvent.ACTION_DOWN
                this.mTapFlag = false
            }

        }
        // else just do nothing, it's Transparent
    }

    fun setEnabled(status: Boolean) {
        this.mRunningFlag = status
    }

    override fun onFling(e1: MotionEvent, e2: MotionEvent, velocityX: Float,
                         velocityY: Float): Boolean {
        var velocityX = velocityX
        var velocityY = velocityY

        val xDistance = Math.abs(e1.x - e2.x)
        val yDistance = Math.abs(e1.y - e2.y)

        if (xDistance > this.swipeMaxDistance || yDistance > this.swipeMaxDistance)
            return false

        velocityX = Math.abs(velocityX)
        velocityY = Math.abs(velocityY)
        var result = false

        if (velocityX > this.swipeMinVelocity && xDistance > this.swipeMinDistance) {
            if (e1.x > e2.x)
            // right to left
                this.mListener.onSwipe(SWIPE_LEFT)
            else
                this.mListener.onSwipe(SWIPE_RIGHT)

            result = true
        } else if (velocityY > this.swipeMinVelocity && yDistance > this.swipeMinDistance) {
            if (e1.y > e2.y)
            // bottom to up
                this.mListener.onSwipe(SWIPE_UP)
            else
                this.mListener.onSwipe(SWIPE_DOWN)

            result = true
        }

        return result
    }

    override fun onSingleTapUp(e: MotionEvent): Boolean {
        this.mTapFlag = true
        return false
    }

    override fun onDoubleTap(arg0: MotionEvent): Boolean {
        this.mListener.onDoubleTap()
        return true
    }

    override fun onDoubleTapEvent(arg0: MotionEvent): Boolean {
        return true
    }

    override fun onSingleTapConfirmed(arg0: MotionEvent): Boolean {

        if (this.mode == MODE_DYNAMIC) { // we owe an ACTION_UP, so we fake an
            arg0.action = ACTION_FAKE // action which will be converted to an
            // ACTION_UP later.
            this.mActivity.dispatchTouchEvent(arg0)
        }

        return false
    }

    internal interface SimpleGestureListener {
        fun onSwipe(direction: Int)

        fun onDoubleTap()
    }

    companion object {
        private val TAG = MyGlobals.TAG + " SimpleGestureFilter"

        val SWIPE_UP = 1
        val SWIPE_DOWN = 2
        val SWIPE_LEFT = 3
        val SWIPE_RIGHT = 4

        val MODE_TRANSPARENT = 0
        val MODE_SOLID = 1
        val MODE_DYNAMIC = 2

        private val ACTION_FAKE = -13 // just an unlikely number
    }

}
