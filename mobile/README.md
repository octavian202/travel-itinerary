# City Break Planner – Mobile (Expo)

## Setup

```bash
cd mobile
npm install
```

## Environment

- **`EXPO_PUBLIC_API_URL`** – Backend base URL (default: `http://localhost:8000`). Use your machine IP (e.g. `http://192.168.1.x:8000`) when running on a physical device.
- **`EXPO_PUBLIC_MAPBOX_ACCESS_TOKEN`** – Mapbox public token (starts with `pk.`) for the map. Required for the real map; without it you get a placeholder.

## Run

```bash
npx expo start
```

- Press `w` for web, `a` for Android, `i` for iOS simulator.
- **Map:** `@rnmapbox/maps` uses native code and does **not** work in Expo Go. For the full map you must create a development build:

  ```bash
  npx expo prebuild --clean
  npx expo run:ios
  # or
  npx expo run:android
  ```

  Until then, the itinerary screen shows a placeholder where the map would be; the day list and stops still work.

## Screens

1. **Input** – City name, days (1–14), pace (relaxed / moderate / fast). Tap “Generate itinerary”.
2. **Loading** – Shown while the backend runs (about 5–15 s).
3. **Itinerary** – Day tabs, map (top), scrollable list of stops (bottom). “New itinerary” returns to input.

## Backend

Start the API and DB first (see project root and `backend/README.md`).
