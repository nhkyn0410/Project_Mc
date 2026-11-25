package vn.handwriting.line

import android.content.Context
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel

/**
 * Chạy mô hình và bộ giải mã. Chỉ gọi từ một luồng nền.
 * Nếu có clm.bin và params.txt có đủ trọng số, bộ giải mã dùng thêm n-gram ký tự,
 * trừ khi useCharLm là false (dùng để đo so sánh với cấu hình cũ).
 */
class Recognizer(context: Context, useCharLm: Boolean = true) {
    private val interpreter: Interpreter
    private val decoder: CtcDecoder
    private val input = ByteBuffer.allocateDirect(Ink.HEIGHT * Ink.WIDTH * 4).order(ByteOrder.nativeOrder())
    private val output: ByteBuffer
    private val steps: Int
    private val labels: Int
    private val maxInk: Int
    private val strokeWidth: Double
    val usesCharLm: Boolean

    class Result(val candidates: List<String>, val modelMs: Long, val decodeMs: Long, val renderMs: Long)

    init {
        val assets = context.assets
        val fd = assets.openFd("model.tflite")
        val model = FileInputStream(fd.fileDescriptor).channel
            .map(FileChannel.MapMode.READ_ONLY, fd.startOffset, fd.declaredLength)
        interpreter = Interpreter(model, Interpreter.Options().setNumThreads(4))
        val shape = interpreter.getOutputTensor(0).shape()
        steps = shape[1]
        labels = shape[2]
        output = ByteBuffer.allocateDirect(steps * labels * 4).order(ByteOrder.nativeOrder())
        val chars = assets.open("chars.txt").use { String(it.readBytes(), Charsets.UTF_8) }
        val lm = NGramModel(assets.open("lm.bin").use { it.readBytes() })
        val params = assets.open("params.txt").use { String(it.readBytes()).trim().split(" ") }
        val clm = if (useCharLm && params.size >= 6 && "clm.bin" in (assets.list("") ?: emptyArray())) {
            CharNGramModel(assets.open("clm.bin").use { it.readBytes() })
        } else null
        usesCharLm = clm != null
        decoder = CtcDecoder(
            chars, lm, params[0].toDouble(), params[1].toDouble(), clm = clm,
            alphaC = if (clm != null) params[4].toDouble() else 0.0,
            gammaC = if (clm != null) params[5].toDouble() else 0.0,
        )
        maxInk = params[2].toInt()
        strokeWidth = params[3].toDouble()
    }

    fun recognize(strokes: List<Stroke>, topPad: Double, rowPx: Double): Result {
        val t0 = System.nanoTime()
        val image = Ink.render(Ink.stitch(strokes, topPad, rowPx), maxInk, strokeWidth)
        input.rewind()
        for (v in image) input.putFloat(v / 255f)
        input.rewind()
        output.rewind()
        val t1 = System.nanoTime()
        // Toán tử LSTM giữ trạng thái giữa các lần chạy, phải đặt lại trước mỗi dòng.
        interpreter.resetVariableTensors()
        interpreter.run(input, output)
        val t2 = System.nanoTime()
        output.rewind()
        val probs = Array(steps) { FloatArray(labels) { output.float } }
        val candidates = decoder.decode(probs)
        val t3 = System.nanoTime()
        return Result(candidates, (t2 - t1) / 1_000_000, (t3 - t2) / 1_000_000, (t1 - t0) / 1_000_000)
    }
}
