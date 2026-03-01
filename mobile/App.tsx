import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useItineraryStore } from './src/store/itineraryStore';
import { InputScreen } from './src/screens/InputScreen';
import { LoadingScreen } from './src/screens/LoadingScreen';
import { ItineraryScreen } from './src/screens/ItineraryScreen';

export default function App() {
  const { status } = useItineraryStore();

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      {status === 'idle' && <InputScreen />}
      {status === 'loading' && <LoadingScreen />}
      {status === 'ready' && <ItineraryScreen />}
      {status === 'error' && <InputScreen />}
    </SafeAreaProvider>
  );
}
