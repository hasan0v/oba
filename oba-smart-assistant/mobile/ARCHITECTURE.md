# Branch Selection Architecture

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────┐      ┌─────────────────────────┐   │
│  │  Checkout Screen   │      │ Branch Selection Map    │   │
│  │                    │      │                         │   │
│  │  - Delivery opts   │◄────►│  - Google Maps          │   │
│  │  - Branch list     │      │  - Branch markers       │   │
│  │  - Map button      │      │  - Search bar           │   │
│  │  - Validation      │      │  - Bottom sheet         │   │
│  └────────┬───────────┘      └──────────┬──────────────┘   │
│           │                             │                   │
└───────────┼─────────────────────────────┼───────────────────┘
            │                             │
┌───────────▼─────────────────────────────▼───────────────────┐
│                      Services Layer                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐    ┌───────────────────────┐     │
│  │  LocationService     │    │   BranchService       │     │
│  │                      │    │                       │     │
│  │  - Get location      │    │   - API calls         │     │
│  │  - Calculate dist    │    │   - Branch search     │     │
│  │  - Load branches     │    │   - Availability      │     │
│  │  - Find nearest      │    │   - Pickup time       │     │
│  │  - Cache data        │    │                       │     │
│  └──────────┬───────────┘    └───────────┬───────────┘     │
│             │                            │                  │
└─────────────┼────────────────────────────┼──────────────────┘
              │                            │
┌─────────────▼────────────────────────────▼──────────────────┐
│                      Data Layer                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐    ┌───────────────────────┐     │
│  │   ObaBranch Model    │    │   Local Assets        │     │
│  │                      │    │                       │     │
│  │  - id, name          │◄───┤  oba_branches.json    │     │
│  │  - lat, lng          │    │  (11,688 branches)    │     │
│  │  - distance          │    │                       │     │
│  │  - helpers           │    │                       │     │
│  └──────────────────────┘    └───────────────────────┘     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

### 1. **Checkout Screen Loads**
```
User Opens Checkout
        ↓
LocationService.init()
        ↓
Request Location Permission
        ↓
Get Current Position (GPS)
        ↓
Load Branches from JSON
        ↓
Calculate Distances (Haversine)
        ↓
Sort by Distance
        ↓
Display Top 3 Nearest
        ↓
Auto-select Nearest Branch
```

### 2. **Map Selection Flow**
```
User Clicks "Xəritədə Seç"
        ↓
Open BranchSelectionMapScreen
        ↓
Load Google Maps
        ↓
Add User Location Marker (Blue)
        ↓
Add Branch Markers (Orange/Green)
        ↓
User Taps Marker or List Item
        ↓
Update Selected Branch (Green)
        ↓
User Confirms Selection
        ↓
Return to Checkout
        ↓
Update UI with Selected Branch
```

### 3. **Distance Calculation**
```
User Location (lat₁, lng₁)
        ↓
Branch Location (lat₂, lng₂)
        ↓
Haversine Formula:
  a = sin²(Δlat/2) + cos(lat₁) × cos(lat₂) × sin²(Δlng/2)
  c = 2 × atan2(√a, √(1-a))
  distance = R × c  (R = 6371 km)
        ↓
Format Distance (km or m)
        ↓
Display to User
```

## 🔄 Component Interaction

```
┌──────────────┐
│ CheckoutScreen│
└──────┬───────┘
       │
       │ Loads branches
       ├──────────────────►┌──────────────────┐
       │                   │ LocationService  │
       │                   └────────┬─────────┘
       │                            │
       │                            │ Reads JSON
       │                            ├─────────►┌───────────────┐
       │                            │          │ oba_branches  │
       │                            │◄─────────┤     .json     │
       │                            │          └───────────────┘
       │ Receives branches          │
       │◄───────────────────────────┤
       │                            │
       │                            │ Calculates
       │                            │ distances
       │                            │
       │ Opens map                  │
       ├──────────────────►┌────────▼─────────┐
       │                   │ BranchSelection  │
       │                   │   MapScreen      │
       │                   └────────┬─────────┘
       │                            │
       │                            │ Uses same
       │                            │ service
       │                            ├─────────►┌──────────────┐
       │                            │          │ LocationServ │
       │                            │◄─────────┤              │
       │                            │          └──────────────┘
       │ Returns selected           │
       │ branch                     │
       │◄───────────────────────────┤
       │                            │
       ▼                            ▼
```

