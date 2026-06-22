# Branch Selection - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Get Google Maps API Key
```
1. Visit: https://console.cloud.google.com/
2. Create new project or select existing
3. Enable: "Maps SDK for Android" and "Maps SDK for iOS"
4. Create API Key
5. Copy the key
```

### Step 2: Configure API Key
```powershell
# Option A: Use our script (recommended)
cd mobile
.\scripts\setup_google_maps.ps1 -ApiKey "YOUR_API_KEY_HERE"

# Option B: Manual setup
# See BRANCH_SELECTION_GUIDE.md for details
```

### Step 3: Install Dependencies
```bash
cd mobile
flutter pub get
flutter clean
```

### Step 4: Run the App
```bash
flutter run
```

## 📱 How It Works

### User Flow:
```
Cart → Checkout → Select "Mağazadan Götür" → See Nearest Branches
                                              ↓
                           Choose from list OR Click map button
                                              ↓
                                    Select Branch on Map
                                              ↓
                                      Confirm Selection
                                              ↓
                                      Complete Order
```

### Key Features:
- 🎯 **Auto-detects** nearest branches based on location
- 🗺️ **Interactive map** with all 11,688 OBA branches
- 📍 **Distance calculation** using GPS coordinates
- 🔍 **Search** for specific branches
- ✅ **Easy selection** with visual feedback

## 🔑 Key Files

```
lib/models/branch.dart              - Branch data model
lib/services/location_service.dart  - Location & distance logic
lib/screens/branch_selection_map_screen.dart - Map UI
lib/screens/checkout_screen.dart    - Integration
assets/data/oba_branches.json       - 11,688 branches
```

## 🎯 Testing Checklist

- [ ] Location permission granted
- [ ] Can see nearest branches in checkout
- [ ] Map opens when clicking "Xəritədə Seç"
- [ ] Can select branch from list
- [ ] Can select branch from map
- [ ] Distance shows correctly
- [ ] Selected branch appears in order summary
- [ ] Can complete order with branch selected

## ⚠️ Troubleshooting

### Map not showing?
```
✓ Check API key is correct
✓ Verify APIs enabled in Google Cloud
✓ Check AndroidManifest.xml / AppDelegate.swift
✓ Run 'flutter clean' and rebuild
```

### Location not working?
```
✓ Grant location permission in app settings
✓ Enable GPS on device
✓ Test on real device (not simulator)
✓ Check AndroidManifest.xml / Info.plist
```

### Branches not loading?
```
✓ Verify oba_branches.json in assets/data/
✓ Check pubspec.yaml includes assets/data/
✓ Run 'flutter pub get'
✓ Check console for errors
```

## 📖 Full Documentation

- **Setup Guide**: `BRANCH_SELECTION_GUIDE.md`
- **Implementation**: `BRANCH_SELECTION_SUMMARY.md`
- **API Reference**: See inline comments in code

## 💡 Tips

1. **Test on real device** - Location works better on physical devices
2. **Check permissions** - Make sure location is allowed
3. **Use WiFi for maps** - Initial map load requires internet
4. **Cache works offline** - Branches cached after first load

## 🎉 You're Ready!

Once Google Maps is configured, the feature is production-ready!

---
Need help? Check `BRANCH_SELECTION_GUIDE.md` for detailed instructions.
