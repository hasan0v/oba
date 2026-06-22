# OBASA — Tam Yaxşılaşdırma Yol Xəritəsi

> Sənior arxitektura analizi və faza-əsaslı icra planı
> **Tarix:** 2026-04-26 | **Versiya:** 1.0

---

## 📊 İcra Xülasəsi (Executive Dashboard)

| Kateqoriya | Sayı | Status |
|------------|------|--------|
| 🔴 Kritik təhlükəsizlik problemi | 9 | URGENT |
| 🔴 Kritik bug / crash | 9 | URGENT |
| 🟠 Kod keyfiyyəti problemi | 10 | HIGH |
| 🟠 Performans problemi | 7 | HIGH |
| 🟠 Arxitektura problemi | 7 | HIGH |
| 🟡 Asılılıq (paket) problemi | 9 | MEDIUM |
| 🟡 UX/Flow problemi | 8 | MEDIUM |
| 🟢 Yeni funksiya təklifi | 24 | OPPORTUNITY |
| **CƏMİ** | **83** | |

**Tam yol xəritəsinin tamamlanma müddəti:** ~10–14 həftə (1 senior dev FTE)

---

## 📋 PHASE 1 — Dərin Analiz Nəticələri

### 1.1 🔴 KRİTİK TƏHLÜKƏSİZLİK PROBLEMLƏRİ

| # | Problem | Yer | Sətir | Təsir | Həll |
|---|---------|-----|-------|-------|------|
| S1 | Hardcoded **Gemini API açarı** | `lib/config/app_config.dart` | 15-16 | Açar APK-dan çıxarılıb istifadə edilə bilər → faktura zərəri | `String.fromEnvironment` + `.env` |
| S2 | Hardcoded **Supabase Anon Key** (JWT) | `lib/config/app_config.dart` | 12 | Layihə ID açıq, RLS yoxdursa data oğurlana bilər | `--dart-define` ilə inject |
| S3 | Hardcoded **Google Maps API Key** | `android/app/src/main/AndroidManifest.xml` | 46 | APK-dan oxunan açar, faktura zərəri | Cloud Console-da paket adı + SHA-1 məhdudiyyəti |
| S4 | FCM token plain SharedPreferences | `lib/services/auth_service.dart` | 80 | Cihaz hijack → push spam | `flutter_secure_storage` |
| S5 | User token şifrələnməmiş SQLite | `lib/services/local_database_service.dart` | full | Root cihazda data oxuna bilər | Şifrələmə və ya secure storage |
| S6 | Search query input validation yox | `supabase_database_service.dart` | 159 | Edge case crash, RPC abuse | Min/max uzunluq + sanitization |
| S7 | Token TTL yoxlanmadan istifadə | `lib/services/api_service.dart` | 23 | Expired token gözlənilməz xəta | İstifadədən əvvəl `exp` claim yoxla |
| S8 | SSL pinning yox | `lib/services/api_service.dart` | full | MITM hücumu mümkündür | `dio_certificate_pinning` |
| S9 | Auth listener-də xəta tutulmur | `lib/providers/auth_provider.dart` | 36-49 | Unhandled exception → app crash | `.onError()` handler əlavə et |

### 1.2 🔴 KRİTİK BUG-LAR / CRASH-LAR

| # | Problem | Yer | Sətir | Həll |
|---|---------|-----|-------|------|
| B1 | `_database!` force unwrap NPE | `local_database_service.dart` | 16, 18 | `??` istifadə + try-catch |
| B2 | `widget.product.primaryImage!` NPE | `widgets/apple_product_card.dart` | 111, 118 | Placeholder fallback |
| B3 | `message!.metadata!` cüt force unwrap | `voice_shopping_screen.dart` | 663 | Null-safe access |
| B4 | `setState()` mounted check yox | `voice_shopping_screen.dart` | 310, 330 | `if (mounted) setState(...)` |
| B5 | initState içindəki async setState | `checkout_screen.dart` | 32-43 | `if (mounted)` qoruması |
| B6 | `VideoPlayerController` dispose yox | `splash_screen.dart` | 27 | `dispose()` override |
| B7 | `.single()` 0/>1 row-da crash | `supabase_database_service.dart` | 359 | `.maybeSingle()` |
| B8 | Auth listener heç bir error handler | `auth_provider.dart` | 36 | Try-catch wrapper |
| B9 | Animation controller dispose audit | `login_screen.dart` | 25 | Explicit dispose |

