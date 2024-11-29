import pandas as pd
import socket

# Baca file CSV
data = pd.read_csv(r'C:\Users\rahmat.wahyu\Desktop\project excel\hasil_packing.csv')

# Fungsi untuk mengirim data ZPL ke printer Zebra
def send_to_printer(ip, port, zpl_code):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, port))
            sock.sendall(zpl_code.encode('utf-8'))
        print("ZPL berhasil dikirim ke printer.")
    except Exception as e:
        print(f"Kesalahan saat mengirim ke printer: {e}")

# Template ZPL sederhana
zpl_template = """
^XA
^FO50,50^ADN,36,20^FD{tanggal}^FS
^FO50,100^ADN,36,20^FD{nama_alamat}^FS
^FO50,150^ADN,36,20^FD{jalan_alamat}^FS
^FO50,200^ADN,36,20^FD{provinsi_alamat}^FS
^FO50,250^ADN,36,20^FD{pic_alamat} - {notel_alamat}^FS
^FO50,300^ADN,36,20^FDProduk: {produk}^FS
^FO50,350^ADN,36,20^FDBox {no_box} dari {total_box}^FS
^XZ
"""

# Loop melalui setiap baris data dan kirim ZPL ke printer
for index, row in data.iterrows():
    zpl_code = zpl_template.format(
        tanggal=row['TANGGAL'],
        nama_alamat=row['db_ALAMAT.NAMA'],
        jalan_alamat=row['db_ALAMAT.JALAN'],
        provinsi_alamat=row['db_ALAMAT.PROVINSI'],
        pic_alamat=row['db_ALAMAT.PIC'],
        notel_alamat=row['db_ALAMAT.NO-TEL'],
        produk=row['PRODUK'],
        no_box=row['NO_BOX'],
        total_box=row['TOTAL_BOX']
    )
    
    # Kirim ke printer (ubah IP dan port sesuai printer Anda)
    printer_ip = "192.168.0.100"  # Ganti dengan IP printer
    printer_port = 9100           # Biasanya port 9100 untuk printer Zebra
    send_to_printer(printer_ip, printer_port, zpl_code)
