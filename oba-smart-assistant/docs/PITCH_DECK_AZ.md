# OBASA — Pitch Deck Məzmunu (Azərbaycan dilində)
### AI ilə Gücləndirilmiş Pərakəndə Ticarət Platforması

---

## SLAYDLİST

1. Başlıq Slaydı
2. Problem
3. Həll
4. Məhsul Demosu
5. Texnologiya
6. Unikal Üstünlüklər
7. Bazar Həcmi
8. İş Modeli
9. Rəqabət Analizi
10. Yol Xəritəsi
11. Komanda
12. Maliyyə Proqnozu
13. İnvestisiya Tələbi
14. Çağırış

---

## SLAYD 1 — BAŞLIQ

**OBASA**
*OBA Smart Assistant*

> **"Azərbaycanın ilk süni intellekt əsaslı mobil alış-veriş köməkçisi"**

- Platforma: Flutter (Android & iOS)
- Backend: FastAPI + Supabase
- AI: Google Gemini 2.5 Flash
- Versiya: 1.0.0 | 2025

---

## SLAYD 2 — PROBLEM

### Azərbaycan Pərakəndə Bazarında Mövcud Problemlər

**Alıcı tərəfindən:**
- Böyük marketlərdə düzgün məhsulu tapmaq çox vaxt alır
- Azərbaycan dilində keyfiyyətli alış-veriş köməkçisi mövcud deyil
- Şəxsiləşdirilmiş tövsiyə xidməti yoxdur
- Mobil ticarət interfeysləri istifadəçi dostu deyil
- Yaxın məhəllə sakinləriylə sərfəli qiymətə bölüşmə imkanı yoxdur

**Biznes tərəfindən:**
- Müştəri davranışını anlamaq üçün data analitikası çatışmır
- Şikayət idarəetməsi manual və yavaşdır
- Stok proqnozlaşdırması düzgün aparılmır, artıq stok yığılır
- Müştəri loyallığı proqramları köhnəlmiş formatlardadır

**Rəqəm:**
> Azərbaycanda e-ticarətin ümumi pərakəndə satışa nisbəti cəmi **~4%** — Avropa ortalaması isə **~25%**. Bu, nəhəng bir boşluqdur.

---

## SLAYD 3 — HƏLLİMİZ

### OBASA: Ağıllı Alış-veriş, Azərbaycan üçün

OBASA, Azərbaycan dilini tam dəstəkləyən, süni intellekt ilə gücləndirilmiş bir mobil pərakəndə ticarət platformasıdır. Sadəcə bir tətbiq deyil — **alış-veriş köməkçisi, resept müşaviri, qonşu bölüşmə şəbəkəsi** və **biznes analitika mərkəzi** birlikdə.

| Problem | OBASA Həlli |
|--------|------------|
| Azərbaycan dilində köməkçi yoxdur | Tam Azərbaycan dilli Gemini AI söhbət botu |
| Məhsul tapmaq çətindir | Semantik axtarış + səsli əmrlər |
| Şəxsiləşdirilmiş tövsiyə yoxdur | SVD əsaslı kollaborativ filtrasiya |
| Stok israfı | Prophet əsaslı tələb proqnozu |
| Müştəri şikayəti idarəsizliyi | AI ilə avtomatik şikayət kateqoriyalaşdırması |
| Loyallıq proqramı köhnəlmiş | Oyunlaşdırma: Tunc/Gümüş/Qızıl/Platin |

---

## SLAYD 4 — MƏHSUL DEMOSU

### Ekranlar və Funksionallıq

#### 🏠 Ana Ekran
- Kateqoriyalara görə məhsul kataloqu
- "Sizin üçün tövsiyə edilən" bölməsi (AI əsaslı)
- Canlı kampaniyalar və endirimlər
- Aşağı naviqasiya: Ev | Məhsullar | AI Köməkçi | Səbət | Profil
- Apple-stilli "Liquid Glass" dizayn dili

#### 🤖 AI Alış-veriş Köməkçisi (Səsli / Yazılı Chat)
- Google Gemini 2.5 Flash ilə işləyir
- **Azərbaycan dilində tam danışıq imkanı**
- Məhsul əlavə etmə: *"2 kq pomidor, 1 ədəd çörək al"*
- Resept məşvərəti: *"Küftə üçün nə lazımdır?"* → Avtomatik səbətə əlavə
- Müqayisə: *"Hansı süd daha sərfəlidir?"*
- Səs mesajı göndərmək və almaq dəstəyi
- Söhbət tarixi saxlanılır

#### 🎤 Səsli Axtarış
- Google Speech-to-Text API ilə real vaxt transkripsiya
- Azərbaycan dilini tanıyır
- Semantik axtarış: *"Yemək üçün bir şey"* → kontekstə uyğun nəticə
- text-embedding-004 modeli ilə vektor bazlı axtarış

