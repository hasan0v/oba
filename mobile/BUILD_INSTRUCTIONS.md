# OBASA — Build & Run Instructions (Phase 1)

> Yeniləndi: Phase 1 implementation tamamlandıqdan sonra.
> Hədəf: Həm `flutter run`, həm də `flutter build apk --release` API açarları
> ilə düzgün işləsin.

---

## 1. Tələblər

- Flutter SDK 3.16+
- Android SDK + emulator (API 35 sınanmışdır: `Medium_Phone_API_35`)
- Java 11
- Real cihaz üçün: Google Maps Android API key, Supabase URL+anon, Gemini API key

---

## 2. API açarları — harada saxlanılır?

İki yer var, hər ikisi git-ignored:

### 2.1. `mobile/.env` (Dart-side: Gemini, Supabase)

`.env.example`-i kopyalayın:

```bash
cd mobile
cp .env.example .env
```

`.env` faylını redaktə edib açarları daxil edin:

```env
GEMINI_API_KEY=AIza...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
GOOGLE_MAPS_API_KEY=AIza...
```

> **Qeyd:** `mobile/lib/config/app_config.dart` faylında dev üçün
> default-lar var — `.env` olmasa da app işləyir, sadəcə dev keys istifadə olunur.

### 2.2. `mobile/android/secret.properties` (Android manifest: Maps key)

`secret.properties.example`-i kopyalayın:

```bash
cd mobile/android
cp secret.properties.example secret.properties
```

Yalnız `MAPS_API_KEY` lazımdır (Gemini/Supabase Android tərəfdən oxunmur).

```properties
MAPS_API_KEY=AIzaSy...your_real_maps_key
```

`android/app/build.gradle.kts` bu açarı oxuyur və
`AndroidManifest.xml`-ə `${MAPS_API_KEY}` placeholder kimi inject edir.

---

## 3. Run / Build əmrləri

### Debug (emulator)

```bash
cd mobile
flutter run --dart-define-from-file=.env
```

Əgər `.env` yoxdursa, sadəcə:

```bash
flutter run
```

(default açarlar AppConfig-dən istifadə olunacaq)

### Release APK

```bash
cd mobile
flutter build apk --release --dart-define-from-file=.env
```

Çıxış: `build/app/outputs/flutter-apk/app-release.apk`

### Release Android App Bundle (Play Store)

```bash
flutter build appbundle --release --dart-define-from-file=.env
```

---

## 4. CI/CD üçün

`secret.properties` və `.env` git-ignored olduğu üçün CI-də ya:

**A) Environment variables** (Gradle avtomatik oxuyur):
```
MAPS_API_KEY=...
GEMINI_API_KEY=...
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

**B) Pipeline başında faylları yarat:**
```yaml
- name: Create secrets
  run: |
    echo "MAPS_API_KEY=${{ secrets.MAPS_API_KEY }}" > mobile/android/secret.properties
    echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" > mobile/.env
    echo "SUPABASE_URL=${{ secrets.SUPABASE_URL }}" >> mobile/.env
    echo "SUPABASE_ANON_KEY=${{ secrets.SUPABASE_ANON_KEY }}" >> mobile/.env
```

---

## 5. Phase 1 — Tətbiq edilmiş dəyişikliklər

| # | Tapşırıq | Status |
|---|----------|--------|
| T1 | API açarları → --dart-define + Android manifest placeholder | ✅ |
| T2 | `.gitignore` + `.env.example` + `secret.properties.example` | ✅ |
| T3 | `AppLogger` (yeni kod üçün) — mövcud `debugPrint` saxlanıldı | ✅ |
| T4 | `mounted` yoxlamaları (checkout, voice_shopping) | ✅ |
| T5 | Force-unwrap düzəlişləri (real olanlar) | ✅ |
| T6 | Auth listener error handler | ✅ |
| T7 | `.single()` → `.maybeSingle()` (getOrderById) | ✅ |
| T8 | Repository pattern | ⏭️ Phase 2-ə təxirə salındı |
| T9 | Real pagination (`.range(start, end)` + `getProductsCount()`) | ✅ |
| T10 | Search debounce (500ms) — `searchProductsDebounced()` | ✅ |
| T11 | Firebase Push Notifications | ⏸️ Bloklandı — `google-services.json` lazımdır |
| T12 | Dark mode (`ThemeProvider` + `ThemeMode.system`) | ✅ |

### T11 — Push notifications üçün lazım olan

`google-services.json` faylı:
1. https://console.firebase.google.com → yeni layihə yarat (və ya mövcudu seç)
2. Add app → Android → package name: `com.example.oba_smart_assistant`
3. `google-services.json`-u yüklə → `mobile/android/app/google-services.json`-a qoy
4. `pubspec.yaml`-da `firebase_core` və `firebase_messaging` paketlərini aktivləşdir
5. `android/build.gradle.kts`-ə `id("com.google.gms.google-services") version "4.4.0" apply false`
6. `android/app/build.gradle.kts`-ə `id("com.google.gms.google-services")`

---

## 6. Dark mode istifadəsi

UI-da dark mode toggle əlavə etmək üçün:

```dart
// İstənilən widget-də:
final themeProvider = context.read<ThemeProvider>();
themeProvider.toggle();                     // dark ↔ light
themeProvider.setMode(ThemeMode.system);    // OS-a uyğun
```

Default: `ThemeMode.system` (OS dark mode-a uyğun avtomatik dəyişir).
Seçim `SharedPreferences`-da saxlanılır.