### 1.3 🟠 KOD KEYFİYYƏTİ

| # | Problem | Yer | Həll |
|---|---------|-----|------|
| Q1 | 100+ `print()` / `debugPrint()` | `ai_service.dart`, hər yerdə | `AppLogger` utility (release-də sönük) |
| Q2 | God class: `AIService` (600+ sətir) | `services/ai_service.dart` | TtsService + TranscriptionService-ə böl |
| Q3 | God class: `ChatMessage` (11 sahə) | `voice_shopping_screen.dart` | Dataclass + freezed |
| Q4 | İki AI servisi üst-üstə düşür | `conversational_ai_service.dart` vs `shopping_assistant_service.dart` | Birinə birləşdir |
| Q5 | Lokalizasiya yoxdur | bütün AZ strings hardcode | `intl` + `strings_az.json` |
| Q6 | Magic numbers (`0.3`, `0.25` threshold) | `conversational_ai_service.dart` | 196 | `AppConfig`-ə daşı |
| Q7 | Provider içində `notifyListeners()` çağırışları sıralanmayıb | `cart_provider.dart` | Batch updates |
| Q8 | Direct DB call provider-dən | `cart_provider.dart` | 10 | Repository pattern |
| Q9 | Hardcoded saxlanan UI strings | `login_screen.dart` | 74 | Localization |
| Q10 | Empty state UI yox | `chat_history_screen.dart` | Empty state widget |

### 1.4 🟠 PERFORMANS

| # | Problem | Yer | Həll |
|---|---------|-----|------|
| P1 | Pagination yox (`getAllProducts`) | `product_provider.dart` | 119 | Offset pagination + lazy load |
| P2 | N+1 queries chat sessions | `supabase_database_service.dart` | 373-383 | Single RPC + JOIN |
| P3 | Embedding cache LRU səhv | `semantic_search_service.dart` | 43 | `lru_cache` paketi |
| P4 | Image cache limit yoxdur | `apple_product_card.dart` | 111 | `cache_manager` config |
| P5 | Search debounce yox | `product_provider.dart` | full | 500ms `Timer` |
| P6 | `const` istifadə natamam | hər yerdə | Linter rule + audit |
| P7 | Heavy DB ops main thread-də | `local_database_service.dart` | full | `compute()` isolate |

### 1.5 🟠 ARXİTEKTURA

| # | Problem | Həll |
|---|---------|------|
| A1 | Repository layer yoxdur | `repository/product_repository.dart` və s. yarat |
| A2 | İki DB service eyni interfeysə malik deyil | Abstract `Database` interface |
| A3 | Provider state birbaşa mutate edilir | Immutable + `copyWith()` |
| A4 | Widget-lər servisi birbaşa instantiate edir | DI (`provider` və ya `get_it`) |
| A5 | Use case / interactor layer yoxdur | `use_cases/` qovluğu |
| A6 | `AppConfig` 60+ flat constant | Nested config class-lar |
| A7 | Circular dependency riski | Auth/API ayrılması |

### 1.6 🟡 ASILIQLAR

| Paket | Versiya | Problem | Həll |
|-------|---------|---------|------|
| `google_generative_ai` | ^0.2.2 | Köhnə | ^0.4.0+-ə yenilə |
| `supabase_flutter` | ^2.3.0 | Köhnə | ^2.5.0+-ə yenilə |
| `firebase_*` | comment-out | Push notif. enabled flag-də | Aktivləşdir və ya flag-i sönük et |
| `just_audio` + `audioplayers` + `flutter_sound` | hər üçü | Bloat (~50MB) | Yalnız ikisini saxla |
| Logger paketi yoxdur | — | print()-lər | `logger: ^2.0.0` əlavə et |

### 1.7 🟡 UX / FLOW

| # | Problem | Yer | Həll |
|---|---------|-----|------|
| U1 | Loading state cart-da yox | `cart_screen.dart` | Shimmer + spinner |
| U2 | Add-to-cart səhvi səssizdir | `cart_provider.dart` | 163 | Snackbar + retry |
| U3 | Voice recording UI feedback yox | `voice_shopping_screen.dart` | 301 | Pulse + timer |
| U4 | Empty chat history feedback | `chat_history_screen.dart` | CTA button |
| U5 | Order placement fail səssizdir | `checkout_screen.dart` | 1575 | Retry dialog |
| U6 | Login success feedback yox | `login_screen.dart` | 84 | "Welcome back" snackbar |
| U7 | Add-to-cart success feedback yox | `apple_product_card.dart` | 62 | Toast |
| U8 | Naviqasiya qarışıqdır | `main.dart` | 82 | `go_router` |

