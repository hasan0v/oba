# Google Maps Setup Script for OBA Mobile App
# Run this after getting your API key from Google Cloud Console

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

Write-Host "🗺️  Setting up Google Maps for OBA Mobile App..." -ForegroundColor Green
Write-Host ""

# Android setup
$androidManifestPath = "android/app/src/main/AndroidManifest.xml"
Write-Host "📱 Configuring Android..." -ForegroundColor Cyan

if (Test-Path $androidManifestPath) {
    $manifest = Get-Content $androidManifestPath -Raw
    
    # Check if API key already exists
    if ($manifest -match 'com.google.android.geo.API_KEY') {
        Write-Host "   ℹ️  API key already configured in Android manifest" -ForegroundColor Yellow
        $manifest = $manifest -replace '(<meta-data[^>]*android:name="com.google.android.geo.API_KEY"[^>]*android:value=")[^"]*(")', "`$1$ApiKey`$2"
    } else {
        # Add API key before </application>
        $apiKeyMeta = @"
  
  <!-- Google Maps API Key -->
  <meta-data
      android:name="com.google.android.geo.API_KEY"
      android:value="$ApiKey"/>
"@
        $manifest = $manifest -replace '(</application>)', "$apiKeyMeta`n    `$1"
    }
    
    Set-Content -Path $androidManifestPath -Value $manifest
    Write-Host "   ✅ Android configuration complete" -ForegroundColor Green
} else {
    Write-Host "   ❌ Android manifest not found at $androidManifestPath" -ForegroundColor Red
}

Write-Host ""

# iOS setup (Swift)
$iosAppDelegatePath = "ios/Runner/AppDelegate.swift"
Write-Host "🍎 Configuring iOS..." -ForegroundColor Cyan

if (Test-Path $iosAppDelegatePath) {
    $appDelegate = Get-Content $iosAppDelegatePath -Raw
    
    # Check if already configured
    if ($appDelegate -match 'GMSServices.provideAPIKey') {
        Write-Host "   ℹ️  API key already configured in iOS AppDelegate" -ForegroundColor Yellow
        $appDelegate = $appDelegate -replace '(GMSServices\.provideAPIKey\(")[^"]*("\))', "`$1$ApiKey`$2"
    } else {
        # Add import if not exists
        if ($appDelegate -notmatch 'import GoogleMaps') {
            $appDelegate = $appDelegate -replace '(import UIKit)', "`$1`nimport GoogleMaps"
        }
        
        # Add API key configuration
        $appDelegate = $appDelegate -replace '(didFinishLaunchingWithOptions[^\{]*\{)', @"
`$1
    GMSServices.provideAPIKey("$ApiKey")
"@
    }
    
    Set-Content -Path $iosAppDelegatePath -Value $appDelegate
    Write-Host "   ✅ iOS configuration complete" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  iOS AppDelegate.swift not found" -ForegroundColor Yellow
    Write-Host "   📝 Manual setup required - see BRANCH_SELECTION_GUIDE.md" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Google Maps setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'flutter pub get' to install dependencies"
Write-Host "2. Run 'flutter clean' to clear build cache"
Write-Host "3. Rebuild your app"
Write-Host ""
Write-Host "📖 For detailed setup instructions, see BRANCH_SELECTION_GUIDE.md"
Write-Host ""
