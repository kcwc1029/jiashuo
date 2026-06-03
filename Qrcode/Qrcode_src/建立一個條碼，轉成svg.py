from pathlib import Path
import barcode

# 定義目標檔案的路徑
# Path(__file__).resolve() 會取得當前這個 .py 檔案的絕對路徑
# .parent 代表當前檔案所在的資料夾 (Qrcode_src)
# 再透過 / 符號串接，指到上一層的 Qrcode_outputs 資料夾
current_dir = Path(__file__).resolve().parent
output_dir = current_dir.parent / 'Qrcode_outputs'

# 產生並儲存條碼
EAN = barcode.get_barcode_class('ean13')
svg_barcode = EAN('5901234123457')

# python-barcode 的 save() 可以直接接受 pathlib.Path 物件
svg_barcode.save(str(output_dir / 'my_barcode_svg'))