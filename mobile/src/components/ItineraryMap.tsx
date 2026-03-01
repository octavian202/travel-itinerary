/**
 * Interactive map (TDD Section 5): POIs as PointAnnotation, route as ShapeSource + LineLayer.
 * Requires @rnmapbox/maps and a development build (not Expo Go). Set MAPBOX_ACCESS_TOKEN.
 */
import React, { useMemo, useEffect } from 'react';
import { View, Text, StyleSheet, Platform } from 'react-native';
import type { POIResponse } from '../types/api';

// Mapbox token: set in app entry (Mapbox.setAccessToken) or via env
const MAPBOX_TOKEN = process.env.EXPO_PUBLIC_MAPBOX_ACCESS_TOKEN;

export interface ItineraryMapProps {
  stops: POIResponse[];
  routeCoordinates: [number, number][]; // [lon, lat] from API
  style?: object;
}

/**
 * GeoJSON LineString for the day's route to be drawn via ShapeSource + LineLayer.
 */
function makeRouteGeoJSON(coords: [number, number][]) {
  return {
    type: 'Feature' as const,
    properties: {},
    geometry: {
      type: 'LineString' as const,
      coordinates: coords,
    },
  };
}

export function ItineraryMap({ stops, routeCoordinates, style }: ItineraryMapProps) {
  const [MapboxReady, setMapboxReady] = React.useState(false);
  const [MapView, setMapView] = React.useState<any>(null);
  const [Camera, setCamera] = React.useState<any>(null);
  const [PointAnnotation, setPointAnnotation] = React.useState<any>(null);
  const [ShapeSource, setShapeSource] = React.useState<any>(null);
  const [LineLayer, setLineLayer] = React.useState<any>(null);
  const [Mapbox, setMapbox] = React.useState<any>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const maps = require('@rnmapbox/maps');
        if (maps.default && typeof maps.default.setAccessToken === 'function') {
          maps.default.setAccessToken(MAPBOX_TOKEN || '');
        }
        if (!cancelled) {
          setMapbox(maps.default);
          setMapView(maps.MapView);
          setCamera(maps.Camera);
          setPointAnnotation(maps.PointAnnotation);
          setShapeSource(maps.ShapeSource);
          setLineLayer(maps.LineLayer);
          setMapboxReady(true);
        }
      } catch {
        if (!cancelled) setMapboxReady(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const routeShape = useMemo(() => makeRouteGeoJSON(routeCoordinates), [routeCoordinates]);

  // Center and zoom from stops (or route) bounds
  const center = useMemo((): [number, number] => {
    if (stops.length === 0) return [23.5, 46.7]; // fallback Cluj
    const lons = stops.map((s) => s.coordinates.longitude);
    const lats = stops.map((s) => s.coordinates.latitude);
    return [
      (Math.min(...lons) + Math.max(...lons)) / 2,
      (Math.min(...lats) + Math.max(...lats)) / 2,
    ];
  }, [stops]);

  if (!MapboxReady || !MapView || !Camera) {
    return (
      <View style={[styles.placeholder, style]}>
        <Text style={styles.placeholderText}>
          Map requires a development build with @rnmapbox/maps. Set EXPO_PUBLIC_MAPBOX_ACCESS_TOKEN.
        </Text>
        <Text style={styles.coordsHint}>
          {stops.length} stops · Route: {routeCoordinates.length} points
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, style]}>
      <MapView
        style={styles.map}
        styleURL={Mapbox?.StyleURL?.Street ?? 'mapbox://styles/mapbox/street-v12'}
      >
        <Camera
          defaultSettings={{
            centerCoordinate: center,
            zoomLevel: 13,
          }}
          centerCoordinate={center}
          zoomLevel={13}
        />
        {/* Route line: ShapeSource + LineLayer (TDD) */}
        {routeCoordinates.length >= 2 && (
          <ShapeSource id="route" shape={routeShape}>
            <LineLayer
              id="route-line"
              style={{
                lineColor: '#6366f1',
                lineWidth: 4,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          </ShapeSource>
        )}
        {/* POIs as PointAnnotation (TDD) */}
        {stops.map((poi, index) => (
          <PointAnnotation
            key={poi.id}
            id={poi.id}
            coordinate={[poi.coordinates.longitude, poi.coordinates.latitude]}
            title={poi.name}
          >
            <View style={styles.marker}>
              <Text style={styles.markerText}>{index + 1}</Text>
            </View>
          </PointAnnotation>
        ))}
      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    minHeight: 240,
  },
  map: {
    flex: 1,
    width: '100%',
  },
  placeholder: {
    flex: 1,
    minHeight: 240,
    backgroundColor: '#1e293b',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  placeholderText: {
    color: '#94a3b8',
    textAlign: 'center',
    fontSize: 14,
  },
  coordsHint: {
    color: '#64748b',
    fontSize: 12,
    marginTop: 8,
  },
  marker: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#6366f1',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#fff',
  },
  markerText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
});
