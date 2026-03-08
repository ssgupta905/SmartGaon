import { Colors, Radius, Spacing } from '@/constants/theme';
import { useAuth } from '@/context/AuthContext';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import {
    Alert,
    Animated,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';

export default function LoginScreen() {
    const colorScheme = useColorScheme() ?? 'dark';
    const colors = Colors[colorScheme];
    const router = useRouter();
    const { login, isLoading } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const fadeAnim = useRef(new Animated.Value(0)).current;
    const slideAnim = useRef(new Animated.Value(40)).current;

    useEffect(() => {
        Animated.parallel([
            Animated.timing(fadeAnim, { toValue: 1, duration: 700, useNativeDriver: true }),
            Animated.timing(slideAnim, { toValue: 0, duration: 700, useNativeDriver: true }),
        ]).start();
    }, [fadeAnim, slideAnim]);

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('Missing Fields', 'Please enter your email and password.');
            return;
        }
        const success = await login(email, password);
        if (success) {
            router.replace('/(tabs)');
        } else {
            Alert.alert('Login Failed', 'Invalid credentials. Password must be at least 6 characters.');
        }
    };

    return (
        <KeyboardAvoidingView
            style={[styles.root, { backgroundColor: colors.background }]}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
            <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
                {/* Logo / Hero */}
                <Animated.View style={[styles.hero, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
                    <View style={[styles.logoCircle, { backgroundColor: colors.tint }]}>
                        <Ionicons name="chatbubbles" size={40} color="#fff" />
                    </View>
                    <Text style={[styles.appName, { color: colors.text }]}>GramSarthiAI</Text>
                    <Text style={[styles.tagline, { color: colors.subtext }]}>
                        Your intelligent assistant in every Indian language
                    </Text>
                </Animated.View>

                {/* Form */}
                <Animated.View style={[styles.form, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
                    <Text style={[styles.formTitle, { color: colors.text }]}>Welcome back</Text>

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
                            placeholder="Password"
                            placeholderTextColor={colors.subtext}
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry={!showPassword}
                        />
                        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                            <Ionicons
                                name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                                size={20}
                                color={colors.subtext}
                            />
                        </TouchableOpacity>
                    </View>

                    <TouchableOpacity
                        style={[styles.loginBtn, { backgroundColor: colors.tint, opacity: isLoading ? 0.7 : 1 }]}
                        onPress={handleLogin}
                        disabled={isLoading}
                        activeOpacity={0.85}>
                        {isLoading ? (
                            <Text style={styles.loginBtnText}>Signing in…</Text>
                        ) : (
                            <>
                                <Text style={styles.loginBtnText}>Sign In</Text>
                                <Ionicons name="arrow-forward" size={18} color="#fff" />
                            </>
                        )}
                    </TouchableOpacity>

                    <View style={styles.divider}>
                        <View style={[styles.dividerLine, { backgroundColor: colors.border }]} />
                        <Text style={[styles.dividerText, { color: colors.subtext }]}>or</Text>
                        <View style={[styles.dividerLine, { backgroundColor: colors.border }]} />
                    </View>

                    <TouchableOpacity
                        style={[styles.googleBtn, { borderColor: colors.border, backgroundColor: colors.card }]}
                        activeOpacity={0.8}>
                        <Ionicons name="logo-google" size={20} color="#EA4335" />
                        <Text style={[styles.googleBtnText, { color: colors.text }]}>Continue with Google</Text>
                    </TouchableOpacity>

                    <View style={styles.signupRow}>
                        <Text style={[styles.signupText, { color: colors.subtext }]}>Don{"'"}t have an account? </Text>
                        <TouchableOpacity onPress={() => router.push('/(auth)/signup')}>
                            <Text style={[styles.signupLink, { color: colors.tint }]}>Sign Up</Text>
                        </TouchableOpacity>
                    </View>
                </Animated.View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1 },
    scroll: { flexGrow: 1, justifyContent: 'center', padding: Spacing.lg },
    hero: { alignItems: 'center', marginBottom: Spacing.xl },
    logoCircle: {
        width: 88, height: 88, borderRadius: 44,
        alignItems: 'center', justifyContent: 'center',
        marginBottom: Spacing.md,
        shadowColor: '#5B6EF5', shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.4, shadowRadius: 20, elevation: 10,
    },
    appName: { fontSize: 32, fontWeight: '800', letterSpacing: -0.5, marginBottom: 6 },
    tagline: { fontSize: 14, textAlign: 'center', lineHeight: 20 },
    form: { gap: Spacing.md },
    formTitle: { fontSize: 22, fontWeight: '700', marginBottom: 4 },
    inputWrapper: {
        flexDirection: 'row', alignItems: 'center',
        borderRadius: Radius.md, borderWidth: 1,
        paddingHorizontal: Spacing.md, height: 52,
    },
    inputIcon: { marginRight: Spacing.sm },
    input: { flex: 1, fontSize: 15 },
    loginBtn: {
        height: 52, borderRadius: Radius.md,
        flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
        shadowColor: '#5B6EF5', shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3, shadowRadius: 8, elevation: 6,
    },
    loginBtnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
    divider: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
    dividerLine: { flex: 1, height: 1 },
    dividerText: { fontSize: 13 },
    googleBtn: {
        height: 52, borderRadius: Radius.md, borderWidth: 1,
        flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
    },
    googleBtnText: { fontSize: 15, fontWeight: '600' },
    signupRow: { flexDirection: 'row', justifyContent: 'center', marginTop: 4 },
    signupText: { fontSize: 14 },
    signupLink: { fontSize: 14, fontWeight: '700' },
});