#### 📦 Məhsul Kataloqu
- Kateqoriya filtrasiyası, sıralama
- Barkod skanerləmə dəstəyi
- Şəkil yükləmə + AI görüntü tanıma (hazırlanır)
- Detallar: qiymət, stok vəziyyəti, rəylər, reytinq

#### 🛒 Ağıllı Səbət
- Pulsuz çatdırılma həddinə nə qədər qaldığı göstərilir (50 AZN)
- Standart çatdırılma: 2 AZN | Express: 5 AZN | Mağazadan götür: Pulsuz
- Ümumi qənaət hesablanır
- Promosiya kodu dəstəyi

#### 🗺️ Checkout & Xəritə
- Google Maps inteqrasiyası — ən yaxın filialları göstərir
- Çatdırılma ünvanını xəritədən seçmək
- 3 addımlı checkout: Çatdırılma → Ödəniş → Təsdiq
- Ödəniş: Nağd, kart, kapital pay (simulyasiya)

#### 🎁 Qonşu Sürprizi (Unikal Funksiya!)
- Bluetooth LE ilə yaxında olan digər OBASA istifadəçilərini tapır
- Real vaxt eşləşmə (Supabase Realtime vasitəsilə)
- Eşləşmə baş verir → konfetti animasiyası + hər ikisi üçün sürpriz endirim
- Oyunlaşdırma elementləri: pulsasiya, silkələmə, hədiyyə qutu açılması

#### 🏆 Profil & Loyallıq
- Xal sistemi: hər 1 AZN = 1 xal
- Rəy yazmaq: +10 xal | İlk sifariş: +50 xal
- Tunc → Gümüş → Qızıl → Platin səviyyələri
- Nailiyyət nişanları (badges)
- Sifariş tarixçəsi

---

## SLAYD 5 — TEXNOLOGİYA

### Texniki Arxitektura

```
Mobil Tətbiq (Flutter 3.x — Android & iOS)
        │
        ├── Google Gemini 2.5 Flash (AI söhbət)
        ├── text-embedding-004 (Semantik axtarış)
        ├── Google Speech-to-Text (Səs tanıma)
        ├── Google Maps Flutter (Xəritə)
        ├── Flutter Blue Plus (Bluetooth LE)
        │
        └── Supabase (Backend-as-a-Service)
              ├── PostgreSQL (verilənlər bazası)
              ├── Realtime (canlı yeniləmələr)
              ├── Auth (autentifikasiya)
              └── Storage (fayllar)
```

**Əlavə Backend (FastAPI):**
- SVD əsaslı tövsiyə mühərriki
- Prophet əsaslı tələb proqnozu
- NLP ilə şikayət kateqoriyalaşdırması
- Hiss analizi (Sentiment Analysis)
- Streamlit analitika paneli

**Texnologiya Yığını:**

| Qat | Texnologiya |
|-----|-------------|
| Mobil | Flutter, Dart |
| AI/ML | Google Gemini, text-embedding-004 |
| Backend | FastAPI (Python 3.11) |
| Verilənlər Bazası | Supabase (PostgreSQL) |
| Cache | Redis |
| Konteyner | Docker + Docker Compose |
| Xəritə | Google Maps |
| Səs | Google Speech-to-Text, flutter_tts |
| BLE | Flutter Blue Plus |

---

## SLAYD 6 — UNİKAL ÜSTÜNLÜKLƏR

### Niyə OBASA? — 7 Rəqabət Üstünlüyü

**1. 🇦🇿 Azərbaycan Dilini Tam Anlayan İlk Platforma**
Gemini AI-nin Azərbaycan dilini dəstəkləməsi ilə istifadəçi öz dilində danışır, AI başa düşür. Heç bir yerli rəqib bu səviyyədə dil dəstəyi təklif etmir.

**2. 🎤 Səsli Alış-veriş**
"2 kq alma, bir litr süd al" — söyləyin, tamamdır. Yazmağa ehtiyac yoxdur. Azərbaycan dilini tanıyan ilk pərakəndə səs köməkçisi.

**3. 🍳 Resept → Səbət Avtomatizasiyası**
"Plovun resepti nədir?" deyirsiniz — AI resepti izah edir VƏ lazımi materialları birbaşa səbətinizə əlavə edir. Dünyada az sayda platforma bu funksiyaya sahibdir.

**4. 📡 Bluetooth "Qonşu Sürprizi"**
BLE texnologiyası ilə eyni məhəllədə alış-veriş edən müştərilər eşləşdirilir, hər ikisi endirim qazanır. Bu, **sosial ticarəti** yeni səviyyəyə çıxarır.

**5. 🤝 Silkəmə (Shake-to-Discover)**
Telefonu silkəyin → yaxınlıqdakı müştərini tapın. Qeyri-adi UX — viral yayılma potensialı yüksəkdir.

