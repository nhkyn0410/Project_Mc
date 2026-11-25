package vn.handwriting.line

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.google.android.gms.tasks.Tasks
import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.common.model.RemoteModelManager
import com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognition
import com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognitionModel
import com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognitionModelIdentifier
import com.google.mlkit.vision.digitalink.recognition.DigitalInkRecognizerOptions
import com.google.mlkit.vision.digitalink.recognition.RecognitionContext
import com.google.mlkit.vision.digitalink.recognition.WritingArea
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.concurrent.TimeUnit
import com.google.mlkit.vision.digitalink.recognition.Ink as MlInk

/**
 * Bài đo trên điện thoại thật (docs/07-nhat-ky-thi-nghiem.md, mục 15). Nét đọc từ assets/bench/ của gói kiểm thử,
 * do training/export_bench.py ghi ra. Kết quả ghi vào thư mục tệp ngoài của ứng dụng, lấy về bằng adb pull.
 */
@RunWith(AndroidJUnit4::class)
class BenchTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val outDir: File get() = instrumentation.targetContext.getExternalFilesDir(null)!!

    private fun forEachLine(set: String, block: (JSONObject) -> Unit) {
        instrumentation.context.assets.open("bench/$set.jsonl").bufferedReader(Charsets.UTF_8).useLines { seq ->
            seq.filter { it.isNotBlank() }.forEach { block(JSONObject(it)) }
        }
    }

    private fun head(obj: JSONObject) = JSONObject()
        .put("who", obj.getString("who")).put("index", obj.getInt("index"))
        .put("kind", obj.getString("kind")).put("label", obj.getString("label"))

    private fun appStrokes(strokes: JSONArray): List<Stroke> = (0 until strokes.length()).map { i ->
        val pts = strokes.getJSONArray(i)
        Stroke(
            DoubleArray(pts.length()) { pts.getJSONArray(it).getDouble(0) },
            DoubleArray(pts.length()) { pts.getJSONArray(it).getDouble(1) },
        )
    }

    /** Độ trễ của ứng dụng trên nhóm chỉnh, có và không có n-gram ký tự, chạy xen kẽ từng dòng. */
    @Test
    fun appLatency() {
        val ctx = instrumentation.targetContext
        val withChar = Recognizer(ctx, useCharLm = true)
        val without = Recognizer(ctx, useCharLm = false)
        check(withChar.usesCharLm && !without.usesCharLm) { "thiếu clm.bin hoặc trọng số trong params.txt" }
        var warm = 0
        forEachLine("chinh") { obj ->
            if (warm < 3) {
                val s = appStrokes(obj.getJSONArray("raw"))
                withChar.recognize(s, obj.getDouble("topPad"), obj.getDouble("rowPx"))
                without.recognize(s, obj.getDouble("topPad"), obj.getDouble("rowPx"))
                warm++
            }
        }
        File(outDir, "app-chinh.jsonl").bufferedWriter().use { out ->
            var n = 0
            forEachLine("chinh") { obj ->
                val strokes = appStrokes(obj.getJSONArray("raw"))
                val res = head(obj).put("points", strokes.sumOf { it.xs.size })
                val order = if (n % 2 == 0) listOf("new" to withChar, "old" to without) else listOf("old" to without, "new" to withChar)
                for ((name, r) in order) {
                    val t0 = System.nanoTime()
                    val result = r.recognize(strokes, obj.getDouble("topPad"), obj.getDouble("rowPx"))
                    val ms = (System.nanoTime() - t0) / 1e6
                    res.put(name, result.candidates.firstOrNull() ?: "")
                        .put("${name}Ms", ms).put("${name}Render", result.renderMs)
                        .put("${name}Model", result.modelMs).put("${name}Decode", result.decodeMs)
                }
                out.write(res.toString()); out.newLine()
                n++
            }
        }
    }

    private fun mlInk(strokes: JSONArray): MlInk {
        val ink = MlInk.builder()
        for (i in 0 until strokes.length()) {
            val pts = strokes.getJSONArray(i)
            val stroke = MlInk.Stroke.builder()
            for (j in 0 until pts.length()) {
                val p = pts.getJSONArray(j)
                stroke.addPoint(MlInk.Point.create(p.getDouble(0).toFloat(), p.getDouble(1).toFloat(), p.getDouble(2).toLong()))
            }
            ink.addStroke(stroke.build())
        }
        return ink.build()
    }

    /** ML Kit tiếng Việt trên nhóm chỉnh và tập đánh giá: nét gốc và dòng ảo sau lớp ghép đoạn. */
    @Test
    fun mlKit() {
        val model = DigitalInkRecognitionModel.builder(DigitalInkRecognitionModelIdentifier.VI).build()
        Tasks.await(RemoteModelManager.getInstance().download(model, DownloadConditions.Builder().build()), 15, TimeUnit.MINUTES)
        val recognizer = DigitalInkRecognition.getClient(DigitalInkRecognizerOptions.builder(model).build())
        // Lần chạy đầu nạp mô hình, không tính vào thời gian.
        forEachLine("chinh") { obj ->
            if (obj.getInt("index") == 0) {
                val ctx = RecognitionContext.builder().setPreContext("").build()
                Tasks.await(recognizer.recognize(mlInk(obj.getJSONArray("stitched")), ctx), 60, TimeUnit.SECONDS)
            }
        }
        for (set in listOf("chinh", "danh-gia")) {
            File(outDir, "mlkit-$set.jsonl").bufferedWriter().use { out ->
                forEachLine(set) { obj ->
                    val res = head(obj)
                    for ((variant, areaKey) in listOf("raw" to "areaRaw", "stitched" to "areaStitched")) {
                        val area = obj.getJSONArray(areaKey)
                        val ctx = RecognitionContext.builder().setPreContext("")
                            .setWritingArea(WritingArea(area.getDouble(0).toFloat(), area.getDouble(1).toFloat())).build()
                        val ink = mlInk(obj.getJSONArray(variant))
                        val t0 = System.nanoTime()
                        val result = Tasks.await(recognizer.recognize(ink, ctx), 60, TimeUnit.SECONDS)
                        val ms = (System.nanoTime() - t0) / 1e6
                        val candidates = JSONArray()
                        result.candidates.take(3).forEach { candidates.put(it.text) }
                        res.put(variant, candidates).put("${variant}Ms", ms)
                    }
                    out.write(res.toString()); out.newLine()
                }
            }
        }
        recognizer.close()
    }
}
