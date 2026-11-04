#!/usr/bin/env bash
set -euo pipefail

BRAIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENTRIES_DIR="$BRAIN_DIR/entries"
INDEX_FILE="$BRAIN_DIR/INDEX.md"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <keyword1> [keyword2 ...]"
    exit 1
fi

echo "=== RÀ SOÁT SECOND BRAIN: TÌM KIẾM TRÙNG LẶP ==="
MATCH_FOUND=0

for kw in "$@"; do
    echo "--- Khóa tìm kiếm: '$kw' ---"
    
    # 1. Tìm trong INDEX.md
    if grep -in "$kw" "$INDEX_FILE" > /dev/null 2>&1; then
        echo "[INDEX.md] Khớp tại các mục:"
        grep -in -C 1 "$kw" "$INDEX_FILE" | head -n 10
        MATCH_FOUND=1
    fi

    # 2. Tìm trong entries/
    if rg -il "$kw" "$ENTRIES_DIR" 2>/dev/null | grep -q .; then
        echo "[entries/] Các file đã có đề cập:"
        rg -il "$kw" "$ENTRIES_DIR" | while read -r f; do
            rel_path="${f#$BRAIN_DIR/}"
            echo "  -> $rel_path"
        done
        MATCH_FOUND=1
    fi
done

echo ""
if [ "$MATCH_FOUND" -eq 1 ]; then
    echo ">>> KẾT LUẬN: ĐÃ CÓ FILE LIÊN QUAN TRONG HỆ THỐNG!"
    echo ">>> HÀNH ĐỘNG BẮT BUỘC: Đọc file cũ và CẬP NHẬT TRỰC TIẾP, không tạo file mới trừ khi domain hoàn toàn độc lập."
    exit 0
else
    echo ">>> KẾT LUẬN: Không tìm thấy trùng lặp trực tiếp."
    echo ">>> HÀNH ĐỘNG: Cho phép tạo file mới theo templates/ENTRY-TEMPLATE.md."
    exit 0
fi
