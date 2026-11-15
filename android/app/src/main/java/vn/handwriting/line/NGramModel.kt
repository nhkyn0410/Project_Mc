package vn.handwriting.line

import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.ln
import kotlin.math.max
import kotlin.math.min
import kotlin.math.pow

/** Đọc lm.bin, cùng định dạng và cùng cách tính với training/lm_binary.py. */
class NGramModel(data: ByteArray) {
    private val vocab = HashMap<String, Int>()
    private val uni: IntArray
    private val biKeys: IntArray
    private val biQ: ByteArray
    private val triKeys: IntArray
    private val triQ: ByteArray
    private val total: Double
    private val floorLog: Double

    init {
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        val magic = ByteArray(4).also { b.get(it) }
        require(String(magic, Charsets.US_ASCII) == "VNLM") { "lm.bin không hợp lệ" }
        b.int
        val n = b.int
        total = b.double
        for (i in 0 until n) {
            val raw = ByteArray(b.short.toInt() and 0xFFFF).also { b.get(it) }
            vocab[String(raw, Charsets.UTF_8)] = i
        }
        uni = IntArray(n) { b.int }
        val nBi = b.int
        biKeys = IntArray(nBi) { b.int }
        biQ = ByteArray(nBi).also { b.get(it) }
        val nTri = b.int
        triKeys = IntArray(nTri) { b.int }
        triQ = ByteArray(nTri).also { b.get(it) }
        floorLog = ln(0.5 / total)
    }

    fun wordId(token: String): Int = vocab[token] ?: -1

    private fun find(keys: IntArray, q: ByteArray, key: Int): Int {
        val i = keys.binarySearch(key)
        return if (i >= 0) q[i].toInt() and 0xFF else -1
    }

    private fun bigram(a: Int, b: Int): Double {
        val q = find(biKeys, biQ, (a shl VOCAB_BITS) or b)
        return if (q < 0) -1.0 else BASE.pow(q)
    }

    fun logP(w: Int, b: Int, a: Int): Double {
        if (w < 0) return floorLog
        var penalty = 0.0
        if (a >= 0 && b >= 0) {
            val context = bigram(a, b)
            val q = find(triKeys, triQ, fnv3(a, b, w))
            if (q >= 0 && context > 0) return min(0.0, q * ln(BASE) - ln(context))
            penalty = ln(BACKOFF)
        }
        if (b >= 0) {
            val pair = bigram(b, w)
            if (pair > 0) return min(0.0, penalty + ln(pair) - ln(max(1.0, uni[b].toDouble())))
            penalty += ln(BACKOFF)
        }
        return penalty + ln(max(0.5, uni[w].toDouble()) / total)
    }

    private fun fnv3(a: Int, b: Int, w: Int): Int {
        var h = -2128831035 // 2166136261 theo số nguyên có dấu
        for (v in intArrayOf(a, b, w)) h = (h xor v) * 16777619
        return h
    }

    private companion object {
        const val BASE = 1.1
        const val BACKOFF = 0.4
        const val VOCAB_BITS = 15
    }
}
