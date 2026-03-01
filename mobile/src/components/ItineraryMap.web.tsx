/**
 * Web-only map: avoids loading @rnmapbox/maps (and mapbox-gl.css) in the web bundle.
 * Renders the same placeholder so the app works in the browser.
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { POIResponse } from '../types/api';

export interface ItineraryMapProps {
  stops: POIResponse[];
  routeCoordinates: [number, number][];
  style?: object;
}

export function ItineraryMap({ stops, routeCoordinates, style }: ItineraryMapProps) {
  return (
    <View style={[styles.placeholder, style]}>
      <Text style={styles.placeholderText}>
        Map is available in the iOS and Android app. Use a development build for the full map.
      </Text>
      <Text style={styles.coordsHint}>
        {stops.length} stops · Route: {routeCoordinates.length} points
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
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
});