---

## 📋 PHASE 2 — Yeni Funksiya Təklifləri

### 2.1 🟢 MUST-HAVE (Rəqabət üçün vacibdir)

| # | Funksiya | İstifadəçi dəyəri | Mürəkkəblik | Müddət |
|---|----------|-------------------|-------------|--------|
| F1 | **Sifariş izləmə real-time** | Müştəri sifarişin harada olduğunu görür | Orta | 5–7 gün |
| F2 | **Push notifications** (Firebase) | Endirim, sifariş statusu xəbərdarlıqları | Asan | 3 gün |
| F3 | **Ödəniş inteqrasiyası** (Pasha/Kapital) | Real ödəniş | Mürəkkəb | 14 gün |
| F4 | **Multi-address dəstəyi** | Ev/iş/digər | Asan | 2 gün |
| F5 | **Sifariş təkrarı** ("yenidən sifariş") | Tez yenidən sifariş | Asan | 1 gün |
| F6 | **Dark mode** | İstifadəçi seçimi | Asan | 2 gün |

### 2.2 🟢 SHOULD-HAVE (Böyük dəyər)

| # | Funksiya | Müddət |
|---|----------|--------|
| F7 | Şəkildən axtarış (Gemini Vision) | 4 gün |
| F8 | Barkod ilə məhsul axtarışı (mobile_scanner) | 2 gün |
| F9 | Sevimlilər (wishlist) | 2 gün |
| F10 | Məhsul müqayisə ekranı | 3 gün |
| F11 | Sosial paylaşım (referal kodu) | 3 gün |
| F12 | Sifariş qiymətləndirmə + rəy yazma | 2 gün |
| F13 | Promokod sistemi | 3 gün |
| F14 | Email/SMS doğrulama (OTP) | 4 gün |

### 2.3 🟢 NICE-TO-HAVE

| # | Funksiya | Müddət |
|---|----------|--------|
| F15 | AR ilə məhsulu evdə "yerləşdir" | 14 gün |
| F16 | Reseptlər kitabxanası (kateqoriyalı) | 5 gün |
| F17 | Resept videoları (YouTube embed) | 3 gün |
| F18 | Diet izləyici + bütçe planlayıcı | 7 gün |
| F19 | Apple Watch / Wear OS app | 14 gün |
| F20 | Voice-only mode (görmə qabiliyyəti aşağı istifadəçilər) | 5 gün |

### 2.4 🟢 INNOVATION (Differensiator)

| # | Funksiya | Müddət |
|---|----------|--------|
| F21 | **Group buying** — qonşular birlikdə alır, qiymət düşür | 10 gün |
| F22 | **AI menu planner** — həftəlik yemək planı + alış-veriş siyahısı | 7 gün |
| F23 | **Smart fridge** — evdəki məhsulları izlə, qurtaranda xəbər ver | 14 gün |
| F24 | **Ramadan/holiday mode** — xüsusi kateqoriyalar, oruc vaxtı bildirişləri | 5 gün |

---

## 📋 PHASE 3 — Faza-əsaslı İcra Yol Xəritəsi

### 🏗️ FAZA 1: Foundation (Həftə 1–4)

**Məqsəd:** App release-ə hazır vəziyyətə gətir. Təhlükəsizlik + crash bug-ları həll et.

| # | Tapşırıq | Növ | Prioritet | Effort | Asılılıq |
|---|----------|-----|-----------|--------|----------|
| T1 | API açarlarını `--dart-define`-a köçür | bugfix | P0 | M (4h) | — |
| T2 | `.gitignore` + `.env.example` yarat | infrastructure | P0 | XS (1h) | T1 |
| T3 | `AppLogger` utility yarat və `print()`-ləri əvəzlə | refactor | P0 | M (8h) | — |
| T4 | Bütün `setState()`-lərə `if (mounted)` əlavə | bugfix | P0 | M (6h) | — |
| T5 | Force unwrap `!` NPE düzəlişləri | bugfix | P0 | S (4h) | — |
| T6 | Auth listener xəta idarəsi | bugfix | P0 | S (2h) | — |
| T7 | `.maybeSingle()` migration | bugfix | P1 | S (3h) | — |
| T8 | Repository pattern (Cart, Product, Order) | refactor | P1 | L (2 gün) | — |
| T9 | Pagination (products) | feature | P1 | M (1 gün) | T8 |
| T10 | Search debounce | feature | P1 | XS (2h) | — |
| T11 | Firebase setup + push notifications | feature | P1 | M (3 gün) | — |
| T12 | Dark mode | feature | P2 | S (2 gün) | — |

