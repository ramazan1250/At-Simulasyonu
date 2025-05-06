import os
import sys

def find_and_save_py_files(root_folder, output_file, ignore_files=None):
    """
    Belirtilen klasör ve alt klasörlerindeki tüm .py dosyalarını bulur,
    içeriklerini göreceli yollarıyla birlikte tek bir .txt dosyasına kaydeder.
    Belirtilen dosyalar (ignore_files) atlanır.

    Args:
        root_folder (str): Aranacak başlangıç klasörünün yolu.
        output_file (str): Tüm içeriğin kaydedileceği .txt dosyasının adı.
        ignore_files (list, optional): İçeriği alınmayacak dosya adlarının listesi.
                                      Varsayılan olarak None (boş liste).
                                      Örn: ['extract.py', 'settings_local.py']
    """
    # ignore_files None ise boş bir listeye ayarlayalım
    if ignore_files is None:
        ignore_files = []

    found_files_count = 0
    processed_files_count = 0 # İşlenen dosya sayısını takip etmek için yeni sayaç
    try:
        # Çıkış dosyasını yazma modunda ('w') ve UTF-8 kodlamasıyla açıyoruz.
        # 'with' bloğu dosyanın iş bittiğinde otomatik kapanmasını sağlar.
        with open(output_file, 'w', encoding='utf-8') as outfile:
            print(f"'{root_folder}' klasöründe .py dosyaları aranıyor...")
            print(f"Atlanacak dosyalar: {ignore_files if ignore_files else 'Yok'}")

            # os.walk, belirtilen klasörden başlayarak tüm alt klasörleri gezer.
            for root, dirs, files in os.walk(root_folder):
                # İsteğe bağlı: Belirli klasörleri atlamak isterseniz (örn: venv, .git)
                # dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]

                for filename in files:
                    # Sadece .py uzantılı dosyalarla ilgileniyoruz
                    if filename.endswith('.py'):
                        found_files_count += 1
                        full_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(full_path, root_folder)
                        relative_path = relative_path.replace(os.sep, '/') # Windows uyumluluğu

                        # --- YENİ KONTROL: Dosya atlanacaklar listesinde mi? ---
                        if filename in ignore_files:
                            print(f"  -> Atlanıyor (ignore list): {relative_path}")
                            continue # Bu dosyayı atla ve döngünün sonraki adımına geç

                        # --- Dosya işleme kısmı (yukarıdaki kontrolü geçerse çalışır) ---
                        processed_files_count += 1
                        try:
                            # .py dosyasını okuma modunda ('r') ve UTF-8 kodlamasıyla açıyoruz.
                            with open(full_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()

                            # Çıktı dosyasına önce göreceli yolu yazıyoruz
                            outfile.write(f"({relative_path})\n")
                            # Sonra dosyanın içeriğini yazıyoruz
                            outfile.write(content)
                            # Dosyalar arasına boşluk ekleyerek okunabilirliği artırıyoruz
                            outfile.write("\n\n" + "="*80 + "\n\n")

                            print(f"  -> İşlendi: {relative_path}")

                        except FileNotFoundError:
                            print(f"Hata: Dosya okunamadı (beklenmedik durum): {full_path}", file=sys.stderr)
                        except UnicodeDecodeError:
                            print(f"Uyarı: '{full_path}' dosyası UTF-8 olarak okunamadı. Atlanıyor.", file=sys.stderr)
                        except Exception as e:
                            print(f"Hata: '{full_path}' dosyası okunurken hata oluştu: {e}", file=sys.stderr)

            print(f"\nİşlem tamamlandı.")
            print(f"Toplam {found_files_count} adet .py dosyası bulundu.")
            if processed_files_count > 0:
                print(f"{processed_files_count} adet dosya işlendi ve içerikleri birleştirildi.")
                print(f"Çıktı '{os.path.abspath(output_file)}' dosyasına kaydedildi.")
            elif found_files_count > 0:
                 print(f"Bulunan tüm .py dosyaları atlama listesinde olduğu için çıktı dosyası boş bırakıldı.")
                 # İsteğe bağlı: Boş dosyayı silmek isterseniz
                 # try:
                 #     os.remove(output_file)
                 #     print(f"Boş çıktı dosyası '{output_file}' silindi.")
                 # except OSError as e:
                 #     print(f"Uyarı: Boş çıktı dosyası silinemedi: {e}", file=sys.stderr)
            else:
                print(f"Belirtilen '{root_folder}' klasöründe ve alt klasörlerinde .py dosyası bulunamadı.")


    except FileNotFoundError:
        print(f"Hata: Başlangıç klasörü '{root_folder}' bulunamadı.", file=sys.stderr)
    except IOError as e:
        print(f"Hata: Çıktı dosyası '{output_file}' yazılamadı: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}", file=sys.stderr)

# --- Scriptin Çalıştırılacağı Kısım ---
if __name__ == "__main__":
    # Aranacak klasör ('.' mevcut klasör anlamına gelir)
    start_directory = '.'

    # Çıktı dosyasının adı
    output_filename = 'project_code.txt'

    # İçeriği alınmayacak dosyaların listesi
    # Bu scriptin kendisini de ekleyebiliriz (eğer adı extract.py ise)
    files_to_ignore = ['extract.py']
    # Başka dosyaları da ekleyebilirsiniz:
    # files_to_ignore = ['extract.py', 'config.py', 'local_settings.py']

    # Ana fonksiyonu çağır, ignore listesini de gönder
    find_and_save_py_files(start_directory, output_filename, ignore_files=files_to_ignore)