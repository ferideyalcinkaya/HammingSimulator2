"""
BLM230 - Bilgisayar Mimarisi
Hamming Error-Correcting Code Simülatörü
Desteklenen veri genişlikleri: 8, 16, 32 bit
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

# ─────────────────────────────────────────────
#  Hamming Hesaplama Fonksiyonları
# ─────────────────────────────────────────────

def parity_bit_count(data_bits: int) -> int:
    """Kaç adet parity bit gerektiğini hesapla (2^r >= m + r + 1)."""
    r = 0
    while (2 ** r) < (data_bits + r + 1):
        r += 1
    return r

def encode_hamming(data_bits_str: str) -> tuple[str, list[int], list[int]]:
    """Veri bitlerini Hamming koduna çevir."""
    m = len(data_bits_str)
    r = parity_bit_count(m)
    n = m + r  # toplam bit sayısı

    hamming = [0] * (n + 1)
    parity_pos = [2**i for i in range(r)]

    # Veri bitlerini (D) parity olmayan yerlere yerleştir (Soldan sağa mantığı)
    data_idx = 0
    for i in range(1, n + 1):
        if i not in parity_pos:
            hamming[i] = int(data_bits_str[data_idx])
            data_idx += 1

    # Parity bitlerini hesapla
    for p in parity_pos:
        xor_val = 0
        for i in range(1, n + 1):
            if i & p:
                xor_val ^= hamming[i]
        hamming[p] = xor_val

    result = ''.join(str(hamming[i]) for i in range(1, n + 1))
    return result, parity_pos, list(range(1, n + 1))

def detect_correct(hamming_str: str, r_bits_count: int) -> tuple[int, str]:
    """
    Sendrom kelimesini hesaplar, hatalı biti bulur ve düzeltir.
    Döndürür: (syndrome_decimal, corrected_str)
    """
    n = len(hamming_str)
    hamming = [0] + [int(b) for b in hamming_str]  # 1-indexed yapısı

    syndrome = 0
    # Parity bit adedi kadar kontrol gerçekleştiriyoruz
    for i in range(r_bits_count):
        p = 2 ** i
        xor_val = 0
        for j in range(1, n + 1):
            if j & p:
                xor_val ^= hamming[j]
        # Eğer XOR sonucu 1 ise, sendromun ilgili bitini setliyoruz
        if xor_val != 0:
            syndrome |= p

    corrected = list(hamming_str)
    # Sendrom 0'dan büyük ve toplam bit sayısından küçük/eşitse hata o indekstir
    if 0 < syndrome <= n:
        corrected[syndrome - 1] = '1' if hamming_str[syndrome - 1] == '0' else '0'

    return syndrome, ''.join(corrected)

def extract_data(hamming_str: str, r: int) -> str:
    """Hamming kodundan sadece orijinal veri bitlerini ayrıştırır."""
    n = len(hamming_str)
    parity_pos = {2**i for i in range(r)}
    data = []
    for i in range(1, n + 1):
        if i not in parity_pos:
            data.append(hamming_str[i - 1])
    return ''.join(data)

# ─────────────────────────────────────────────
#  Renk Paleti & Stiller
# ─────────────────────────────────────────────

BG         = "#0f1117"
PANEL      = "#1a1d2e"
CARD       = "#1e2235"
ACCENT     = "#4f9eff"
ACCENT2    = "#7c5cfc"
GREEN      = "#3ddc84"
RED_C      = "#ff4757"
YELLOW     = "#ffc107"
TEXT       = "#e8eaf6"
SUBTEXT    = "#8892a4"
BORDER     = "#2d3250"
PARITY_BG  = "#2a1f4e"
DATA_BG    = "#1a2e1a"
ERR_BG     = "#2e1a1a"

FONT_TITLE = ("Courier New", 18, "bold")
FONT_HEAD  = ("Courier New", 13, "bold")
FONT_MONO  = ("Courier New", 12)
FONT_SMALL = ("Courier New", 10)


# ─────────────────────────────────────────────
#  Ana Uygulama Sınıfı
# ─────────────────────────────────────────────

class HammingSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLM230 — Hamming Error-Correcting Code Simülatörü")
        self.configure(bg=BG)
        self.geometry("1150x850")

        # Durum Değişkenleri
        self.data_width   = tk.IntVar(value=8)
        self.data_input   = tk.StringVar()
        self.memory       = {}          # addr -> data_dict
        self.mem_addr     = 0

        self._build_ui()

    def _build_ui(self):
        # Başlık Bölümü
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill=tk.X, padx=20, pady=(15, 0))
        tk.Label(hdr, text="⬡  HAMMING SEC SİMÜLATÖRÜ", font=FONT_TITLE, fg=ACCENT, bg=BG).pack(side=tk.LEFT)
        tk.Label(hdr, text="BLM230 Bilgisayar Mimarisi", font=FONT_SMALL, fg=SUBTEXT, bg=BG).pack(side=tk.RIGHT, pady=6)

        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=20, pady=8)

        # Ana Panel Düzeni (Sol ve Sağ Kolonlar)
        main = tk.Frame(self, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=4)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        left  = tk.Frame(main, bg=BG)
        right = tk.Frame(main, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right.grid(row=0, column=1, sticky="nsew")

        self._build_encode_panel(left)
        self._build_memory_panel(left)
        self._build_bit_grid(left)
        self._build_error_panel(right)
        self._build_log_panel(right)

    def _build_encode_panel(self, parent):
        card = self._card(parent, "📥  VERİ GİRİŞİ & KODLAMA")
        card.pack(fill=tk.X, pady=(0, 10))

        row = tk.Frame(card, bg=CARD)
        row.pack(fill=tk.X, padx=12, pady=(5, 5))
        tk.Label(row, text="Veri Genişliği:", font=FONT_MONO, fg=TEXT, bg=CARD).pack(side=tk.LEFT)
        for w in (8, 16, 32):
            rb = tk.Radiobutton(row, text=f"{w} bit", variable=self.data_width, value=w,
                                command=self._on_width_change, fg=ACCENT, bg=CARD, selectcolor=PANEL,
                                activebackground=CARD, font=FONT_MONO)
            rb.pack(side=tk.LEFT, padx=10)

        inp_row = tk.Frame(card, bg=CARD)
        inp_row.pack(fill=tk.X, padx=12, pady=5)
        tk.Label(inp_row, text="Binary Veri:", font=FONT_MONO, fg=TEXT, bg=CARD, width=12, anchor="w").pack(side=tk.LEFT)
        self.entry_data = tk.Entry(inp_row, textvariable=self.data_input, font=FONT_MONO, bg=PANEL, fg=GREEN,
                                   insertbackground=GREEN, bd=0, relief=tk.FLAT, width=32)
        self.entry_data.pack(side=tk.LEFT, ipady=4, padx=(4, 8))
        self.entry_data.bind("<KeyRelease>", self._validate_input)

        tk.Button(inp_row, text="Rastgele", font=FONT_SMALL, bg=ACCENT2, fg="white",
                  bd=0, padx=10, pady=4, cursor="hand2", command=self._random_fill).pack(side=tk.LEFT, padx=4)

        self.lbl_bitcount = tk.Label(card, text="", font=FONT_SMALL, fg=SUBTEXT, bg=CARD)
        self.lbl_bitcount.pack(anchor="w", padx=14, pady=2)

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.pack(fill=tk.X, padx=12, pady=5)
        tk.Button(btn_row, text="▶  HAMMING KODLA & BELLEĞE YAZ", font=FONT_HEAD, bg=ACCENT, fg="white",
                  bd=0, padx=14, pady=6, cursor="hand2", command=self._encode_and_write).pack(fill=tk.X)

        # Düzenlenmiş Grid Bilgi Alanı
        info_frame = tk.Frame(card, bg=CARD)
        info_frame.pack(fill=tk.X, padx=12, pady=5)
        
        tk.Label(info_frame, text="Parity Sayısı:", font=FONT_MONO, fg=SUBTEXT, bg=CARD).grid(row=0, column=0, sticky="w")
        self.lbl_parity_count = tk.Label(info_frame, text="—", font=FONT_MONO, fg=ACCENT, bg=CARD)
        self.lbl_parity_count.grid(row=0, column=1, sticky="w", padx=10)

        tk.Label(info_frame, text="Hamming Kodu :", font=FONT_MONO, fg=SUBTEXT, bg=CARD).grid(row=1, column=0, sticky="w")
        self.lbl_hamming_out = tk.Label(info_frame, text="—", font=FONT_MONO, fg=YELLOW, bg=CARD, wraplength=500, justify="left")
        self.lbl_hamming_out.grid(row=1, column=1, sticky="w", padx=10)

    def _build_memory_panel(self, parent):
        card = self._card(parent, "🗄  BELLEK TABLOSU")
        card.pack(fill=tk.X, pady=(0, 10))

        cols = ("addr", "data_bits", "hamming", "width")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=5)
        heads = {"addr": ("Adres", 70), "data_bits": ("Giriş Verisi", 150),
                 "hamming": ("Bellekteki Hamming Kodu", 360), "width": ("Genişlik", 80)}
        for c, (h, w) in heads.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL, font=FONT_SMALL, rowheight=24)
        style.configure("Treeview.Heading", background=BORDER, foreground=ACCENT, font=FONT_SMALL)
        style.map("Treeview", background=[("selected", ACCENT2)])

        sb = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=6)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=6, padx=(0, 8))
        self.tree.bind("<<TreeviewSelect>>", self._on_mem_select)

    def _build_bit_grid(self, parent):
        card = self._card(parent, "🔢  BİT IZGARASI (Seçili Bellek Satırı Görseli)")
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.bit_grid_frame = tk.Frame(card, bg=CARD)
        self.bit_grid_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        
        self.grid_placeholder = tk.Label(self.bit_grid_frame, text="İncelemek ve yapay hata enjekte etmek için bellekten bir satır seçin.",
                                         font=FONT_SMALL, fg=SUBTEXT, bg=CARD)
        self.grid_placeholder.pack(pady=20)

    def _build_error_panel(self, parent):
        card = self._card(parent, "⚡  HATA ENJEKSİYONU & DÜZELTME DÜZENEĞİ")
        card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(card, text="Hata Enjekte Edilecek Pozisyon (1'den Başlar):", font=FONT_SMALL, fg=SUBTEXT, bg=CARD).pack(anchor="w", padx=12, pady=(4, 2))

        pos_row = tk.Frame(card, bg=CARD)
        pos_row.pack(fill=tk.X, padx=12, pady=4)
        self.error_pos_var = tk.StringVar()
        self.entry_errpos = tk.Entry(pos_row, textvariable=self.error_pos_var, font=FONT_MONO, bg=PANEL, fg=RED_C,
                                     insertbackground=RED_C, bd=0, relief=tk.FLAT, width=8)
        self.entry_errpos.pack(side=tk.LEFT, ipady=4, padx=(0, 10))

        tk.Button(pos_row, text="⚡ Hata Oluştur", font=FONT_SMALL, bg=RED_C, fg="white", bd=0, padx=8, pady=4, cursor="hand2", command=self._inject_error).pack(side=tk.LEFT, padx=2)
        tk.Button(pos_row, text="🔧 Doğrula & Oku", font=FONT_SMALL, bg=GREEN, fg="#0f1117", bd=0, padx=8, pady=4, cursor="hand2", command=self._correct_and_read).pack(side=tk.LEFT, padx=2)
        tk.Button(pos_row, text="🔄 Reset", font=FONT_SMALL, bg=SUBTEXT, fg="white", bd=0, padx=8, pady=4, cursor="hand2", command=self._reset_selected).pack(side=tk.LEFT, padx=2)

        res_grid = tk.Frame(card, bg=CARD)
        res_grid.pack(fill=tk.X, padx=12, pady=10)
        
        lbl_defs = [
            ("Hesaplanan Sendrom :", "lbl_syndrome"),
            ("Teyit Edilen Hata  :", "lbl_errbit"),
            ("Düzeltilen Kod     :", "lbl_corrected"),
            ("Kanal Çıktı Verisi  :", "lbl_dataout"),
        ]
        for i, (txt, attr) in enumerate(lbl_defs):
            tk.Label(res_grid, text=txt, font=FONT_MONO, fg=SUBTEXT, bg=CARD, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            lbl = tk.Label(res_grid, text="—", font=FONT_MONO, fg=YELLOW, bg=CARD, anchor="w", wraplength=250)
            lbl.grid(row=i, column=1, sticky="w", padx=10)
            setattr(self, attr, lbl)

        self.lbl_status = tk.Label(card, text="", font=FONT_HEAD, bg=CARD, pady=4)
        self.lbl_status.pack(fill=tk.X, padx=12, pady=4)

    def _build_log_panel(self, parent):
        card = self._card(parent, "📋  SİMÜLASYON LOGLARI")
        card.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(card, font=FONT_SMALL, bg=PANEL, fg=TEXT, bd=0, relief=tk.FLAT, state=tk.DISABLED, wrap=tk.WORD)
        sb = ttk.Scrollbar(card, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=6)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=6, padx=(0, 8))

        self.log_text.tag_configure("ok", foreground=GREEN)
        self.log_text.tag_configure("err", foreground=RED_C)
        self.log_text.tag_configure("info", foreground=ACCENT)
        self.log_text.tag_configure("warn", foreground=YELLOW)

    def _card(self, parent, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg=BORDER, bd=1, relief=tk.FLAT)
        outer.pack(fill=tk.X, pady=2)
        tk.Label(outer, text=title, font=FONT_SMALL, fg=ACCENT, bg=BORDER, anchor="w").pack(fill=tk.X, padx=8, pady=3)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
        return inner

    # ─────────────────────────────────────────────
    #  Arayüz Mantığı ve Olay Yöneticileri
    # ─────────────────────────────────────────────

    def _on_width_change(self):
        self.data_input.set("")
        self.lbl_bitcount.config(text="")
        self.lbl_parity_count.config(text="—")
        self.lbl_hamming_out.config(text="—")
        self._clear_error_display()

    def _validate_input(self, event=None):
        val = self.data_input.get()
        width = self.data_width.get()
        clean = ''.join(c for c in val if c in '01')
        if clean != val:
            self.data_input.set(clean)
        n = len(clean)
        color = GREEN if n == width else (YELLOW if n < width else RED_C)
        self.lbl_bitcount.config(text=f"{n}/{width} bit  {'✓ Uygun' if n == width else '— Eksik' if n < width else '— Limit dışı'}", fg=color)

    def _random_fill(self):
        w = self.data_width.get()
        self.data_input.set(''.join(random.choice('01') for _ in range(w)))
        self._validate_input()

    def _encode_and_write(self):
        data = self.data_input.get().strip()
        width = self.data_width.get()
        if len(data) != width or not all(c in '01' for c in data):
            messagebox.showerror("Hata", f"Lütfen tam olarak {width} bit genişliğinde binary veri giriniz.")
            return

        hamming, p_pos, _ = encode_hamming(data)
        r = len(p_pos)

        self.lbl_parity_count.config(text=f"{r} Bit (Pozisyonlar: {', '.join(str(p) for p in p_pos)})")
        self.lbl_hamming_out.config(text=hamming)

        addr = self.mem_addr
        self.memory[addr] = {
            "hamming": hamming,
            "original": hamming,
            "data": data,
            "width": width,
            "r": r,
            "p_pos": p_pos,
        }
        self.mem_addr += 1

        self.tree.insert("", tk.END, iid=str(addr), values=(f"0x{addr:03X}", data, hamming, f"{width} bit"))
        self._log(f"[BELLEK YAZMA] Adres 0x{addr:03X} -> Hamming Kodu Başarıyla Üretildi: {hamming}", "ok")
        
        # Seçimi otomatik yap ve tetikle
        self.tree.selection_set(str(addr))
        self._on_mem_select()

    def _on_mem_select(self, event=None):
        sel = self.tree.selection()
        if not sel: return
        addr = int(sel[0])
        row = self.memory.get(addr)
        if row:
            if hasattr(self, 'grid_placeholder'):
                self.grid_placeholder.destroy()
            self._draw_bit_grid(row["hamming"], row["p_pos"])
            self._clear_error_display()

    def _inject_error(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Hata enjekte etmek için önce tablodan bellek hücresi seçin.")
            return
        addr = int(sel[0])
        row = self.memory[addr]
        pos_str = self.error_pos_var.get().strip()
        
        if not pos_str.isdigit():
            messagebox.showerror("Hata", "Lütfen nümerik bir bit pozisyon değeri girin.")
            return
            
        pos = int(pos_str)
        n = len(row["hamming"])
        if pos < 1 or pos > n:
            messagebox.showerror("Hata", f"Girilen pozisyon Hamming dizisi sınırları dışında (1 ile {n} arasında olmalı).")
            return

        # Yapay Hata Oluşturma (Bit Evirme)
        h = list(row["hamming"])
        h[pos - 1] = '1' if h[pos - 1] == '0' else '0'
        row["hamming"] = ''.join(h)

        self.tree.item(str(addr), values=(f"0x{addr:03X}", row["data"], row["hamming"], f"{row['width']} bit"))
        self._draw_bit_grid(row["hamming"], row["p_pos"], error_pos=pos)

        self._log(f"[YAPAY HATA] Adres 0x{addr:03X} -> {pos}. bit üzerinde manipülasyon yapıldı.", "err")
        self.lbl_status.config(text=f"⚡ Bit {pos} üzerinde yapay hata oluşturuldu!", fg=RED_C, bg=ERR_BG)

    def _correct_and_read(self):
        sel = self.tree.selection()
        if not sel: return
        addr = int(sel[0])
        row = self.memory[addr]
        
        # Karşılaştırma Ünitesi ve Sendrom Kelimesi Analizi
        syndrome, corrected = detect_correct(row["hamming"], row["r"])
        r = row["r"]
        p_pos = row["p_pos"]

        syn_bin = format(syndrome, f'0{r}b')
        self.lbl_syndrome.config(text=f"{syndrome} (Binary Sendrom: {syn_bin})", fg=YELLOW)

        if syndrome == 0:
            self.lbl_errbit.config(text="Hata Algılanmadı", fg=GREEN)
            self.lbl_corrected.config(text=row["hamming"], fg=GREEN)
            self.lbl_status.config(text="✅ Veri bloğu tamamen güvenli ve hatasız!", fg=GREEN, bg=DATA_BG)
            self._log(f"[OKUMA] Adres 0x{addr:03X} -> Sendrom 0. Herhangi bir veri bozulması saptanmadı.", "ok")
        else:
            bit_type = "Parity kontrol biti" if syndrome in p_pos else "Data veri basamağı"
            self.lbl_errbit.config(text=f"Pozisyon: {syndrome} ({bit_type})", fg=RED_C)
            self.lbl_corrected.config(text=corrected, fg=GREEN)
            self.lbl_status.config(text=f"🔧 Sendrom yorumlandı! Pozisyon {syndrome} düzeltildi.", fg=YELLOW, bg=PARITY_BG)
            self._log(f"[DÜZELTME] Adres 0x{addr:03X} -> Sendrom: {syndrome} tespitiyle bozulan bit otomatik onarıldı.", "warn")

        data_out = extract_data(corrected, r)
        self.lbl_dataout.config(text=f"{data_out} (Hex: 0x{int(data_out, 2):X})", fg=ACCENT)

        # Bellek kaydını düzeltilmiş haliyle güncelle
        row["hamming"] = corrected
        self.tree.item(str(addr), values=(f"0x{addr:03X}", row["data"], corrected, f"{row['width']} bit"))
        self._draw_bit_grid(corrected, p_pos, error_pos=syndrome if syndrome else None, corrected=True)

    def _reset_selected(self):
        sel = self.tree.selection()
        if not sel: return
        addr = int(sel[0])
        row = self.memory[addr]
        row["hamming"] = row["original"]
        self.tree.item(str(addr), values=(f"0x{addr:03X}", row["data"], row["original"], f"{row['width']} bit"))
        self._draw_bit_grid(row["original"], row["p_pos"])
        self._clear_error_display()
        self._log(f"[RESET] Adres 0x{addr:03X} başlangıç haline getirildi.", "info")

    def _draw_bit_grid(self, hamming: str, p_pos: list, error_pos: int = None, corrected: bool = False):
        for w in self.bit_grid_frame.winfo_children():
            w.destroy()

        n = len(hamming)
        cols = 12 if n <= 12 else (16 if n <= 24 else 20)

        # Renk Bilgilendirme Skalası
        legend = tk.Frame(self.bit_grid_frame, bg=CARD)
        legend.pack(anchor="w", pady=(0, 8))
        for bg, label in [(PARITY_BG, "Parity (P)"), (DATA_BG, "Veri (D)"), (ERR_BG, "Hatalı Bit"), (GREEN, "Düzeltildi")]:
            f = tk.Frame(legend, bg=bg, width=12, height=12)
            f.pack(side=tk.LEFT, padx=(6, 2))
            tk.Label(legend, text=label, font=FONT_SMALL, fg=TEXT, bg=CARD).pack(side=tk.LEFT, padx=(0, 10))

        grid = tk.Frame(self.bit_grid_frame, bg=CARD)
        grid.pack(anchor="w", fill=tk.BOTH, expand=True)

        for i in range(1, n + 1):
            bit = hamming[i - 1]
            is_parity = i in p_pos
            is_error   = (i == error_pos)
            is_corr    = (is_error and corrected)

            if is_corr:
                bg_c = GREEN; fg_c = "#0f1117"
            elif is_error:
                bg_c = ERR_BG; fg_c = RED_C
            elif is_parity:
                bg_c = PARITY_BG; fg_c = ACCENT
            else:
                bg_c = DATA_BG; fg_c = TEXT

            cell = tk.Frame(grid, bg=bg_c, bd=1, relief=tk.RIDGE, width=48, height=48)
            cell.grid_propagate(False)
            row_i  = (i - 1) // cols
            col_i  = (i - 1) %  cols
            cell.grid(row=row_i, column=col_i, padx=2, pady=2)

            # Hücre içi etiketler
            tk.Label(cell, text=bit, font=("Courier New", 14, "bold"), fg=fg_c, bg=bg_c).place(relx=0.5, rely=0.35, anchor="center")
            tag = f"P{i}" if is_parity else f"D{i}"
            tk.Label(cell, text=tag, font=("Courier New", 7), fg=SUBTEXT, bg=bg_c).place(relx=0.5, rely=0.78, anchor="center")

    def _clear_error_display(self):
        for attr in ("lbl_syndrome", "lbl_errbit", "lbl_corrected", "lbl_dataout"):
            getattr(self, attr).config(text="—", fg=YELLOW)
        self.lbl_status.config(text="", bg=CARD)

    def _log(self, msg: str, tag: str = "info"):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)


# ─────────────────────────────────────────────
#  Uygulama Giriş Noktası
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = HammingSimulator()
    app.mainloop()