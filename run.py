import requests
from requests.exceptions import RequestException
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_proxies(file_path):
    """Memuat proxy dari file teks"""
    with open(file_path, 'r') as file:
        proxies = file.readlines()
    return [proxy.strip() for proxy in proxies]

def get_proxy_type(ip):
    """Mengambil tipe proxy (Datacenter atau Residential) dengan menggunakan API eksternal"""
    try:
        # Menggunakan layanan API untuk mendeteksi tipe IP (dapat diganti dengan layanan lain jika diperlukan)
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        # Mengambil informasi tipe IP dari data yang diterima
        org = data.get("org", "")
        if "AS" in org:
            return "Datacenter"  # Deteksi berdasarkan organisasi (misalnya, pusat data)
        else:
            return "Residential"  # Jika tidak terdeteksi sebagai pusat data, anggap sebagai residential
    except Exception as e:
        logger.error(f"Kesalahan saat mendeteksi tipe proxy untuk IP {ip}: {e}")
        return "Unknown"  # Jika gagal mendeteksi, anggap sebagai tidak diketahui

def test_proxy(proxy, test_url="https://httpbin.org/ip", timeout=5):
    """
    Menguji apakah proxy dapat digunakan untuk mengakses URL.
    Menggunakan URL https://httpbin.org/ip sebagai tes untuk mendapatkan IP.
    Timeout diatur ke 5 detik.
    """
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }

    try:
        # Kirim permintaan GET dengan proxy dan timeout 5 detik
        response = requests.get(test_url, proxies=proxy_dict, timeout=timeout)
        if response.status_code == 200:
            # Mengambil IP yang digunakan untuk mengakses
            ip_used = response.json()['origin']
            proxy_type = get_proxy_type(ip_used)
            logger.info(f"Proxy {proxy} berhasil, IP yang digunakan: {ip_used}, Tipe: {proxy_type}")
            return True, proxy_type
        else:
            logger.error(f"Proxy {proxy} gagal, status code: {response.status_code}")
            return False, "Unknown"
    except RequestException as e:
        logger.error(f"Proxy {proxy} gagal, kesalahan: {e}")
        return False, "Unknown"

def save_proxy_to_file(proxy, is_active=True, active_file='aktif.txt', dead_file='dead.txt'):
    """Menyimpan proxy ke file yang sesuai tanpa menyertakan tipe proxy"""
    file_name = active_file if is_active else dead_file
    with open(file_name, 'a') as file:
        file.write(proxy + '\n')

def check_proxies(file_path):
    """Memeriksa daftar proxy dari file proxies.txt"""
    proxies = load_proxies(file_path)
    for proxy in proxies:
        logger.info(f"Memeriksa proxy: {proxy}")
        is_active, proxy_type = test_proxy(proxy)
        if is_active:
            save_proxy_to_file(proxy, is_active=True)  # Menyimpan proxy aktif tanpa tipe
        else:
            save_proxy_to_file(proxy, is_active=False)  # Menyimpan proxy mati tanpa tipe

# Contoh penggunaan
file_path = 'proxies.txt'  # Ganti dengan path ke file yang berisi daftar proxy
check_proxies(file_path)