## 🎯 State Management

```
CheckoutScreen State:
├── _selectedDeliveryOption: int
├── _selectedBranch: ObaBranch?
├── _nearestBranches: List<ObaBranch>
├── _isLoadingBranches: bool
└── _locationService: LocationService

BranchSelectionMapScreen State:
├── _branches: List<ObaBranch>
├── _selectedBranch: ObaBranch?
├── _userLocation: Position?
├── _isLoading: bool
├── _searchQuery: String
└── _mapController: GoogleMapController?

LocationService (Singleton):
├── _cachedBranches: List<ObaBranch>?
├── _lastKnownPosition: Position?
└── Methods for calculations
```

## 🔐 Permission Flow

```
App Starts
    ↓
LocationService.getCurrentLocation()
    ↓
Check: isLocationServiceEnabled()
    ├── NO → Return null, show branches without distance
    └── YES → Continue
              ↓
Check: checkPermission()
    ├── DENIED → requestPermission()
    │            ├── GRANTED → Continue
    │            └── DENIED → Return null
    └── GRANTED → Continue
                  ↓
Get Current Position
    ↓
Cache Position
    ↓
Return Position
```

## 📱 Screen Hierarchy

```
App
└── CheckoutScreen
    ├── DeliveryOptions
    │   └── "Mağazadan Götür" Option
    │       ├── Selected Branch Card
    │       ├── Map Button → BranchSelectionMapScreen
    │       │                ├── Google Map
    │       │                ├── Search Bar
    │       │                └── Branch List (Bottom Sheet)
    │       └── Nearest Branches List (3)
    ├── PaymentOptions
    └── OrderSummary
        └── Shows Selected Branch
```

## 🚀 Performance Flow

```
Initial Load:
├── Load branches from JSON (~100ms)
├── Request location (~500-2000ms)
├── Calculate top 10 distances (~10ms)
└── Render UI (~50ms)
    Total: ~700-2200ms

Map Load:
├── Open screen (~50ms)
├── Initialize Google Map (~500ms)
├── Create markers (~100ms)
└── Position camera (~200ms)
    Total: ~850ms

Search:
├── Filter branches (~5ms)
├── Update UI (~20ms)
└── Total: ~25ms (debounced 300ms)
```

## 💾 Caching Strategy

```
LocationService Cache:
└── _cachedBranches
    ├── Loaded on first call
    ├── Persists during app session
    └── Can be cleared with clearCache()

Location Cache:
└── _lastKnownPosition
    ├── Updated on each location fetch
    ├── Used for distance calculations
    └── Avoids repeated GPS calls

Benefits:
├── Faster subsequent loads
├── Reduced battery usage
├── Less network/GPS usage
└── Better user experience
```

## 🎨 UI Component Tree

```
CheckoutScreen
└── Scaffold
    ├── Stack
    │   ├── Ambient Orbs (Background)
    │   └── Column
    │       ├── Header
    │       ├── Progress Indicator
    │       ├── Content
    │       │   └── DeliveryStep
    │       │       ├── Delivery Options (Cards)
    │       │       ├── Branch Selection (if pickup)
    │       │       │   ├── Selected Branch Card
    │       │       │   ├── Map Button
    │       │       │   └── Nearest Branches List
    │       │       └── Address Input (if delivery)
    │       └── Bottom Action Bar

BranchSelectionMapScreen
└── Scaffold
    └── Stack
        ├── Google Map (Full Screen)
        ├── SafeArea
        │   ├── Header Card
        │   └── Search Bar
        └── DraggableScrollableSheet
            ├── Handle
            ├── Selected Branch Card
            └── Branch List
```

## 🔌 External Dependencies

```
Google Services:
└── Google Maps Platform
    ├── Maps SDK for Android
    ├── Maps SDK for iOS
    └── API Key (required)

Device Services:
└── Location Services
    ├── GPS Provider
    ├── Network Provider
    └── Permissions (runtime)

Flutter Packages:
├── google_maps_flutter: ^2.5.3
├── geolocator: ^11.0.0
└── Other app dependencies
```

---

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Reusable services
- ✅ Efficient data flow
- ✅ Optimal performance
- ✅ Easy maintainability
