/**
 * Itinerary View (TDD Section 5): horizontal pager/tabs for Day 1, Day 2…;
 * split-screen: map top, scrollable list of the day's stops bottom.
 * Fetches walking route geometry from GET /api/v1/routes/{daily_route_id}/geometry when available.
 */
import React, { useState, useMemo, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
} from 'react-native';
import { useItineraryStore } from '../store/itineraryStore';
import { ItineraryMap } from '../components/ItineraryMap';
import { getRouteGeometry } from '../api/client';
import type { DayStops, POIResponse } from '../types/api';

export function ItineraryScreen() {
  const { itinerary, reset } = useItineraryStore();
  const [dayIndex, setDayIndex] = useState(0);
  const [routeGeometry, setRouteGeometry] = useState<[number, number][] | null>(null);

  const days = itinerary?.days_with_stops ?? [];
  const currentDay: DayStops | null = days[dayIndex] ?? null;

  // Fallback: straight line through stops when API geometry isn't used
  const fallbackLineCoordinates = useMemo((): [number, number][] => {
    if (!currentDay?.stops?.length) return [];
    return currentDay.stops.map((s) => [s.coordinates.longitude, s.coordinates.latitude]);
  }, [currentDay]);

  // Fetch walking route geometry for current day (Mapbox Directions API via backend)
  useEffect(() => {
    if (!currentDay?.daily_route_id) {
      setRouteGeometry(null);
      return;
    }
    let cancelled = false;
    setRouteGeometry(null);
    getRouteGeometry(currentDay.daily_route_id)
      .then((res) => {
        if (!cancelled && res.coordinates?.length) setRouteGeometry(res.coordinates);
      })
      .catch(() => {
        if (!cancelled) setRouteGeometry(null);
      });
    return () => { cancelled = true; };
  }, [currentDay?.daily_route_id]);

  const lineCoordinates = routeGeometry ?? fallbackLineCoordinates;

  if (!itinerary) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>No itinerary</Text>
        <TouchableOpacity style={styles.button} onPress={reset}>
          <Text style={styles.buttonText}>Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Day tabs (horizontal pager) */}
      <View style={styles.tabs}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabsContent}>
          {days.map((d, i) => (
            <TouchableOpacity
              key={d.day_number}
              style={[styles.tab, i === dayIndex && styles.tabActive]}
              onPress={() => setDayIndex(i)}
            >
              <Text style={[styles.tabText, i === dayIndex && styles.tabTextActive]}>
                Day {d.day_number}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Map: top half (TDD) */}
      <View style={styles.mapContainer}>
        <ItineraryMap
          stops={currentDay?.stops ?? []}
          routeCoordinates={lineCoordinates}
        />
      </View>

      {/* Scrollable list: bottom half (TDD) */}
      <View style={styles.listContainer}>
        <Text style={styles.listTitle}>Stops</Text>
        <FlatList
          data={currentDay?.stops ?? []}
          keyExtractor={(item) => item.id}
          renderItem={({ item, index }: { item: POIResponse; index: number }) => (
            <View style={styles.stopRow}>
              <View style={styles.stopNumber}>
                <Text style={styles.stopNumberText}>{index + 1}</Text>
              </View>
              <View style={styles.stopContent}>
                <Text style={styles.stopName}>{item.name}</Text>
                <Text style={styles.stopMeta}>
                  {item.category} · {item.estimated_duration_minutes} min
                </Text>
              </View>
            </View>
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>No stops for this day.</Text>
          }
        />
      </View>

      <TouchableOpacity style={styles.backButton} onPress={reset}>
        <Text style={styles.backButtonText}>New itinerary</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0f172a',
  },
  errorText: {
    color: '#94a3b8',
    marginBottom: 16,
  },
  tabs: {
    backgroundColor: '#1e293b',
    paddingVertical: 8,
  },
  tabsContent: {
    paddingHorizontal: 16,
    gap: 8,
    flexDirection: 'row',
  },
  tab: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
  },
  tabActive: {
    backgroundColor: '#6366f1',
  },
  tabText: {
    color: '#94a3b8',
    fontWeight: '600',
    fontSize: 14,
  },
  tabTextActive: {
    color: '#fff',
  },
  mapContainer: {
    height: '45%',
    minHeight: 220,
  },
  listContainer: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 12,
  },
  stopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  stopNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#6366f1',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  stopNumberText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '700',
  },
  stopContent: {
    flex: 1,
  },
  stopName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#f8fafc',
  },
  stopMeta: {
    fontSize: 13,
    color: '#94a3b8',
    marginTop: 2,
  },
  empty: {
    color: '#64748b',
    paddingVertical: 24,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 10,
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
  backButton: {
    position: 'absolute',
    top: 56,
    right: 16,
    backgroundColor: '#334155',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#f8fafc',
    fontSize: 14,
    fontWeight: '600',
  },
});
