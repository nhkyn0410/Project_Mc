package vn.handwriting.line

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.TypedValue
import android.view.Gravity
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private val worker = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private var recognizer: Recognizer? = null
    private var generation = 0
    private lateinit var ink: InkView
    private lateinit var committed: TextView
    private lateinit var status: TextView
    private val choices = ArrayList<Button>()
    private val runRecognition = Runnable { recognize() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pad = dp(10)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(245, 247, 250))
            setPadding(pad, pad * 3, pad, pad)
            fitsSystemWindows = true
        }
        committed = TextView(this).apply {
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 20f)
            setTextColor(Color.rgb(20, 30, 60))
            hint = "Văn bản đã chốt hiện ở đây"
            setTextIsSelectable(true)
        }
        root.addView(ScrollView(this).apply { addView(committed) }, LinearLayout.LayoutParams(MATCH_PARENT, dp(90)))
        val row = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        repeat(3) { i ->
            val b = Button(this).apply {
                isAllCaps = false
                gravity = Gravity.START or Gravity.CENTER_VERTICAL
                text = if (i == 0) "Viết vào khung bên dưới" else ""
                isEnabled = false
                setOnClickListener { commit(text.toString()) }
            }
            choices.add(b)
            row.addView(b, LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT))
        }
        root.addView(row)
        ink = InkView(this).apply { onStrokeEnd = { schedule() } }
        root.addView(ink, LinearLayout.LayoutParams(MATCH_PARENT, 0, 1f))
        status = TextView(this).apply {
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 12f)
            text = "Đang nạp mô hình"
        }
        root.addView(status)
        val actions = LinearLayout(this)
        fun action(label: String, block: () -> Unit) = actions.addView(
            Button(this).apply { text = label; isAllCaps = false; setOnClickListener { block() } },
            LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f),
        )
        action("Hoàn tác") { ink.undo(); schedule() }
        action("Xóa") { reset() }
        action("Xong") { choices[0].takeIf { it.isEnabled }?.let { commit(it.text.toString()) } }
        root.addView(actions)
        setContentView(root)
        worker.execute {
            val r = Recognizer(this)
            main.post { recognizer = r; status.text = "Sẵn sàng, nhận dạng không cần mạng" }
        }
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    private fun schedule() {
        main.removeCallbacks(runRecognition)
        main.postDelayed(runRecognition, DEBOUNCE_MS)
    }

    private fun recognize() {
        val r = recognizer ?: return
        val strokes = ink.strokes
        val id = ++generation
        if (strokes.isEmpty()) { showEmpty(); return }
        val top = ink.topPad
        val row = ink.rowPx
        worker.execute {
            if (id != generation) return@execute
            val started = System.nanoTime()
            val result = r.recognize(strokes, top, row)
            val total = (System.nanoTime() - started) / 1_000_000
            main.post {
                if (id != generation) return@post
                choices.forEachIndexed { i, b ->
                    val text = result.candidates.getOrNull(i).orEmpty()
                    b.text = text
                    b.isEnabled = text.isNotEmpty()
                }
                status.text = "Tổng $total ms: vẽ ${result.renderMs}, mô hình ${result.modelMs}, giải mã ${result.decodeMs}"
            }
        }
    }

    private fun commit(text: String) {
        if (text.isEmpty()) return
        committed.append(if (committed.text.isEmpty()) text else " $text")
        reset()
    }

    private fun reset() {
        generation++
        main.removeCallbacks(runRecognition)
        ink.clear()
        showEmpty()
    }

    private fun showEmpty() {
        choices.forEachIndexed { i, b -> b.text = if (i == 0) "Viết vào khung bên dưới" else ""; b.isEnabled = false }
    }

    override fun onDestroy() {
        worker.shutdown()
        super.onDestroy()
    }

    private companion object {
        const val DEBOUNCE_MS = 350L
    }
}
