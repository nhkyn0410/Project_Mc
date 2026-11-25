# Dựng toàn bộ báo cáo từ các tệp trong ../noi-dung.
# Các bước: dựng .docx thô để lấy thứ tự trích dẫn, tạo phần tài liệu tham khảo, dựng lại,
# thay công thức bằng OMML, mở bằng Word để cập nhật trường và xuất PDF, rồi hậu kỳ.
# Dùng: pwsh -NoProfile -File dung-bao-cao.ps1 [tên tệp ra, không có đuôi]
param([string]$Ra = "Bao-cao-do-an")
$ErrorActionPreference = 'Stop'
$cc = $PSScriptRoot
$goc = Split-Path -Parent $cc
$tam = Join-Path $goc "tam"
$nd = Join-Path $goc "noi-dung"
$bib = Join-Path (Split-Path -Parent $goc) "docs\tai-lieu-tham-khao.bib"
New-Item -ItemType Directory -Force $tam | Out-Null

$chinh = @("00-phan-dau.md", "01-chuong-1.md", "02-chuong-2.md", "03-chuong-3.md", "04-chuong-4.md", "05-chuong-5.md", "06-ket-luan.md") | ForEach-Object { Join-Path $nd $_ }
$tl = Join-Path $nd "07-tai-lieu.md"

function Invoke-Buoc([string]$ten, [scriptblock]$lenh) {
  Write-Output "== $ten"
  & $lenh
  if ($LASTEXITCODE -ne 0) { throw "Lỗi ở bước: $ten" }
}

Invoke-Buoc "dựng lần đầu" { node (Join-Path $cc "xay-dung.js") (Join-Path $tam "lan-dau.docx") @chinh }
Invoke-Buoc "tài liệu tham khảo" { python (Join-Path $cc "tai_lieu.py") $bib (Join-Path $tam "trich-dan.json") $tl }
Invoke-Buoc "dựng đầy đủ" { node (Join-Path $cc "xay-dung.js") (Join-Path $tam "tho.docx") @chinh $tl }
Invoke-Buoc "công thức" { python (Join-Path $cc "cong_thuc.py") (Join-Path $tam "tho.docx") (Join-Path $tam "cong-thuc.json") }
Invoke-Buoc "Word cập nhật trường" { pwsh -NoProfile -File (Join-Path $cc "cap-nhat.ps1") (Join-Path $tam "tho.docx") (Join-Path $goc "$Ra.docx") (Join-Path $goc "$Ra.pdf") }
Invoke-Buoc "hậu kỳ" { python (Join-Path $cc "hau_ky.py") (Join-Path $goc "$Ra.docx") }
