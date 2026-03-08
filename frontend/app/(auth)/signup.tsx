import { Colors, Radius, Spacing } from '@/constants/theme';
import { useAuth } from '@/context/AuthContext';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import {
    Alert,
    Animated,
    Image,
    KeyboardAvoidingView, Platform,
    ScrollView,
    StyleSheet,
    Text, TextInput, TouchableOpacity,
    View,
} from 'react-native';

type DocType = 'aadhar' | 'pan';

export default function SignupScreen() {
    const colorScheme = useColorScheme() ?? 'dark';
    const colors = Colors[colorScheme];
    const router = useRouter();
    const { signup, isLoading } = useAuth();

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [aadharUri, setAadharUri] = useState<string | null>(null);
    const [panUri, setPanUri] = useState<string | null>(null);

    const fadeAnim = useRef(new Animated.Value(0)).current;
    const slideAnim = useRef(new Animated.Value(40)).current;

    useEffect(() => {
        Animated.parallel([
            Animated.timing(fadeAnim, { toValue: 1, duration: 700, useNativeDriver: true }),
            Animated.timing(slideAnim, { toValue: 0, duration: 700, useNativeDriver: true }),
        ]).start();
    }, [fadeAnim, slideAnim]);

    const pickDocument = async (type: DocType) => {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
            Alert.alert('Permission required', 'Please allow access to your photo library.');
            return;
        }
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: true,
            quality: 0.8,
        });
        if (!result.canceled && result.assets[0]) {
            if (type === 'aadhar') setAadharUri(result.assets[0].uri);
            else setPanUri(result.assets[0].uri);
        }
    };

    const handleSignup = async () => {
        if (!name || !email || !password) {
            Alert.alert('Missing Fields', 'Please fill all required fields.');
            return;
        }
        if (password.length < 6) {
            Alert.alert('Weak Password', 'Password must be at least 6 characters.');
            return;
        }
        const success = await signup(name, email, password);
        if (success) {
            router.replace('/(tabs)');
        } else {
            Alert.alert('Signup Failed', 'Something went wrong. Please try again.');
        }
    };

    const DocUploadCard = ({
        label, icon, uri, type,
    }: { label: string; icon: string; uri: string | null; type: DocType }) => (
        <TouchableOpacity
            style={[
                styles.docCard,
                {
                    backgroundColor: colors.card,
                    borderColor: uri ? colors.success : colors.border,
                    borderStyle: uri ? 'solid' : 'dashed',
                },
            ]}
            onPress={() => pickDocument(type)}
            activeOpacity={0.8}>
            {uri ? (
                <>
                    <Image source={{ uri }} style={styles.docPreview} resizeMode="cover" />
                    <View style={styles.docOverlay}>
                        <View style={[styles.checkBadge, { backgroundColor: colors.success }]}>
                            <Ionicons name="checkmark" size={14} color="#fff" />
                        </View>
                        <Text style={[styles.docLabel, { color: '#fff' }]}>{label}</Text>
                    </View>
                </>
            ) : (
                <>
                    <View style={[styles.docIconCircle, { backgroundColor: colors.inputBg }]}>
                        <Ionicons name={icon as any} size={28} color={colors.tint} />
                    </View>
                    <Text style={[styles.docLabel, { color: colors.text }]}>{label}</Text>
                    <Text style={[styles.docSub, { color: colors.subtext }]}>Tap to upload</Text>
                </>
            )}
        </TouchableOpacity>
    );

    return (
        <KeyboardAvoidingView
            style={[styles.root, { backgroundColor: colors.background }]}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
            <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
                {/* Back */}
                <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
                    <Ionicons name="arrow-back" size={22} color={colors.text} />
                </TouchableOpacity>

                <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }] }}>
                    <View style={styles.header}>
                        <View style={[styles.logoCircle, { backgroundColor: colors.accent }]}>
                            <Ionicons name="person-add" size={32} color="#fff" />
                        </View>
                        <Text style={[styles.title, { color: colors.text }]}>Create Account</Text>
                        <Text style={[styles.subtitle, { color: colors.subtext }]}>
                            Join GramSarthiAI — your multilingual AI companion
                        </Text>
                    </View>

                    <View style={styles.form}>
                        {/* Name */}
                        <View style={[styles.inputWrapper, { backgroundColor: colors.inputBg, borderColor: colors.border }]}>
                            <Ionicons name="person-outline" size={20} color={colors.subtext} style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, { color: colors.text }]}
                                placeholder="Full name"
                                placeholderTextColor={colors.subtext}
                                value={name}
                                onChangeText={setName}
                            />
                        </View>

                        {/* Email */}
                        <View style={[styles.inputWrapper, { backgroundColor: colors.inputBg, borderColor: colors.border }]}>
                            <Ionicons name="mail-outline" size={20} color={colors.subtext} style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, { color: colors.text }]}
                                placeholder="Email address"
                                placeholderTextColor={colors.subtext}
                                value={email}
                                onChangeText={setEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                                autoCorrect={false}
                            />
                        </View>

                        {/* Password */}
                        <View style={[styles.inputWrapper, { backgroundColor: colors.inputBg, borderColor: colors.border }]}>
                            <Ionicons name="lock-closed-outline" size={20} color={colors.subtext} style={styles.inputIcon} />
                            <TextInput
                                style={[styles.input, { color: colors.text }]}
                                placeholder="Password (min. 6 characters)"
                                placeholderTextColor={colors.subtext}
                                value={password}
                                onChangeText={setPassword}
                                secureTextEntry={!showPassword}
                            />
                            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={20} color={colors.subtext} />
                            </TouchableOpacity>
                        </View>

                        {/* Document Upload */}
                        <Text style={[styles.sectionLabel, { color: colors.text }]}>
                            KYC Documents <Text style={{ color: colors.subtext, fontWeight: '400', fontSize: 13 }}>(optional)</Text>
                        </Text>
                        <View style={styles.docRow}>
                            <DocUploadCard label="Aadhar Card" icon="card-outline" uri={aadharUri} type="aadhar" />
                            <DocUploadCard label="PAN Card" icon="document-text-outline" uri={panUri} type="pan" />
                        </View>

                        {/* Submit */}
                        <TouchableOpacity
                            style={[styles.signupBtn, { backgroundColor: colors.accent, opacity: isLoading ? 0.7 : 1 }]}
                            onPress={handleSignup}
                            disabled={isLoading}
                            activeOpacity={0.85}>
                            {isLoading ? (
                                <Text style={styles.signupBtnText}>Creating account…</Text>
                            ) : (
                                <>
                                    <Text style={styles.signupBtnText}>Create Account</Text>
                                    <Ionicons name="arrow-forward" size={18} color="#fff" />
                                </>
                            )}
                        </TouchableOpacity>

                        <View style={styles.loginRow}>
                            <Text style={[styles.loginText, { color: colors.subtext }]}>Already have an account? </Text>
                            <TouchableOpacity onPress={() => router.back()}>
                                <Text style={[styles.loginLink, { color: colors.tint }]}>Sign In</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Animated.View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1 },
    scroll: { flexGrow: 1, padding: Spacing.lg, paddingTop: 60 },
    backBtn: { marginBottom: Spacing.md },
    header: { alignItems: 'center', marginBottom: Spacing.xl },
    logoCircle: {
        width: 72, height: 72, borderRadius: 36, alignItems: 'center', justifyContent: 'center',
        marginBottom: Spacing.md,
        shadowColor: '#7C3AED', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.35, shadowRadius: 16, elevation: 8,
    },
    title: { fontSize: 26, fontWeight: '800', marginBottom: 6 },
    subtitle: { fontSize: 14, textAlign: 'center' },
    form: { gap: Spacing.md },
    inputWrapper: {
        flexDirection: 'row', alignItems: 'center',
        borderRadius: Radius.md, borderWidth: 1,
        paddingHorizontal: Spacing.md, height: 52,
    },
    inputIcon: { marginRight: Spacing.sm },
    input: { flex: 1, fontSize: 15 },
    sectionLabel: { fontSize: 15, fontWeight: '700', marginTop: 4 },
    docRow: { flexDirection: 'row', gap: Spacing.md },
    docCard: {
        flex: 1, height: 120, borderRadius: Radius.md, borderWidth: 2,
        alignItems: 'center', justifyContent: 'center', overflow: 'hidden',
    },
    docPreview: { width: '100%', height: '100%', position: 'absolute' },
    docOverlay: {
        ...StyleSheet.absoluteFillObject,
        backgroundColor: 'rgba(0,0,0,0.4)',
        alignItems: 'center', justifyContent: 'center', gap: 6,
    },
    checkBadge: {
        width: 28, height: 28, borderRadius: 14, alignItems: 'center', justifyContent: 'center',
    },
    docIconCircle: {
        width: 52, height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center', marginBottom: 8,
    },
    docLabel: { fontSize: 13, fontWeight: '700' },
    docSub: { fontSize: 11, marginTop: 2 },
    signupBtn: {
        height: 52, borderRadius: Radius.md,
        flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
        shadowColor: '#7C3AED', shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3, shadowRadius: 8, elevation: 6,
        marginTop: 4,
    },
    signupBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
    loginRow: { flexDirection: 'row', justifyContent: 'center' },
    loginText: { fontSize: 14 },
    loginLink: { fontSize: 14, fontWeight: '700' },
});
