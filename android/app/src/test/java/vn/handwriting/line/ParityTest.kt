package vn.handwriting.line

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Đối chiếu bản Kotlin với bản Python tham chiếu, trên bộ mẫu do training/export_assets.py sinh ra. */
class ParityTest {
    private fun bytes(name: String) = javaClass.classLoader!!.getResourceAsStream(name)!!.use { it.readBytes() }
    private fun text(name: String) = String(bytes(name), Charsets.UTF_8)

    @Test
    fun stitchAndRenderMatchPython() {
        val params = text("params.txt").trim().split(" ")
        val lines = text("ink_parity.txt").split("\n").iterator()
        var cases = 0
        var differentPixels = 0
        var pixels = 0
        while (lines.hasNext()) {
            val head = lines.next()
            if (!head.startsWith("case")) continue
            val n = head.split(" ")[1].toInt()
            val strokes = (0 until n).map {
                val v = lines.next().trim().split(" ").map(String::toDouble)
                Stroke(DoubleArray(v.size / 2) { i -> v[2 * i] }, DoubleArray(v.size / 2) { i -> v[2 * i + 1] })
            }
            val rows = lines.next().trim().split(" ").map(String::toInt)
            val coords = lines.next().trim().split(" ").map(String::toDouble)
            val image = lines.next().trim().split(" ").map(String::toInt)
            assertEquals(rows, Ink.assignRows(strokes, 14.0, 90.0).toList())
            val stitched = Ink.stitch(strokes, 14.0, 90.0)
            val flat = stitched.flatMap { s -> (0 until s.size).flatMap { listOf(s.xs[it], s.ys[it]) } }
            assertEquals(coords.size, flat.size)
            coords.indices.forEach { assertEquals(coords[it], flat[it], 1e-6) }
            val rendered = Ink.render(stitched, params[5].toInt(), params[6].toDouble())
            assertEquals(image.size, rendered.size)
            image.indices.forEach { if (image[it] != rendered[it]) differentPixels++ }
            pixels += image.size
            cases++
        }
        assertEquals(12, cases)
        assertTrue("khác $differentPixels trên $pixels điểm ảnh", differentPixels.toDouble() / pixels < 0.0005)
    }

    @Test
    fun decoderMatchesPython() {
        val p = text("params.txt").trim().split(" ")
        val alpha = p[0].toDouble()
        val beta = p[1].toDouble()
        val steps = p[2].toInt()
        val labels = p[3].toInt()
        val count = p[4].toInt()
        val floats = ByteBuffer.wrap(bytes("decoder_probs.bin")).order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer()
        val decoder = CtcDecoder(text("chars.txt"), NGramModel(bytes("lm.bin")), alpha, beta)
        val expected = text("decoder_expected.txt").trim('\n').split("\n")
        assertEquals(count, expected.size)
        for (c in 0 until count) {
            val probs = Array(steps) { FloatArray(labels) { floats.get() } }
            assertEquals(expected[c].split("\t"), decoder.decode(probs))
        }
    }
}
