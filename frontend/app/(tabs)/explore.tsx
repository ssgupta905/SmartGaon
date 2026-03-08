import { Colors, Radius, Spacing } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import {
  FlatList,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

type Conversation = {
  id: string;
  title: string;
  preview: string;
  language: string;
  timestamp: string;
  messageCount: number;
};

const MOCK_CONVERSATIONS: Conversation[] = [
  { id: '1', title: 'Weather in Mumbai', preview: 'मुझे आज के मौसम के बारे में बताओ', language: 'Hindi', timestamp: 'Today, 6:45 PM', messageCount: 8 },
  { id: '2', title: 'Indian History Quiz', preview: 'Tell me about the Mughal Empire', language: 'English', timestamp: 'Today, 2:30 PM', messageCount: 15 },
  { id: '3', title: 'Tamil Movie Suggestions', preview: 'நல்ல தமிழ் படங்கள் சொல்லுங்கள்', language: 'Tamil', timestamp: 'Yesterday', messageCount: 6 },
  { id: '4', title: 'Bengali Literature', preview: 'রবীন্দ্রনাথ ঠাকুর সম্পর্কে বলুন', language: 'Bengali', timestamp: 'Yesterday', messageCount: 12 },
  { id: '5', title: 'Recipe Ideas', preview: 'मुझे दाल मखनी की रेसिपी बताओ', language: 'Hindi', timestamp: 'Mon, Mar 2', messageCount: 5 },
  { id: '6', title: 'Travel Tips Goa', preview: 'Best places to visit in Goa', language: 'English', timestamp: 'Sun, Mar 1', messageCount: 10 },
];

const LANG_COLORS: Record<string, string> = {
  Hindi: '#FF6B35',
  English: '#5B6EF5',
  Tamil: '#10B981',
  Bengali: '#F59E0B',
  Telugu: '#EC4899',
  Marathi: '#8B5CF6',
};

export default function HistoryScreen() {
  const colorScheme = useColorScheme() ?? 'dark';
  const colors = Colors[colorScheme];
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = MOCK_CONVERSATIONS.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.preview.includes(searchQuery)
  );

  return (
    <SafeAreaView style={[styles.root, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { borderBottomColor: colors.border }]}>
        <Text style={[styles.title, { color: colors.text }]}>History</Text>
        <Text style={[styles.subtitle, { color: colors.subtext }]}>{MOCK_CONVERSATIONS.length} conversations</Text>
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          <View style={[styles.searchBar, { backgroundColor: colors.inputBg, borderColor: colors.border }]}>
            <Ionicons name="search" size={18} color={colors.subtext} />
            <TextInput
              style={[styles.searchInput, { color: colors.text }]}
              placeholder="Search conversations…"
              placeholderTextColor={colors.subtext}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}
            activeOpacity={0.75}>
            <View style={styles.cardLeft}>
              <View style={[styles.iconCircle, { backgroundColor: (LANG_COLORS[item.language] ?? colors.tint) + '22' }]}>
                <Ionicons name="chatbubble-ellipses" size={20} color={LANG_COLORS[item.language] ?? colors.tint} />
              </View>
            </View>
            <View style={styles.cardBody}>
              <View style={styles.cardTop}>
                <Text style={[styles.cardTitle, { color: colors.text }]} numberOfLines={1}>{item.title}</Text>
                <Text style={[styles.cardTime, { color: colors.subtext }]}>{item.timestamp}</Text>
              </View>
              <Text style={[styles.cardPreview, { color: colors.subtext }]} numberOfLines={1}>{item.preview}</Text>
              <View style={styles.cardBottom}>
                <View style={[styles.langTag, { backgroundColor: (LANG_COLORS[item.language] ?? colors.tint) + '20' }]}>
                  <Text style={[styles.langTagText, { color: LANG_COLORS[item.language] ?? colors.tint }]}>{item.language}</Text>
                </View>
                <Text style={[styles.msgCount, { color: colors.subtext }]}>
                  <Ionicons name="chatbubble-outline" size={11} /> {item.messageCount} messages
                </Text>
              </View>
            </View>
            <Ionicons name="chevron-forward" size={16} color={colors.subtext} />
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="chatbubbles-outline" size={52} color={colors.border} />
            <Text style={[styles.emptyText, { color: colors.subtext }]}>No conversations yet</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: { paddingHorizontal: Spacing.lg, paddingTop: Spacing.md, paddingBottom: Spacing.md, borderBottomWidth: 1 },
  title: { fontSize: 28, fontWeight: '800' },
  subtitle: { fontSize: 13, marginTop: 2 },
  list: { padding: Spacing.md, gap: Spacing.sm },
  searchBar: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    borderRadius: Radius.md, borderWidth: 1,
    paddingHorizontal: Spacing.md, height: 44, marginBottom: Spacing.sm,
  },
  searchInput: { flex: 1, fontSize: 14, height: '100%' },
  card: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    borderRadius: Radius.md, borderWidth: 1,
    padding: Spacing.md,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06, shadowRadius: 4, elevation: 2,
  },
  cardLeft: {},
  iconCircle: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  cardBody: { flex: 1, gap: 4 },
  cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: 15, fontWeight: '700', flex: 1 },
  cardTime: { fontSize: 11 },
  cardPreview: { fontSize: 13 },
  cardBottom: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 2 },
  langTag: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: Radius.full },
  langTagText: { fontSize: 11, fontWeight: '700' },
  msgCount: { fontSize: 11 },
  empty: { alignItems: 'center', marginTop: 60, gap: 12 },
  emptyText: { fontSize: 15 },
});
