import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
    // Firebase (T11) — reads google-services.json next to this file.
    id("com.google.gms.google-services")
}

// =============================================================================
// Secrets loading (T1 — Phase 1)
//
// 1. Reads `secret.properties` from the android/ folder if present (gitignored).
//    Format:
//      MAPS_API_KEY=AIza...
//      GEMINI_API_KEY=AIza...
//      SUPABASE_URL=https://....supabase.co
//      SUPABASE_ANON_KEY=eyJhbGc...
//
// 2. Falls back to env vars (CI/CD friendly).
// 3. Falls back to the original committed defaults so dev builds keep working.
// =============================================================================
val secretsFile = rootProject.file("secret.properties")
val secretProps = Properties().apply {
    if (secretsFile.exists()) {
        load(FileInputStream(secretsFile))
    }
}

fun secret(key: String, default: String): String {
    return secretProps.getProperty(key)
        ?: System.getenv(key)
        ?: default
}

val mapsApiKey      = secret("MAPS_API_KEY",      "AIzaSyAVj4PwOfXMIZfBWMWcEfea_cMqwemNcys")
// Note: Gemini & Supabase keys are read on the Dart side via String.fromEnvironment
// (see lib/config/app_config.dart). Pass them at build/run time with
//   flutter build apk --dart-define-from-file=.env
// or rely on the committed dev defaults inside AppConfig.

android {
    namespace = "com.example.oba_smart_assistant"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = "27.0.12077973"

    compileOptions {
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        // NOTE: applicationId must match the package_name in
        // android/app/google-services.json (Firebase project binding).
        // Kotlin source files still live under com.example.oba_smart_assistant
        // (see `namespace` above) — Android allows these to differ.
        applicationId = "com.codelandia.smart_assisstant"
        minSdk = 24
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        multiDexEnabled = true

        // Inject Maps API key into AndroidManifest.xml (replaces ${MAPS_API_KEY}).
        // Dart-side keys (Gemini, Supabase) come from AppConfig defaults OR from
        // `flutter run/build --dart-define-from-file=.env` at the Flutter layer.
        manifestPlaceholders["MAPS_API_KEY"] = mapsApiKey
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
    // WindowManager for Android 12L+ fix with desugaring
    implementation("androidx.window:window:1.0.0")
    implementation("androidx.window:window-java:1.0.0")
    // Firebase BoM — versions of individual Firebase libs are managed centrally.
    implementation(platform("com.google.firebase:firebase-bom:33.5.1"))
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-messaging")
}
