# HammingSimulator2
# BLM230 Bilgisayar Mimarisi Dönem Projesi

## ⬡ Hamming Error-Correcting Code (SEC) Simülatörü

Bu proje, **Bursa Teknik Üniversitesi Bilgisayar Mühendisliği Bölümü** BLM230 Bilgisayar Mimarisi dersi kapsamında geliştirilmiştir. Proje, bilgisayar mimarisinde bellek güvenliğini ve veri iletim doğruluğunu sağlamak amacıyla kullanılan **Hamming Tek Hata Düzeltme (Single Error Correction - SEC)** mekanizmasının donanımsal işleyişini görselleştiren interaktif bir simülasyon yazılımıdır.

---
Kodun Dosyası: https://github.com/ferideyalcinkaya/HammingSimulator2/blob/main/hamming_simulator.py

Video Linki: https://www.youtube.com/watch?v=0fWqbEDYUNc
## 👥 Geliştirici Bilgileri
* **Ad Soyad:** Feride Saygı Yalçınkaya
* **Öğrenci No:** 22360859064
* **Üniversite / Bölüm:** Bursa Teknik Üniversitesi - Bilgisayar Mühendisliği

---

## 📌 Proje Amacı ve Kapsamı
Yazılım; 8, 16 ve 32 bit uzunluğundaki veriler üzerinde Hamming Code algoritmasını uygulayarak verilerin bellekte saklanmasını, hatasız okunmasını ve hatanın donanımsal bloklar (Encoder, Memory, Compare, Corrector) arasındaki akışını simüle eder.

### Temel Fonksiyonlar:
1. **Dinamik Kodlama (Encoding):** Kullanıcı tarafından girilen (veya rastgele üretilen) 8, 16 veya 32 bitlik binary veriler için gerekli parity bit sayısını ve pozisyonlarını hesaplayarak Hamming kodunu üretir ve belleğe yazar.
2. **Yapay Hata Enjeksiyonu (Error Injection):** Bellekte saklanan Hamming bloğunun istenilen herhangi bir bit pozisyonu üzerinde (1-indexed) yapay olarak hata (bit evirme) oluşturulmasına izin verir.
3. **Sendrom Analizi ve Teşhis (Compare):** Değiştirilen veya bozulan veri bloğunu okurken, her bir parity kontrol grubunu yeniden değerlendirerek bir **Sendrom Kelimesi (Syndrome Word)** üretir. Bu kelime üzerinden hatalı bitin konumunu ve tipini (Data / Parity) teyit eder.
4. **Otomatik Onarım (Corrector):** Teşhis edilen hatalı biti evirerek orijinal veri bloğunu kayıpsız bir şekilde kurtarır ve çıkışa (`Data Out`) aktarır.

---

## 🏗️ Mimari ve Donanımsal Blok Akışı
Simülatör tasarımı, veri akış şemasındaki donanımsal birimlerin çalışma prensibine sadık kalınarak modellenmiştir:

* **f (Üreteç Fonksiyonu):** Giriş verisinden kontrol bitlerini ($K$) üretir.
* **Memory (Bellek Tablosu):** Veriyi ($M$) ve kontrol bitlerini ($K$) bir arada saklar.
* **Compare (Karşılaştırma Ünitesi):** Bellekten okunan veriyle yeniden hesaplanan parity bitlerini XOR işlemine sokarak **Sendrom Kelimesini** oluşturur. Eğer hata varsa `Error Signal` hattını aktif eder.
* **Corrector (Düzeltici Blok):** Sendrom kelimesinin işaret ettiği indeksteki biti düzelterek temiz veriyi dışarıya aktarır.

---

## 🎨 Ekran Görüntüsü & Arayüz Tasarımı
Yazılım, kullanıcı dostu ve modern bir "Dark Mode" siber estetik temaya sahiptir. Bit bazlı değişimlerin anlık izlenebilmesi için dinamik renk kodlu bir **Bit Izgarası (Bit Grid)** ve tüm donanımsal adımları kronolojik raporlayan bir **İşlem Günlüğü (Log Panel)** içerir.

* 🟣 **Mor Hücreler:** Parity (P) Kontrol Bitleri
* 🟢 **Yeşil Hücreler:** Orijinal Veri (D) Bitleri
* 🔴 **Kırmızı Hücreler:** Yapay Hata Enjekte Edilmiş Bozuk Bitler
* ✨ **Canlı Yeşil:** Başarıyla Onarılmış ve Kurtarılmış Bitler

---

## ⚙️ Kurulum ve Çalıştırma

### Gereksinimler
Proje standart Python 3.x kütüphaneleri kullanılarak geliştirildiğinden ek bir harici paket kurulumuna (pip install vb.) ihtiyaç duymaz. Grafik arayüz için `tkinter` kütüphanesi yeterlidir.

### Çalıştırma Adımları
1. Depoyu bilgisayarınıza indirin veya klonlayın.
2. Terminal veya komut satırını açarak proje dizinine gidin.
3. Aşağıdaki komutu çalıştırarak simülatörü başlatın:

```bash
python main.py


