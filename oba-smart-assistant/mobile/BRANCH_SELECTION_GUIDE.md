# Branch Selection Feature - Mağazadan Götür

This feature enables users to select an OBA branch for pickup when choosing "Mağazadan Götür" (Store Pickup) option during checkout.

## Features

### 1. **Location-Based Branch Suggestions** 🎯
- Automatically detects user's current location
- Calculates distance to all OBA branches
- Suggests nearest 3-5 branches sorted by distance
- Shows distance in kilometers or meters

### 2. **Interactive Map Selection** 🗺️
- Google Maps integration for visual branch selection
- Color-coded markers:
  - 🔵 Blue: User's current location
  - 🟢 Green: Selected branch
  - 🟠 Orange: Available branches
- Tap any marker to select that branch
- Automatic camera positioning to show user and selected branch

### 3. **Smart Branch Matching** 🧠
- Haversine formula for accurate distance calculation
- Real-time distance updates based on user location
- Search functionality to find branches by name
- Filter branches within specific radius

### 4. **Seamless Checkout Integration** 🛒
- Branch selection appears when "Mağazadan Götür" is selected
- Shows top 3 nearest branches in the list
- "Xəritədə Seç" button for map view
- Validates branch selection before proceeding
- Displays selected branch in order summary

## Technical Implementation

### Files Created/Modified

#### New Files:
1. **`lib/models/branch.dart`** - ObaBranch model with distance calculation
2. **`lib/services/location_service.dart`** - Location & distance calculations
3. **`lib/services/branch_service.dart`** - API service for branch operations
4. **`lib/screens/branch_selection_map_screen.dart`** - Interactive map UI

#### Modified Files:
1. **`lib/screens/checkout_screen.dart`** - Integrated branch selection
2. **`pubspec.yaml`** - Added dependencies
3. **`mobile/assets/data/`** - Added oba_branches.json

### Dependencies Added

```yaml
dependencies:
  geolocator: ^11.0.0        # Location services
  google_maps_flutter: ^2.5.3 # Map display
```

### Key Components

#### 1. ObaBranch Model
```dart
class ObaBranch {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final double? distanceKm;
  
  // Helper methods for display
  String get displayName;
  String get formattedDistance;
  ObaBranch copyWithDistance(double distance);
}
```

#### 2. LocationService
```dart
class LocationService {
  // Get user's current location
  Future<Position?> getCurrentLocation();
  
  // Calculate distance between coordinates
  double calculateDistance(lat1, lon1, lat2, lon2);
  
  // Get nearest branches (sorted by distance)
  Future<List<ObaBranch>> getNearestBranches({limit, userLocation});
  
  // Search branches by name
  Future<List<ObaBranch>> searchBranches(String query);
  
  // Get branches within radius
  Future<List<ObaBranch>> getBranchesInRadius({radiusKm, userLocation});
}
```

#### 3. BranchSelectionMapScreen
- Interactive Google Maps view
- Draggable bottom sheet with branch list
- Search bar for filtering branches
- Current location button
- Real-time marker updates

## Setup Instructions

### 1. Install Dependencies
```bash
cd mobile
flutter pub get
```

### 2. Configure Google Maps API

#### For Android:
1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<application>
  <meta-data
    android:name="com.google.android.geo.API_KEY"
    android:value="YOUR_API_KEY_HERE"/>
</application>
```

#### For iOS:
1. Add to `ios/Runner/AppDelegate.swift`:
```swift
import GoogleMaps

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GMSServices.provideAPIKey("YOUR_API_KEY_HERE")
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

### 3. Configure Location Permissions

#### Android (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

