# Mở báo cáo bằng Word, cập nhật mọi trường (mục lục, danh mục bảng, danh mục hình, số trang),
# lưu lại thành .docx và xuất .pdf để kiểm tra bản dựng trang.
# Dùng: powershell -File cap-nhat.ps1 <tệp .docx vào> <tệp .docx ra> <tệp .pdf ra>
param([string]$In, [string]$OutDocx, [string]$OutPdf)
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open((Resolve-Path $In).Path, $false, $false)
  $doc.Fields.Update() | Out-Null
  foreach ($t in $doc.TablesOfContents) { $t.Update() | Out-Null }
  foreach ($t in $doc.TablesOfFigures) { $t.Update() | Out-Null }
  $doc.Repaginate()
  foreach ($t in $doc.TablesOfContents) { $t.UpdatePageNumbers() | Out-Null }
  foreach ($t in $doc.TablesOfFigures) { $t.UpdatePageNumbers() | Out-Null }
  $outFull = [System.IO.Path]::GetFullPath($OutDocx)
  $pdfFull = [System.IO.Path]::GetFullPath($OutPdf)
  $doc.SaveAs2($outFull, 16)
  $doc.ExportAsFixedFormat($pdfFull, 17)
  "trang: " + $doc.ComputeStatistics(2)
  "mục lục: " + $doc.TablesOfContents.Count + ", danh mục: " + $doc.TablesOfFigures.Count + ", trường: " + $doc.Fields.Count
  $doc.Close($false)
} finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
