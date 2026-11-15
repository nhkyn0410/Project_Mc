package vn.handwriting.line

import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.ln1p

/** Bản Kotlin của training/decoder.py. */
class CtcDecoder(
    chars: String,
    private val lm: NGramModel?,
    private val alpha: Double,
    private val beta: Double,
    private val beam: Int = 30,
    private val topChars: Int = 8,
    private val minProb: Float = 0.002f,
) {
    private val chars = chars.toCharArray()
    private val index = HashMap<Char, Int>().also { m -> this.chars.forEachIndexed { i, c -> m[c] = i } }
    private val blank = this.chars.size
    private val space = index.getValue(' ')

    private class LmState(val score: Double, val a: Int, val b: Int, val current: String)
    private class Entry(var lb: Double, var lnb: Double, val state: LmState)

    private fun add(x: Double, y: Double): Double {
        val a = maxOf(x, y)
        val b = minOf(x, y)
        return if (b < a - 30) a else a + ln1p(exp(b - a))
    }

    private fun wordScore(s: LmState): LmState {
        val t = token(s.current)
        if (t.isEmpty()) return LmState(s.score, s.a, s.b, "")
        val model = lm ?: return LmState(s.score + beta, s.a, s.b, "")
        val w = model.wordId(t)
        return LmState(s.score + alpha * model.logP(w, s.b, s.a) + beta, s.b, w, "")
    }

    /** probs theo dạng T dòng, mỗi dòng có số phần tử bằng số nhãn. Kết quả xếp điểm giảm dần. */
    fun decode(probs: Array<FloatArray>, keep: Int = 3): List<String> {
        var current = LinkedHashMap<String, Entry>()
        current[""] = Entry(0.0, NEG, LmState(0.0, -1, -1, ""))
        for (row in probs) {
            val labels = (row.indices).sortedByDescending { row[it] }.take(topChars)
                .filter { it != blank && row[it] >= minProb }
            val blankLp = ln(row[blank].coerceAtLeast(1e-12f).toDouble())
            val next = HashMap<String, Entry>(beam * (topChars + 2))
            fun update(prefix: String, lb: Double, lnb: Double, state: LmState) {
                val old = next[prefix]
                if (old == null) next[prefix] = Entry(lb, lnb, state)
                else { old.lb = add(old.lb, lb); old.lnb = add(old.lnb, lnb) }
            }
            for ((prefix, e) in current) {
                val total = add(e.lb, e.lnb)
                update(prefix, total + blankLp, NEG, e.state)
                val last = if (prefix.isEmpty()) -1 else index.getValue(prefix.last())
                if (last >= 0 && e.lnb > NEG / 2) {
                    update(prefix, NEG, e.lnb + ln(row[last].coerceAtLeast(1e-12f).toDouble()), e.state)
                }
                for (k in labels) {
                    val base = if (k == last) e.lb else total
                    if (base <= NEG / 2) continue
                    val state = if (k == space) wordScore(e.state)
                    else LmState(e.state.score, e.state.a, e.state.b, e.state.current + chars[k])
                    update(prefix + chars[k], NEG, base + ln(row[k].coerceAtLeast(1e-12f).toDouble()), state)
                }
            }
            val ranked = next.entries.sortedByDescending { add(it.value.lb, it.value.lnb) + it.value.state.score }
            current = LinkedHashMap()
            for (entry in ranked.take(beam)) current[entry.key] = entry.value
        }
        return current.entries
            .map { (prefix, e) -> Pair(add(e.lb, e.lnb) + wordScore(e.state).score, prefix.trim()) }
            .sortedByDescending { it.first }
            .take(keep)
            .map { it.second }
    }

    companion object {
        private const val NEG = -1e9
        private val NOT_WORD = Regex("[^\\p{L}\\p{Nd}\\p{Nl}\\p{No}_]")
        private val DIGIT = Regex("\\p{Nd}")

        fun token(raw: String): String {
            val t = NOT_WORD.replace(raw, "").lowercase(java.util.Locale.ROOT)
            return if (DIGIT.containsMatchIn(t)) "<số>" else t
        }
    }
}
