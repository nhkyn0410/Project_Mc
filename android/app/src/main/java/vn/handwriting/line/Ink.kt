package vn.handwriting.line

import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.max
import kotlin.math.min

/** Một nét: các tọa độ x, y theo khung viết. */
class Stroke(val xs: DoubleArray, val ys: DoubleArray) {
    val size get() = xs.size
}

/** Bản Kotlin của training/ink.py. Mọi thay đổi phải làm ở cả hai nơi. */
object Ink {
    const val WIDTH = 512
    const val HEIGHT = 64
    private const val MARGIN = 8
    private const val SUPERSAMPLE = 4
    private const val STROKE_WIDTH = 1.2
    private const val BODY_GUESS = 0.35
    private const val BODY_MIN = 0.6
    private const val BODY_MAX = 1.5
    private const val NEW_LINE_DROP = 1.2
    private const val DESCENDER_DROP = 0.5
    private const val RETURN_SHIFT = 2.0
    private const val FLAT = 0.4
    private const val UP_RETURN = 1.2

    private fun ptp(a: DoubleArray) = a.max() - a.min()
    private const val MAX_GAP = 2.0
    private const val GAP_RATIO = 0.7
    private const val SCALE_MIN = 0.7
    private const val SCALE_MAX = 1.4

    /** Đỉnh thân chữ, đường chân chữ và chiều cao thân chữ của một nhóm nét. */
    private class Body(val top: Double, val base: Double, val height: Double)

    /** Phân vị theo nội suy tuyến tính, giống numpy.percentile. */
    private fun percentile(values: DoubleArray, q: Double): Double {
        val sorted = values.sortedArray()
        val rank = q / 100.0 * (sorted.size - 1)
        val low = floor(rank).toInt()
        val high = min(low + 1, sorted.size - 1)
        return sorted[low] + (sorted[high] - sorted[low]) * (rank - low)
    }

    private fun median(values: List<Double>): Double {
        val s = values.sorted()
        val n = s.size
        return if (n % 2 == 1) s[n / 2] else (s[n / 2 - 1] + s[n / 2]) / 2.0
    }

    private fun body(group: List<Stroke>): Body {
        val ys = DoubleArray(group.sumOf { it.size })
        var p = 0
        for (s in group) { s.ys.copyInto(ys, p); p += s.size }
        val top = percentile(ys, 15.0)
        val base = percentile(ys, 85.0)
        return Body(top, base, max(1.0, base - top))
    }

    /**
     * Một lượt gán nét vào dòng chữ theo thứ tự viết. adapt đúng: chiều cao thân chữ lấy theo dòng đang viết,
     * kẹp trong [BODY_MIN, BODY_MAX] nhân hRef. adapt sai: chiều cao thân chữ bằng hRef cho mọi dòng.
     */
    private fun segment(strokes: List<Stroke>, hRef: Double, adapt: Boolean): IntArray {
        val lines = ArrayList<ArrayList<Int>>()
        val rows = IntArray(strokes.size)
        for (i in strokes.indices) {
            val s = strokes[i]
            if (lines.isEmpty()) {
                lines.add(arrayListOf(i))
                continue
            }
            val cur = lines.size - 1
            val group = lines[cur].map { strokes[it] }
            val b = body(group)
            val h = if (adapt) min(max(b.height, BODY_MIN * hRef), BODY_MAX * hRef) else hRef
            val cy = s.ys.average()
            val drop = cy - b.base
            val right = group.maxOf { it.xs.max() }
            val flat = ptp(s.ys) < FLAT * h
            if (!flat && (drop > NEW_LINE_DROP * h || (drop > DESCENDER_DROP * h && s.xs.min() < right - RETURN_SHIFT * h))) {
                lines.add(arrayListOf(i))
                rows[i] = lines.size - 1
                continue
            }
            var target = cur
            if (cy < b.top - UP_RETURN * h && cur > 0) {
                // Nét viết bổ sung cho dòng trước: chỉ xét dòng có đường chân chữ thấp hơn tâm nét,
                // rồi chọn dòng có đỉnh thân chữ gần tâm nét hơn dòng đang viết.
                var nearest = b.top - cy
                for (k in 0 until cur) {
                    val o = body(lines[k].map { strokes[it] })
                    if (cy > o.base) continue
                    val d = max(o.top - cy, 0.0)
                    if (d < nearest) {
                        target = k
                        nearest = d
                    }
                }
            }
            lines[target].add(i)
            rows[i] = target
        }
        return rows
    }

    /** Gán mỗi nét vào một dòng chữ theo thứ tự viết, giống training/ink.py. topPad giữ lại cho cùng chữ ký. */
    fun assignRows(strokes: List<Stroke>, topPad: Double, rowPx: Double): IntArray {
        if (strokes.isEmpty()) return IntArray(0)
        val first = segment(strokes, BODY_GUESS * rowPx, true)
        val heights = (0..first.max()).map { u -> body(strokes.filterIndexed { i, _ -> first[i] == u }).height }
        return segment(strokes, median(heights), false)
    }