### 🚀 FAZA 2: Enhancement (Həftə 5–8)

**Məqsəd:** UX-i polish, performansı yaxşılaşdır, must-have funksiyaları əlavə et.

| # | Tapşırıq | Effort |
|---|----------|--------|
| T13 | Sifariş izləmə real-time | 5 gün |
| T14 | Multi-address dəstəyi | 2 gün |
| T15 | Sifariş təkrarı | 1 gün |
| T16 | Wishlist (sevimlilər) | 2 gün |
| T17 | Barkod scanner aktivləşdir | 2 gün |
| T18 | Sifariş qiymətləndirmə + rəy | 2 gün |
| T19 | OTP email/SMS doğrulama | 4 gün |
| T20 | Promokod sistemi | 3 gün |
| T21 | God class refactoring (AIService) | 3 gün |
| T22 | Localization (`intl` + json) | 4 gün |
| T23 | N+1 query fix + chat session optimization | 1 gün |
| T24 | Empty states + error retry UI | 2 gün |

### 💎 FAZA 3: Innovation (Həftə 9–14)

**Məqsəd:** Differensiator funksiyalar — bazarda fərqlən.

| # | Tapşırıq | Effort |
|---|----------|--------|
| T25 | Şəkildən axtarış (Gemini Vision) | 4 gün |
| T26 | AI menu planner (həftəlik) | 7 gün |
| T27 | Group buying (qonşular birlikdə) | 10 gün |
| T28 | Reseptlər kitabxanası | 5 gün |
| T29 | Smart fridge (məhsul izlə) | 14 gün |
| T30 | Ödəniş inteqrasiyası (Pasha) | 14 gün |
| T31 | Ramadan/holiday mode | 5 gün |
| T32 | Apple Watch app | 14 gün |

---

## 📈 Vizual Prioritet Matrisi

```
                        TƏSIR
                Aşağı  ←──────→  Yüksək
              ┌─────────────────────────┐
   Aşağı     │  T6  T10│ T1  T2  T3  T4 │ ← TEZ ET (Quick wins + P0)
   Effort    │  T7    │ T5  T11 T13      │
   ↑         │         │                  │
   ↓         │  T22 T24│ T8  T9  T19 T20  │
   Yüksək   │  T28 T29│ T25 T26 T27 T30  │ ← STRATEJI (Böyük layihələr)
              └─────────────────────────┘
```

**Tövsiyə:** Yuxarı-sağ kvadrant ilə başla → aşağı-sağ kvadranta keç → sonra sol tərəf.

---

## 🎯 Müvəffəqiyyət Meyarları (Success Criteria)

| Faza | KPI | Hədəf |
|------|-----|-------|
| Faza 1 | Crash-free user rate | >99.5% |
| Faza 1 | Production deploy üçün hazır | ✅ |
| Faza 1 | Static analyzer xəbərdarlıq sayı | <10 |
| Faza 2 | App Store reytinq | ≥4.3 |
| Faza 2 | Conversion rate (cart → order) | >35% |
| Faza 2 | DAU/MAU | >40% |
| Faza 3 | Aktiv istifadəçi | 10.000+ |
| Faza 3 | Revenue/ay | 100.000 AZN+ |

---

## 🛠️ Test Strategiyası

| Test növü | Coverage hədəf | Alət |
|-----------|----------------|------|
| Unit testlər | >70% (services + providers) | `flutter_test` |
| Widget testlər | Kritik ekranlar | `flutter_test` |
| Integration testlər | Auth + Order flow | `integration_test` |
| Manual QA | Hər release | TestFlight + Internal track |
| Performance | Frame rate, memory | DevTools |

---

## 📝 Qeyd

Bu sənəd canlı sənəddir — hər sprint sonunda yenilənir. P0-lar həll olunduqdan sonra production-a çıxış qərarı verilir.

**Növbəti addım:** P0 düzəlişlərinin dərhal tətbiqi (bax: aşağıdakı kodlar).