#### iOS (`ios/Runner/Info.plist`):
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>OBA tətbiqi sizə ən yaxın mağazanı tapmaqdır</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>OBA tətbiqi sizə ən yaxın mağazanı tapmaq üçün yerləşməyə ehtiyac duyur</string>
```

### 4. Verify Assets
Ensure `oba_branches.json` is copied to `mobile/assets/data/`:
```bash
# The file should be at:
mobile/assets/data/oba_branches.json
```

## Usage Flow

### User Journey:
1. User adds items to cart
2. Proceeds to checkout
3. Selects "Mağazadan Götür" option
4. System shows:
   - Nearest branch (auto-selected)
   - Top 3 nearest branches
   - "Xəritədə Seç" button
5. User can:
   - Select from nearby branches list
   - Open map view for visual selection
   - Search for specific branch
6. Selected branch appears in order summary
7. Order is placed with pickup details

### Map Screen Interaction:
1. Opens with nearest branch selected
2. Shows user location and all branches
3. User can:
   - Pan/zoom the map
   - Tap markers to select branches
   - Use search to filter
   - Scroll through list in bottom sheet
4. Confirm selection returns to checkout

## Distance Calculation

Uses **Haversine Formula** for accurate great-circle distance:

```dart
double calculateDistance(lat1, lon1, lat2, lon2) {
  const earthRadius = 6371; // km
  
  final dLat = toRadians(lat2 - lat1);
  final dLon = toRadians(lon2 - lon1);
  
  final a = sin(dLat/2) * sin(dLat/2) +
            cos(toRadians(lat1)) * cos(toRadians(lat2)) *
            sin(dLon/2) * sin(dLon/2);
  
  final c = 2 * atan2(sqrt(a), sqrt(1-a));
  
  return earthRadius * c;
}
```

## Data Format

### oba_branches.json Structure:
```json
{
  "branches": [
    {
      "id": 1,
      "name": "OBA-QARACHUXUR 8",
      "latitude": 40.400486148133,
      "longitude": 49.9785234134508,
      "distance_km": 0.12
    }
  ]
}
```

## Error Handling

### Location Permission Denied:
- Shows branches without distance calculation
- Uses default sorting (by ID)
- Displays message to enable location

### No Internet Connection:
- Loads branches from local JSON asset
- Map may not load (requires connectivity)
- Shows appropriate error messages

### Branch Data Load Failure:
- Gracefully falls back to empty list
- Logs error for debugging
- Shows user-friendly message

## Performance Optimizations

1. **Caching**: Branches cached after first load
2. **Lazy Loading**: Only top N branches calculated initially
3. **Debounced Search**: Search triggers after typing pause
4. **Efficient Markers**: Only visible branches shown on map
5. **Background Loading**: Location fetched asynchronously

## Future Enhancements

- [ ] Branch operating hours
- [ ] Real-time stock availability per branch
- [ ] Estimated pickup time
- [ ] Branch photos and amenities
- [ ] Route navigation to selected branch
- [ ] Favorite branches
- [ ] Recent branch selections
- [ ] Branch reviews and ratings
- [ ] Push notifications when order ready

## Testing Checklist

- [ ] Location permission flow (granted/denied)
- [ ] Distance calculation accuracy
- [ ] Map marker interactions
- [ ] Branch selection persistence
- [ ] Search functionality
- [ ] Network error scenarios
- [ ] Different device locations
- [ ] iOS and Android platforms
- [ ] Checkout flow integration
- [ ] Order submission with branch info

## API Integration (Future)

When backend API is ready, the `BranchService` can fetch live data:

```dart
// Fetch from API instead of local JSON
final branches = await BranchService().fetchBranches();

// Check real-time availability
final isAvailable = await BranchService().checkBranchAvailability(branchId);

// Get estimated pickup time
final pickupTime = await BranchService().getEstimatedPickupTime(branchId);
```

## Troubleshooting

### Maps not showing:
- Verify Google Maps API key
- Check API is enabled in Google Cloud Console
- Ensure billing is enabled
- Check platform-specific configuration

### Location not working:
- Check permissions in app settings
- Verify location services enabled on device
- Check manifest/Info.plist permissions
- Test on physical device (not simulator)

### Branches not loading:
- Verify JSON file in assets
- Check pubspec.yaml assets configuration
- Run `flutter clean` and rebuild
- Check console for error logs

## Support

For issues or questions:
- Check error logs in console
- Verify all setup steps completed
- Test on physical device
- Check Google Maps API quotas

---

**Last Updated**: January 23, 2026
**Version**: 1.0.0
**Platform**: Flutter (iOS & Android)