    /** Thu các khoảng trống ngang rộng hơn MAX_GAP lần chiều cao thân chữ về GAP_RATIO lần, giữ thứ tự nét. */
    fun closeGaps(group: List<Stroke>, height: Double): List<Stroke> {
        val order = group.indices.sortedBy { group[it].xs.min() }
        val shift = DoubleArray(group.size)
        var right = Double.NaN
        var total = 0.0
        for (i in order) {
            val left = group[i].xs.min()
            if (!right.isNaN() && left - right > MAX_GAP * height) total += left - right - GAP_RATIO * height
            shift[i] = total
            right = if (right.isNaN()) group[i].xs.max() else max(right, group[i].xs.max())
        }
        return group.mapIndexed { i, s -> Stroke(DoubleArray(s.size) { s.xs[it] - shift[i] }, s.ys.copyOf()) }
    }

    /** Nối các nhóm nét, mỗi nhóm một dòng chữ, thành dòng ảo: cùng cỡ chữ, cùng đường chân chữ, khoảng cách chuẩn. */
    fun stitchRows(input: List<List<Stroke>>): List<Stroke> {
        val bodies = input.map { body(it) }
        val groups = input.mapIndexed { g, group -> closeGaps(group, bodies[g].height) }
        val target = median(bodies.map { it.height })
        val out = ArrayList<Stroke>()
        var cursor = 0.0
        groups.forEachIndexed { g, group ->
            val scale = (target / bodies[g].height).coerceIn(SCALE_MIN, SCALE_MAX)
            val left = group.minOf { it.xs.min() }
            val right = group.maxOf { it.xs.max() }
            for (s in group) {
                out.add(Stroke(
                    DoubleArray(s.size) { cursor + (s.xs[it] - left) * scale },
                    DoubleArray(s.size) { (s.ys[it] - bodies[g].base) * scale },
                ))
            }
            cursor += (right - left) * scale + GAP_RATIO * target
        }
        return out
    }

    fun stitch(strokes: List<Stroke>, topPad: Double, rowPx: Double): List<Stroke> {
        val rows = assignRows(strokes, topPad, rowPx)
        if (rows.isEmpty()) return emptyList()
        return stitchRows((0..rows.max()).map { u -> strokes.filterIndexed { i, _ -> rows[i] == u } })
    }

    /** Trả về ảnh HEIGHT nhân WIDTH, theo hàng, giá trị 0 đến 255, nền bằng 0. maxInk khác 0 giới hạn chiều cao phần nét. */
    fun render(strokes: List<Stroke>, maxInk: Int = 0, strokeWidth: Double = STROKE_WIDTH): IntArray {
        val minX = strokes.minOf { it.xs.min() }
        val minY = strokes.minOf { it.ys.min() }
        val extentX = max(strokes.maxOf { it.xs.max() } - minX, 1.0)
        val extentY = max(strokes.maxOf { it.ys.max() } - minY, 1.0)
        val limit = if (maxInk > 0) maxInk else HEIGHT
        val scale = min((WIDTH - 2 * MARGIN - strokeWidth) / extentX, (limit - strokeWidth) / extentY)
        val newH = extentY * scale
        val k = SUPERSAMPLE
        val gridW = WIDTH * k
        val gridH = HEIGHT * k
        val grid = BooleanArray(gridW * gridH)
        val radius = strokeWidth * k / 2.0
        val offsetX = MARGIN + strokeWidth / 2
        val offsetY = (HEIGHT - newH) / 2
        for (s in strokes) {
            val px = DoubleArray(s.size) { ((s.xs[it] - minX) * scale + offsetX) * k }
            val py = DoubleArray(s.size) { ((s.ys[it] - minY) * scale + offsetY) * k }
            if (s.size == 1) stamp(grid, gridW, gridH, px[0], py[0], px[0], py[0], radius)
            for (i in 0 until s.size - 1) stamp(grid, gridW, gridH, px[i], py[i], px[i + 1], py[i + 1], radius)
        }
        val image = IntArray(WIDTH * HEIGHT)
        for (y in 0 until HEIGHT) for (x in 0 until WIDTH) {
            var count = 0
            for (v in 0 until k) for (u in 0 until k) if (grid[(y * k + v) * gridW + x * k + u]) count++
            image[y * WIDTH + x] = (count * 255 + k * k / 2) / (k * k)
        }
        return image
    }

    private fun stamp(grid: BooleanArray, w: Int, h: Int, ax: Double, ay: Double, bx: Double, by: Double, radius: Double) {
        val x0 = max(0, floor(min(ax, bx) - radius).toInt())
        val x1 = min(w - 1, ceil(max(ax, bx) + radius).toInt())
        val y0 = max(0, floor(min(ay, by) - radius).toInt())
        val y1 = min(h - 1, ceil(max(ay, by) + radius).toInt())
        val dx = bx - ax
        val dy = by - ay
        val length2 = dx * dx + dy * dy
        val r2 = radius * radius
        for (y in y0..y1) for (x in x0..x1) {
            val cx = x + 0.5
            val cy = y + 0.5
            val t = if (length2 == 0.0) 0.0 else (((cx - ax) * dx + (cy - ay) * dy) / length2).coerceIn(0.0, 1.0)
            val ex = cx - (ax + t * dx)
            val ey = cy - (ay + t * dy)
            if (ex * ex + ey * ey <= r2) grid[y * w + x] = true
        }
    }
}
