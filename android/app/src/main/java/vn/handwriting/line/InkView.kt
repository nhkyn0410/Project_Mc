package vn.handwriting.line

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.view.MotionEvent
import android.view.View

/** Khung viết có hàng kẻ. Nhận ngón tay hoặc bút, khi đã có bút thì bỏ qua ngón tay. */
class InkView(context: Context) : View(context) {
    var onStrokeEnd: (() -> Unit)? = null
    val topPad = 8.0 * resources.displayMetrics.density
    val rowPx = ROW_MM * resources.displayMetrics.ydpi / 25.4

    private class Live(val xs: ArrayList<Double> = ArrayList(), val ys: ArrayList<Double> = ArrayList()) {
        val path = Path()
    }

    private val done = ArrayList<Live>()
    private var current: Live? = null
    private var stylusSeen = false
    private val rule = Paint().apply { color = Color.rgb(205, 214, 226); strokeWidth = 2f }
    private val ink = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(20, 30, 60)
        style = Paint.Style.STROKE
        strokeWidth = 3.2f * resources.displayMetrics.density
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }

    val strokes: List<Stroke>
        get() = done.map { Stroke(it.xs.toDoubleArray(), it.ys.toDoubleArray()) }

    fun undo() {
        if (done.isNotEmpty()) { done.removeAt(done.lastIndex); invalidate() }
    }

    fun clear() {
        done.clear(); current = null; invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        canvas.drawColor(Color.WHITE)
        var y = topPad
        while (y <= height) {
            canvas.drawLine(0f, y.toFloat(), width.toFloat(), y.toFloat(), rule)
            y += rowPx
        }
        for (s in done) canvas.drawPath(s.path, ink)
        current?.let { canvas.drawPath(it.path, ink) }
    }

    private fun add(s: Live, x: Float, y: Float) {
        if (s.xs.isEmpty()) s.path.moveTo(x, y) else s.path.lineTo(x, y)
        s.xs.add(x.toDouble())
        s.ys.add(y.toDouble())
    }

    override fun onTouchEvent(e: MotionEvent): Boolean {
        val tool = e.getToolType(0)
        if (tool == MotionEvent.TOOL_TYPE_STYLUS) stylusSeen = true
        if (stylusSeen && tool == MotionEvent.TOOL_TYPE_FINGER) return true
        when (e.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                parent?.requestDisallowInterceptTouchEvent(true)
                current = Live().also { add(it, e.x, e.y) }
                invalidate()
            }
            MotionEvent.ACTION_MOVE -> current?.let { s ->
                for (h in 0 until e.historySize) add(s, e.getHistoricalX(h), e.getHistoricalY(h))
                add(s, e.x, e.y)
                invalidate()
            }
            MotionEvent.ACTION_UP -> current?.let { s ->
                add(s, e.x, e.y)
                done.add(s)
                current = null
                invalidate()
                onStrokeEnd?.invoke()
            }
            MotionEvent.ACTION_CANCEL -> {
                current = null
                invalidate()
            }
        }
        return true
    }

    private companion object {
        const val ROW_MM = 12.0
    }
}
