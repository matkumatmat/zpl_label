import pandas as pd
import numpy as np
import logging
#from datetime import datetime
import os
#from ortools.linear_solver import pywraplp
from typing import List, Dict

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logging.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Product:
    def __init__(self, id, name, length, width, height, quantity):
        self.id = id
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.quantity = quantity  # Jumlah produk yang tersedia

    def volume(self):
        return self.length * self.width * self.height

def greedy_packing(products, container_dimensions):
    container_length, container_width, container_height = container_dimensions
    container_volume = container_length * container_width * container_height
    
    # Urutkan produk berdasarkan volume secara menurun
    products.sort(key=lambda x: x.volume(), reverse=True)
    
    packed_boxes = []
    remaining_products = products[:]  # Salin produk yang tersedia

    while remaining_products:  # Selama masih ada produk yang tersisa
        current_box = []
        used_volume = 0  # Volume yang digunakan dalam kotak saat ini
        remaining_volume = container_volume  # Reset volume untuk kotak baru

        for product in remaining_products:
            product_volume = product.volume()
            total_packed = 0  # Menghitung total produk yang telah dimasukkan ke dalam box
            
            while product.quantity > 0 and remaining_volume >= product_volume:
                # Cek jika produk dapat dimasukkan ke dalam wadah
                current_box.append(product)
                used_volume += product_volume
                remaining_volume -= product_volume
                product.quantity -= 1
                total_packed += 1  # Increment total produk yang dimasukkan
            
            if total_packed > 0:
                logger.info(f"Packed: {product.name} (ID: {product.id}) - Total packed: {total_packed}")

        if current_box:
            # Simpan kotak yang sudah terisi
            packed_boxes.append((current_box, used_volume))

        # Hapus produk yang sudah habis dari daftar produk yang tersisa
        remaining_products = [p for p in remaining_products if p.quantity > 0]

    return packed_boxes

    return packed_boxes
class VaccinePacking:
    def __init__(self, input_file: str):
        self.box_dimensions = (45, 60, 30)  # Dimensi wadah (panjang, lebar, tinggi)
        self.input_data = pd.read_excel(input_file, sheet_name="PENGIRIMANN")
        self.validate_data()
    def validate_data(self):
        # Cek alamat yang kosong atau NaN
        invalid_rows = self.input_data[self.input_data['db_ALAMAT.JALAN'].isna()]

        if not invalid_rows.empty:
            logger.warning(f"Ditemukan {len(invalid_rows)} baris dengan data alamat tidak valid")
            
            # Menyimpan alamat yang kosong ke dalam file
            with open('alamatkosong.txt', 'w') as f:
                for idx, row in invalid_rows.iterrows():
                    alamat_kosong = f"Baris {idx}: Alamat kosong untuk {row['ALAMAT']}\n"
                    f.write(alamat_kosong)
                    logger.warning(alamat_kosong.strip())  # Log ke konsol
            
            # Mengisi nilai kosong dengan "data alamat kosong"
            self.input_data['db_ALAMAT.JALAN'].fillna("data alamat kosong", inplace=True)
    def aggregate_products(self, address_group):
        """Mengagregasi data produk berdasarkan ID."""
        grouped_products = address_group.groupby('ID').agg({
            'NAMA BARANG': 'first',
            'DISTRIBUSI': 'sum',
            'db_DIMENSI_PRODUK.Panjang': 'first',
            'db_DIMENSI_PRODUK.Lebar': 'first',
            'db_DIMENSI_PRODUK.Tinggi': 'first',
            'TGL KIRIM': 'first',
            'db_ALAMAT.JALAN': 'first',
            'db_ALAMAT.PROVINSI': 'first',
            'db_ALAMAT.PIC': 'first',
            'db_ALAMAT.NO-TEL': 'first'
        }).reset_index()

        return grouped_products
    def pack_vaccines(self):
        final_packed_data = []
        
        # Group by alamat
        for address, address_group in self.input_data.groupby('db_ALAMAT.NAMA'):
            logger.info(f"\nMemproses alamat: {address}")
            grouped_products = self.aggregate_products(address_group)
            
            # Pisahkan produk khusus (ID 01.014)
            special_products = grouped_products[grouped_products['ID'] == '01.014']
            regular_products = grouped_products[grouped_products['ID'] != '01.014']
            
            # Ambil informasi alamat
            address_info = {
                'db_ALAMAT.JALAN': regular_products.iloc[0]['db_ALAMAT.JALAN'],
                'db_ALAMAT.PROVINSI': regular_products.iloc[0]['db_ALAMAT.PROVINSI'],
                'db_ALAMAT.PIC': regular_products.iloc[0]['db_ALAMAT.PIC'],
                'db_ALAMAT.NO-TEL': regular_products.iloc[0]['db_ALAMAT.NO-TEL'],
                'TANGGAL': regular_products.iloc[0]['TGL KIRIM']
            }
            
            # Buat daftar produk
            product_objects = []
            for index, row in regular_products.iterrows():
                quantity = int(row['DISTRIBUSI'])  # Ambil jumlah dari kolom DISTRIBUSI
                product = Product(row['ID'], row['NAMA BARANG'], 
                                  row['db_DIMENSI_PRODUK.Panjang'], 
                                  row['db_DIMENSI_PRODUK.Lebar'], 
                                  row['db_DIMENSI_PRODUK.Tinggi'], 
                                  quantity)  # Set quantity sesuai dengan jumlah yang diambil
                product_objects.append(product)

            # Pack produk
            packed_boxes = greedy_packing(product_objects, self.box_dimensions)

            # Buat rekaman output
            for box_idx, (box_content, used_volume) in enumerate(packed_boxes, 1):
                product_info = {}
                for product in box_content:
                    if product.id not in product_info:
                        product_info[product.id] = f"{product.id}-{product.name}:{1}"  # Mulai dari 1
                    else:
                        current_quantity = int(product_info[product.id].split(':')[1].strip('()'))
                        product_info[product.id] = f"{product.id}-{product.name}:({current_quantity + 1})"

                # Gabungkan semua informasi produk dalam satu string
                product_info 
                product_info_string = ', '.join(product_info.values())
                
                box_info = {
                    'TANGGAL': address_info['TANGGAL'],
                    'db_ALAMAT.NAMA': address,
                    'db_ALAMAT.JALAN': address_info['db_ALAMAT.JALAN'],
                    'db_ALAMAT.PROVINSI': address_info['db_ALAMAT.PROVINSI'],
                    'db_ALAMAT.PIC': address_info['db_ALAMAT.PIC'],
                    'db_ALAMAT.NO-TEL': address_info['db_ALAMAT.NO-TEL'],
                    'PRODUK': product_info_string,
                    'NO_BOX': box_idx,
                    'TOTAL_BOX': len(packed_boxes),
                    'VOLUME_DIGUNAKAN': used_volume
                }
                final_packed_data.append(box_info)

        # Simpan hasil
        self.save_results(final_packed_data)
    def save_results(self, packed_data):
        """ Menyimpan hasil akhir ke dalam file CSV."""
        final_df = pd.DataFrame(packed_data)
        final_df.to_csv('hasil_packing.csv', index=False)
        logger.info("\nProses packing selesai. Hasil disimpan di hasil_packing.csv")


def main():
    try:
        input_file = r'C:\Users\rahmat.wahyu\Desktop\project excel\PROJECT LABEL\RENCANA DISTRIBUSI 2024 (1).xlsx'
        packer = VaccinePacking(input_file)
        packer.pack_vaccines()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()