**6. 📊 Real Vaxt Biznes Analitikası**
Streamlit paneli ilə stok vəziyyəti, satış proqnozu, şikayət analizi — hamısı bir yerdə.

**7. 🏆 Dərin Oyunlaşdırma**
Sadə xal sistemi deyil: səviyyələr, nişanlar, "ilk sifariş" bonusları — müştərini uzunmüddətli saxlamağın ən effektiv yolu.

---

## SLAYD 7 — BAZAR HƏCMİ

### Azərbaycan Bazarı

| Göstərici | Rəqəm |
|-----------|-------|
| Azərbaycan əhalisi | ~10 milyon |
| İnternet istifadəçiləri | ~8.2 milyon (82%) |
| Smartfon penetrasiyası | ~75% |
| E-ticarət bazarı (2024) | ~$1.2 milyard |
| Pərakəndə sektorun ÜDM-ə payı | ~15% |
| E-ticaretin pərakəndəyə nisbəti | ~4% (böyümə potensialı: 6x) |

**TAM BAZAR HƏCMİ (TAM):** $1.2 milyard

**XİDMƏT GÖSTƏRƏ BİLƏCƏYİMİZ BAZAR (SAM):**
Bakı + böyük şəhərlər, smartfon istifadəçiləri: ~$400 milyon

**HƏDƏF BAZAR (SOM — 3 il):**
Bazar payının 2–3% -i: **~$8–12 milyon**

**Regional İmkan:**
Gürcüstan, Özbəkistan, Türkiyə bazarlarına eyni platforma ilə genişlənmə imkanı mövcuddur (dil dəstəyi əlavə etmək kifayətdir).

---

## SLAYD 8 — İŞ MODELİ

### Gəlir Axınları

**1. Komissiya Modeli (əsas gəlir)**
- Hər satışdan 8–15% komissiya
- Proqnoz: 10.000 sifariş/ay × ortalama 25 AZN × 10% = **25.000 AZN/ay**

**2. Premium Abunəlik (B2C)**
- "OBASA Pro": Pulsuz çatdırılma + əlavə xallar + eksklüziv endirimlər
- Aylıq: 4.99 AZN | İllik: 39.99 AZN
- 5.000 abunəçi hədəfi → **~25.000 AZN/ay**

**3. Mağaza Yerləşdirmə (B2B)**
- Marketlər öz məhsullarını platformada öncül yerə qoymaq üçün ödəyir
- Aylıq sabit ücret: 500–2000 AZN/mağaza
- 50 mağaza × 1000 AZN = **50.000 AZN/ay**

**4. Analitika Paketi (B2B)**
- Sahibkarlar üçün satış analizi, müştəri davranışı hesabatları
- Aylıq abunəlik: 200–800 AZN

**5. Reklam & Sponsorluq**
- Tətbiq daxilində hədəflənmiş banner reklamlar
- Kateqoriya sponsorluğu

**Cəmi Aylıq Gəlir Proqnozu (1 il sonra):** ~100.000–150.000 AZN/ay

---

## SLAYD 9 — RƏQABƏTLİ ANALİZ

### Rəqabət Mövqeyi

| Xüsusiyyət | OBASA | Bolt Food | Bringo | Wolt | Yerli tətbiqlər |
|------------|-------|-----------|--------|------|-----------------|
| Azərbaycan dili AI | ✅ | ❌ | ❌ | ❌ | ❌ |
| Səsli alış-veriş | ✅ | ❌ | ❌ | ❌ | ❌ |
| Resept → Səbət | ✅ | ❌ | ❌ | ❌ | ❌ |
| Qonşu eşləşmə (BLE) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Şəxsiləşdirilmiş tövsiyə | ✅ | Zəif | ❌ | Zəif | ❌ |
| Oyunlaşdırma | ✅ | ❌ | ❌ | ❌ | ❌ |
| B2B analitika | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pərakəndə + Çatdırılma | ✅ | Yalnız yemək | ✅ | Yalnız yemək | ❌ |

**Nəticə:** OBASA, Azərbaycan bazarında birbaşa rəqibi olmayan, AI-first, dil doğru bir platforma kimi mövqelənir.

---

## SLAYD 10 — YOL XƏRİTƏSİ

### İnkişaf Planı

```
2025 Q1–Q2  ████████████  MVP: Flutter tətbiqi, AI köməkçi, Supabase backend
2025 Q3     ████████      Beta Test: Bakı-da 100 istifadəçi ilə pilot
2025 Q4     ████████      Launch: App Store & Google Play
2026 Q1     ██████        Genişlənmə: 10 pərakəndəçi ilə ortaqlıq
2026 Q2     ██████        B2B analitika paketi
2026 Q3     ████          Gəncə, Sumqayıt bazarları
2026 Q4     ████          Gürcüstan pilot
2027        ██            Türkiyə & Orta Asiya
```

