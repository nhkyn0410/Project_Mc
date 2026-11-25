package vn.handwriting.line

import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Đọc clm.bin, cùng định dạng và cùng cách tính với lớp CharNGramBin trong training/char_ngram.py. */
class CharNGramModel(data: ByteArray) {
    val order: Int
    private val symbols = HashMap<Char, Int>()
    private val unk: Int
    private val bos: Int
    val eos: Int
    private val keys: Array<IntArray>
    private val logp: Array<ByteArray>
    private val bow: Array<ByteArray?>
    private val stepLogp: Double
    private val stepBow: Double
    private val floorLog: Double

    init {
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        val magic = ByteArray(4).also { b.get(it) }
        require(String(magic, Charsets.US_ASCII) == "VNCL") { "clm.bin không hợp lệ" }
        b.int
        order = b.int
        val nChars = b.int
        for (i in 0 until nChars) {
            val raw = ByteArray(b.short.toInt() and 0xFFFF).also { b.get(it) }
            symbols[String(raw, Charsets.UTF_8)[0]] = i + 1
        }
        unk = nChars + 1
        bos = nChars + 2
        eos = nChars + 3
        stepLogp = b.float.toDouble()
        stepBow = b.float.toDouble()
        keys = Array(order) { IntArray(0) }
        logp = Array(order) { ByteArray(0) }
        bow = arrayOfNulls(order)
        for (n in 1..order) {
            val count = b.int
            keys[n - 1] = IntArray(count) { b.int }
            logp[n - 1] = ByteArray(count).also { b.get(it) }
            if (n < order) bow[n - 1] = ByteArray(count).also { b.get(it) }
        }
        floorLog = -255 * stepLogp
    }

    fun symbol(c: Char): Int = symbols[c] ?: unk

    /** Ký hiệu ngữ cảnh của một tiền tố: tối đa order - 1 ký tự cuối, thêm ký hiệu đầu câu nếu tiền tố ngắn. */
    fun contextOf(prefix: String): IntArray {
        val n1 = order - 1
        val tail = if (prefix.length > n1) prefix.substring(prefix.length - n1) else prefix
        val body = IntArray(tail.length) { symbol(tail[it]) }
        return if (prefix.length < n1) intArrayOf(bos) + body else body
    }

    private fun find(symbols: IntArray, from: Int, extra: Int): Int {
        val n = symbols.size - from + (if (extra >= 0) 1 else 0)
        if (n < 1 || n > order) return -1
        var h = -2128831035 // 2166136261 theo số nguyên có dấu
        for (i in from until symbols.size) h = (h xor symbols[i]) * 16777619
        if (extra >= 0) h = (h xor extra) * 16777619
        val i = keys[n - 1].binarySearch(h)
        return if (i >= 0) i else -1
    }

    private fun lp(n: Int, i: Int) = -(logp[n - 1][i].toInt() and 0xFF).toDouble() * stepLogp
    private fun bw(n: Int, i: Int) = bow[n - 1]?.let { -(it[i].toInt() and 0xFF).toDouble() * stepBow } ?: 0.0

    /** log P(w | context), context là ký hiệu, ký hiệu gần nhất ở cuối. */
    fun logP(contextIn: IntArray, w: Int): Double {
        val context = if (contextIn.size > order - 1) contextIn.copyOfRange(contextIn.size - (order - 1), contextIn.size) else contextIn
        var start = 0
        // Ngữ cảnh dài nhất đã có trong mô hình. Ngữ cảnh chưa có thì không có n-gram nào dài hơn nó.
        while (start < context.size && find(context, start, -1) < 0) start++
        var total = 0.0
        for (s in start..context.size) {
            val len = context.size - s
            val hit = find(context, s, w)
            if (hit >= 0) return total + lp(len + 1, hit)
            if (len > 0) {
                val c = find(context, s, -1)
                if (c >= 0) total += bw(len, c)
            }
        }
        return total + floorLog
    }
}
