import { AuthProvider } from '@/context/AuthContext';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';
import { SafeAreaProvider } from 'react-native-safe-area-context';

function RootNavigator() {
  return (
    <Stack initialRouteName="(tabs)">
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}

export const unstable_settings = {
  anchor: '(auth)',
};

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <AuthProvider>
        <SafeAreaProvider>
          <RootNavigator />
          <StatusBar style="auto" />
        </SafeAreaProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