**Qısamüddətli Hədəflər (6 ay):**
- [ ] 5.000 aktiv istifadəçi
- [ ] 10+ mağaza inteqrasiyası
- [ ] Apple App Store & Google Play dərc
- [ ] Firebase Push Notification aktiv edilməsi
- [ ] Barkod skanerləmə tam işlək

**Ortamüddətli (12–18 ay):**
- [ ] 50.000 aktiv istifadəçi
- [ ] 100+ mağaza
- [ ] AR üzərindən məhsul baxışı
- [ ] Loyal müştərilər üçün virtual kart

---

## SLAYD 11 — KOMANDA

*(Buraya öz komanda məlumatlarını əlavə edin)*

**Tövsiyə olunan struktur:**

| Rol | Məsuliyyət |
|-----|-----------|
| CEO / Founder | Strateji istiqamət, investorlarla əlaqə |
| CTO | Flutter & AI arxitekturası |
| ML Engineer | Gemini inteqrasiyası, tövsiyə mühərrikləri |
| Product Designer | UX/UI, Apple Design System |
| Business Development | B2B müqavilələr, mağaza ortaqlıqları |
| Marketing | Sosial media, ASO, istifadəçi qazanılması |

**Texniki Üstünlük:**
- Gemini 2.5 Flash API inteqrasiyası tamamdır
- Supabase Realtime BLE ilə birləşdirilib
- Google Maps + GPS çatdırılma sistemi hazırdır
- Tam işlək MVP emülyatorda test edilib

---

## SLAYD 12 — MALİYYƏ PROQNOZU

### 3 İllik Proqnoz (AZN)

| Göstərici | İl 1 | İl 2 | İl 3 |
|-----------|------|------|------|
| Aktiv İstifadəçi | 5.000 | 40.000 | 150.000 |
| Aylıq Sifariş | 2.000 | 20.000 | 90.000 |
| Komissiya Gəliri | 60.000 | 600.000 | 2.700.000 |
| Abunəlik Gəliri | 24.000 | 240.000 | 900.000 |
| B2B Analitika | 12.000 | 120.000 | 480.000 |
| **Cəmi Gəlir** | **96.000** | **960.000** | **4.080.000** |
| Əməliyyat Xərcləri | 180.000 | 480.000 | 1.200.000 |
| **Xalis Mənfəət** | **-84.000** | **+480.000** | **+2.880.000** |

**Break-even nöqtəsi:** ~18. ay

---

## SLAYD 13 — İNVESTİSİYA TƏLƏBİ

### Seed Round: $150.000 – $250.000

**Pul Haraya Getir:**

| Bölmə | Məbləğ | % |
|-------|--------|---|
| Texniki inkişaf (backend, ML) | $60.000 | 28% |
| Marketinq & istifadəçi qazanılması | $50.000 | 24% |
| Mağaza inteqrasiyaları & B2B satış | $40.000 | 19% |
| Komanda genişləndirilməsi | $50.000 | 24% |
| Ehtiyat fondu | $15.000 | 7% |
| **Cəmi** | **$215.000** | **100%** |

**İnvestora Təklif:**
- Equity: 15–20%
- Qiymətləndirmə: $750.000 – $1.000.000 (pre-money)
- Geri qaytarma dövrü: 24–30 ay
- Exit strategiyası: Regional e-ticarət şirkətinə satış və ya Seriya-A (2027)

---

## SLAYD 14 — ÇAĞIRIŞ

### Birlikdə Azərbaycanın Rəqəmsal Ticarətini Dəyişdirək

**OBASA nə deyildir:**
❌ Sadə onlayn mağaza deyil
❌ Adi çatdırılma tətbiqi deyil
❌ Köhnə loyallıq kartı deyil

**OBASA nədir:**
✅ Azərbaycan dilini anlayan AI alış-veriş köməkçisi
✅ Sosial ticarəti BLE ilə yenidən kəşf edən platforma
✅ Resept biliyindən stok prognozuna qədər tam ekosistem
✅ Hər kəsin öz dilində danışdığı ağıllı mağaza

---

> **"Dünyada ən yaxşı texnologiyaları götürüb Azərbaycan üçün yenidən qurdq — OBASA belədir."**

---

### Əlaqə

- **Tətbiq Adı:** OBASA (OBA Smart Assistant)
- **Texnologiya:** Flutter + Gemini 2.5 Flash + Supabase
- **Hazır Status:** MVP hazır, emülyatorda test edilib
- **Növbəti Addım:** Pilot istifadəçi testi + App Store dərci

---

*Bu sənəd OBASA layihəsinin pitch deck üçün hazırlanmış Azərbaycan dilli məzmunudur.*
*Bütün maliyyə rəqəmləri proqnoz xarakteri daşıyır.*
