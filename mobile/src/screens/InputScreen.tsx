/**
 * Input Screen (TDD Section 5): City, Days (slider), Pace (segmented control).
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { useItineraryStore } from '../store/itineraryStore';

const PACE_OPTIONS: Array<'relaxed' | 'moderate' | 'fast'> = ['relaxed', 'moderate', 'fast'];

export function InputScreen() {
  const [city, setCity] = useState('');
  const [days, setDays] = useState(3);
  const [pace, setPace] = useState<'relaxed' | 'moderate' | 'fast'>('moderate');
  const { generate, error, status } = useItineraryStore();

  const handleSubmit = () => {
    const trimmed = city.trim();
    if (!trimmed) {
      Alert.alert('Missing city', 'Please enter a city name.');
      return;
    }
    generate(trimmed, days, pace);
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.card}>
        <Text style={styles.title}>City Break Planner</Text>
        <Text style={styles.subtitle}>Where to? How long? How fast?</Text>

        <Text style={styles.label}>City</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Cluj-Napoca"
          placeholderTextColor="#888"
          value={city}
          onChangeText={setCity}
          autoCapitalize="words"
        />

        <Text style={styles.label}>Days: {days}</Text>
        <View style={styles.daysRow}>
          <TouchableOpacity
            style={styles.dayButton}
            onPress={() => setDays((d) => Math.max(1, d - 1))}
          >
            <Text style={styles.dayButtonText}>−</Text>
          </TouchableOpacity>
          <Text style={styles.daysValue}>{days}</Text>
          <TouchableOpacity
            style={styles.dayButton}
            onPress={() => setDays((d) => Math.min(14, d + 1))}
          >
            <Text style={styles.dayButtonText}>+</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Pace</Text>
        <View style={styles.segmented}>
          {PACE_OPTIONS.map((p) => (
            <TouchableOpacity
              key={p}
              style={[styles.segment, pace === p && styles.segmentActive]}
              onPress={() => setPace(p)}
            >
              <Text style={[styles.segmentText, pace === p && styles.segmentTextActive]}>
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        <TouchableOpacity
          style={[styles.button, status === 'loading' && styles.buttonDisabled]}
          onPress={handleSubmit}
          disabled={status === 'loading'}
        >
          <Text style={styles.buttonText}>Generate itinerary</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 24,
    gap: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#cbd5e1',
    marginTop: 12,
    marginBottom: 4,
  },
  input: {
    backgroundColor: '#334155',
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    color: '#f8fafc',
  },
  daysRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  dayButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#334155',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dayButtonText: {
    fontSize: 22,
    color: '#f8fafc',
    fontWeight: '600',
  },
  daysValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#f8fafc',
    minWidth: 32,
    textAlign: 'center',
  },
  segmented: {
    flexDirection: 'row',
    backgroundColor: '#334155',
    borderRadius: 10,
    padding: 4,
  },
  segment: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  segmentActive: {
    backgroundColor: '#6366f1',
  },
  segmentText: {
    fontSize: 14,
    color: '#94a3b8',
    fontWeight: '600',
  },
  segmentTextActive: {
    color: '#fff',
  },
  error: {
    color: '#f87171',
    fontSize: 14,
    marginTop: 12,
  },
  button: {
    backgroundColor: '#6366f1',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});
