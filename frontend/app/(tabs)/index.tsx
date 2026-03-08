import { ChatBubble, Message } from '@/components/ChatBubble';
import { MicButton } from '@/components/MicButton';
import { TypingIndicator } from '@/components/TypingIndicator';
import { Colors, Radius, Spacing } from '@/constants/theme';
import { useAuth } from '@/context/AuthContext';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import React, { useCallback, useRef, useState } from 'react';
import {
  FlatList, KeyboardAvoidingView, Platform,
  StyleSheet,
  Text, TextInput, TouchableOpacity,
  View
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { transcribeAudio } from '@/services/sarvamService';
import { Audio } from 'expo-av';

const LANGUAGES = ['Auto', 'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati', 'English'];

const AI_RESPONSES = [
  "नमस्ते! मैं GramSarthiAI हूँ। मैं आपकी कैसे मदद कर सकता हूँ? 🙏",
  "I can understand and respond in Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, and many more Indian languages!",
  "यह एक बहुत अच्छा सवाल है। मुझे बताइए कि आप किस विषय में जानकारी चाहते हैं।",
  "That's interesting! As your multilingual AI assistant, I'm here to help you with anything you need.",
  "आप मुझसे किसी भी भारतीय भाषा में बात कर सकते हैं — मैं सब समझता हूँ! 😊",
];

let msgId = 1;

export default function ChatScreen() {
  const colorScheme = useColorScheme() ?? 'dark';
  const colors = Colors[colorScheme];
  const insets = useSafeAreaInsets();
  const { user } = useAuth();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: String(msgId++),
      role: 'assistant',
      content: `नमस्ते ${user?.name?.split(' ')[0] ?? ''}! 🙏 I'm GramSarthiAI — your intelligent assistant in every Indian language. Ask me anything! आप हिंदी, बங்காली, तमिल, या किसी भी भाषा में बात कर सकते हैं।`,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  const [selectedLang, setSelectedLang] = useState('Auto');
  const [showLangPicker, setShowLangPicker] = useState(false);

  const flatListRef = useRef<FlatList>(null);
  const inputRef = useRef<TextInput>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);
  const isPreparingRef = useRef(false);
  const isPressedRef = useRef(false);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;
    setInputText('');

    const userMsg: Message = {
      id: String(msgId++),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);

    // Simulate API delay
    await new Promise((r) => setTimeout(r, 1500 + Math.random() * 1000));

    const aiMsg: Message = {
      id: String(msgId++),
      role: 'assistant',
      content: AI_RESPONSES[Math.floor(Math.random() * AI_RESPONSES.length)],
      timestamp: new Date(),
    };

    setIsTyping(false);
    setMessages((prev) => [...prev, aiMsg]);
    setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
  }, []);

  const handleMicPressIn = async () => {
    if (isPreparingRef.current || recordingRef.current) return;
    isPressedRef.current = true;

    try {
      if (permissionResponse?.status !== 'granted') {
        const resp = await requestPermission();
        if (resp.status !== 'granted') {
          isPressedRef.current = false;
          return;
        }
      }

      isPreparingRef.current = true;
      setIsRecording(true);

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      recordingRef.current = recording;
      isPreparingRef.current = false;

      // If user already released while we were preparing
      if (!isPressedRef.current) {
        console.log('User released before recording was ready, cleaning up...');
        stopAndCleanupRecording();
      }
    } catch (err) {
      isPreparingRef.current = false;
      setIsRecording(false);
      isPressedRef.current = false;
      console.error('Failed to start recording', err);
    }
  };

  const stopAndCleanupRecording = async () => {
    const rec = recordingRef.current;
    recordingRef.current = null;
    if (rec) {
      try {
        await rec.stopAndUnloadAsync();
      } catch (e) {
        console.warn('Silent failure on stopAndUnload:', e);
      }
    }
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
    setIsRecording(false);
  };

  const handleMicPressOut = async () => {
    isPressedRef.current = false;
    setIsRecording(false);

    // Wait if it's still preparing
    if (isPreparingRef.current) {
      return; // handleMicPressIn will catch the release via isPressedRef
    }

    const rec = recordingRef.current;
    if (!rec) return;

    recordingRef.current = null;
    console.log('Stopping recording..');

    try {
      setIsTranscribing(true);

      // Check if recording is actually prepared/recording
      const status = await rec.getStatusAsync();
      if (!status.canRecord || status.durationMillis < 200) {
        console.warn('Recording too short or not ready');
        await rec.stopAndUnloadAsync();
        setIsTranscribing(false);
        return;
      }

      await rec.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({ allowsRecordingIOS: false });

      const uri = rec.getURI();
      console.log('Recording stopped and stored at', uri);

      if (uri) {
        const result = await transcribeAudio(uri);
        setIsTranscribing(false);

        if (result?.transcript) {
          sendMessage(result.transcript);
        } else {
          const errorMsg = !process.env.EXPO_PUBLIC_SARVAM_API_KEY
            ? 'API Key Missing in .env (Check EXPO_PUBLIC_SARVAM_API_KEY)'
            : 'Sarvam API Error (Check API logs)';
          console.warn('Transcription failed:', errorMsg);
          sendMessage(`[Error] ${errorMsg}`);
        }
      }
    } catch (err: any) {
      setIsTranscribing(false);
      console.error('Failed to stop recording', err);
      if (err.message?.includes('no valid audio data')) {
        sendMessage('[Error] Recording was too short. Please hold the button longer.');
      }
    }
  };



  return (
    <View style={[styles.root, { backgroundColor: colors.background }]}>
      {/* Header */}
      <View style={[
        styles.header,
        {
          borderBottomColor: colors.border,
          backgroundColor: colors.background,
          paddingTop: insets.top + (Platform.OS === 'ios' ? 0 : 10),
        }
      ]}>
        <View style={styles.headerLeft}>
          <View style={[styles.aiBadge, { backgroundColor: colors.tint }]}>
            <Ionicons name="chatbubbles" size={18} color="#fff" />
          </View>
          <View>
            <Text style={[styles.headerTitle, { color: colors.text }]}>GramSarthiAI</Text>
            <View style={styles.onlineRow}>
              <View style={[styles.onlineDot, { backgroundColor: colors.success }]} />
              <Text style={[styles.headerSub, { color: colors.subtext }]}>Online · Multilingual</Text>
            </View>
          </View>
        </View>

        {/* Language selector */}
        <TouchableOpacity
          style={[styles.langBtn, { backgroundColor: colors.inputBg, borderColor: colors.border }]}
          onPress={() => setShowLangPicker(!showLangPicker)}>
          <Ionicons name="language" size={14} color={colors.tint} />
          <Text style={[styles.langBtnText, { color: colors.tint }]}>{selectedLang}</Text>
          <Ionicons name="chevron-down" size={12} color={colors.tint} />
        </TouchableOpacity>
      </View>

      {/* Language picker dropdown */}
      {showLangPicker && (
        <View style={[styles.langDropdown, { backgroundColor: colors.card, borderColor: colors.border }]}>
          {LANGUAGES.map((lang) => (
            <TouchableOpacity
              key={lang}
              style={[styles.langOption, selectedLang === lang && { backgroundColor: colors.tint + '22' }]}
              onPress={() => { setSelectedLang(lang); setShowLangPicker(false); }}>
              <Text style={[styles.langOptionText, { color: selectedLang === lang ? colors.tint : colors.text }]}>
                {lang}
              </Text>
              {selectedLang === lang && <Ionicons name="checkmark" size={14} color={colors.tint} />}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Messages */}
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={90}>
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <ChatBubble message={item} />}
          ListFooterComponent={isTyping ? <TypingIndicator /> : null}
          contentContainerStyle={[styles.messagesList, { paddingBottom: Spacing.md }]}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          showsVerticalScrollIndicator={false}
        />

        {/* Input Bar */}
        <View style={[
          styles.inputBar,
          {
            backgroundColor: colors.background,
            borderTopColor: colors.border,
            paddingBottom: Math.max(insets.bottom, Spacing.md),
          }
        ]}>
          {isRecording ? (
            <View style={[styles.recordingBar, { backgroundColor: colors.danger + '18', borderColor: colors.danger }]}>
              <View style={[styles.recordingDot, { backgroundColor: colors.danger }]} />
              <Text style={[styles.recordingText, { color: colors.danger }]}>
                Listening… Release to send
              </Text>
            </View>
          ) : isTranscribing ? (
            <View style={[styles.recordingBar, { backgroundColor: colors.tint + '18', borderColor: colors.tint }]}>
              <View style={[styles.recordingDot, { backgroundColor: colors.tint }]} />
              <Text style={[styles.recordingText, { color: colors.tint }]}>
                Transcribing Audio...
              </Text>
            </View>
          ) : (
            <View style={[styles.textInputWrapper, { backgroundColor: colors.inputBg, borderColor: colors.border }]}>
              <TextInput
                ref={inputRef}
                style={[styles.textInput, { color: colors.text }]}
                placeholder="Message GramSarthiAI…"
                placeholderTextColor={colors.subtext}
                value={inputText}
                onChangeText={setInputText}
                multiline
                maxLength={2000}
                onSubmitEditing={() => sendMessage(inputText)}
              />
              {inputText.trim().length > 0 && (
                <TouchableOpacity
                  style={[styles.sendBtn, { backgroundColor: colors.tint }]}
                  onPress={() => sendMessage(inputText)}>
                  <Ionicons name="send" size={16} color="#fff" />
                </TouchableOpacity>
              )}
            </View>
          )}
          <MicButton
            isRecording={isRecording}
            onPressIn={handleMicPressIn}
            onPressOut={handleMicPressOut}
          />
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm + 4,
    borderBottomWidth: 1,
  },
  headerLeft: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  aiBadge: {
    width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center',
  },
  headerTitle: { fontSize: 17, fontWeight: '700' },
  onlineRow: { flexDirection: 'row', alignItems: 'center', gap: 5, marginTop: 2 },
  onlineDot: { width: 6, height: 6, borderRadius: 3 },
  headerSub: { fontSize: 12 },
  langBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 10, paddingVertical: 6,
    borderRadius: Radius.full, borderWidth: 1,
  },
  langBtnText: { fontSize: 12, fontWeight: '600' },
  langDropdown: {
    position: 'absolute', top: 72, right: Spacing.md, zIndex: 100,
    borderRadius: Radius.md, borderWidth: 1,
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2, shadowRadius: 8, elevation: 8,
    overflow: 'hidden', minWidth: 140,
  },
  langOption: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 16, paddingVertical: 10,
  },
  langOptionText: { fontSize: 14 },
  messagesList: { paddingTop: Spacing.md, paddingBottom: Spacing.md },
  inputBar: {
    flexDirection: 'row', alignItems: 'flex-end', gap: Spacing.sm,
    paddingHorizontal: Spacing.md, paddingVertical: Spacing.sm + 2,
    borderTopWidth: 1,
  },
  textInputWrapper: {
    flex: 1, flexDirection: 'row', alignItems: 'flex-end',
    borderRadius: Radius.xl, borderWidth: 1,
    paddingHorizontal: 14, paddingVertical: 8, minHeight: 48, maxHeight: 120,
  },
  textInput: { flex: 1, fontSize: 15, paddingTop: 2, paddingBottom: 2 },
  sendBtn: {
    width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center', marginLeft: 8,
  },
  recordingBar: {
    flex: 1, height: 48, borderRadius: Radius.xl, borderWidth: 1,
    flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, gap: 10,
  },
  recordingDot: { width: 8, height: 8, borderRadius: 4 },
  recordingText: { fontSize: 14, fontWeight: '500' },
});
