pluginManagement {
    val flutterSdkPath = run {
        val properties = java.util.Properties()
        file("local.properties").inputStream().use { properties.load(it) }
        val flutterSdkPath = properties.getProperty("flutter.sdk")
        require(flutterSdkPath != null) { "flutter.sdk not set in local.properties" }
        flutterSdkPath
    }

    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id("dev.flutter.flutter-plugin-loader") version "1.0.0"
    id("com.android.application") version "8.7.0" apply false
    // Kotlin 2.1.0 required by Firebase BoM 33.5.x (play-services-measurement
    // is compiled with Kotlin metadata version 2.1.0).
    id("org.jetbrains.kotlin.android") version "2.1.0" apply false
    // Firebase (T11) — google-services plugin, applied in app/build.gradle.kts
    id("com.google.gms.google-services") version "4.4.2" apply false
}

include(":app")
