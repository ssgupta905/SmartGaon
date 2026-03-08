import { Colors, Radius, Spacing } from '@/constants/theme';
import { useAuth } from '@/context/AuthContext';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import React from 'react';
import {
    SafeAreaView, ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from 'react-native';

type SettingRow = {
    icon: string;
    label: string;
    value?: string;
    onPress?: () => void;
    isDestructive?: boolean;
};

export default function ProfileScreen() {
    const colorScheme = useColorScheme() ?? 'dark';
    const colors = Colors[colorScheme];
    const { user, logout } = useAuth();
    const router = useRouter();

    const initials = user?.name
        ? user.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
        : 'U';

    const handleLogout = () => {
        logout();
        router.replace('/(auth)/login');
    };

    const settings: SettingRow[] = [
        { icon: 'language', label: 'Preferred Language', value: 'Auto-detect' },
        { icon: 'mic', label: 'Voice Input', value: 'Enabled' },
        { icon: 'notifications-outline', label: 'Notifications', value: 'On' },
        { icon: 'shield-checkmark-outline', label: 'Privacy & Data' },
        { icon: 'help-circle-outline', label: 'Help & Support' },
        { icon: 'information-circle-outline', label: 'About GramSarthiAI', value: 'v1.0.0' },
    ];

    const SettingItem = ({ icon, label, value, onPress, isDestructive }: SettingRow) => (
        <TouchableOpacity
            style={[styles.settingRow, { borderBottomColor: colors.border }]}
            onPress={onPress}
            activeOpacity={0.7}>
            <View style={[styles.settingIcon, { backgroundColor: isDestructive ? colors.danger + '18' : colors.tint + '18' }]}>
                <Ionicons name={icon as any} size={18} color={isDestructive ? colors.danger : colors.tint} />
            </View>
            <Text style={[styles.settingLabel, { color: isDestructive ? colors.danger : colors.text }]}>{label}</Text>
            <View style={styles.settingRight}>
                {value && <Text style={[styles.settingValue, { color: colors.subtext }]}>{value}</Text>}
                {!isDestructive && <Ionicons name="chevron-forward" size={16} color={colors.subtext} />}
            </View>
        </TouchableOpacity>
    );

    return (
        <SafeAreaView style={[styles.root, { backgroundColor: colors.background }]}>
            <ScrollView showsVerticalScrollIndicator={false}>
                {/* Header */}
                <View style={styles.headerSection}>
                    <Text style={[styles.pageTitle, { color: colors.text }]}>Profile</Text>
                </View>

                {/* Avatar card */}
                <View style={[styles.avatarCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
                    <View style={[styles.avatar, { backgroundColor: colors.tint }]}>
                        <Text style={styles.avatarText}>{initials}</Text>
                    </View>
                    <View style={styles.userInfo}>
                        <Text style={[styles.userName, { color: colors.text }]}>{user?.name ?? 'Guest'}</Text>
                        <Text style={[styles.userEmail, { color: colors.subtext }]}>{user?.email ?? ''}</Text>
                    </View>
                    <TouchableOpacity style={[styles.editBtn, { borderColor: colors.border }]}>
                        <Ionicons name="pencil" size={16} color={colors.tint} />
                    </TouchableOpacity>
                </View>

                {/* Stats */}
                <View style={[styles.statsRow, { backgroundColor: colors.card, borderColor: colors.border }]}>
                    {[
                        { label: 'Chats', value: '24' },
                        { label: 'Messages', value: '312' },
                        { label: 'Languages', value: '4' },
                    ].map((stat, i) => (
                        <React.Fragment key={stat.label}>
                            {i > 0 && <View style={[styles.statDivider, { backgroundColor: colors.border }]} />}
                            <View style={styles.stat}>
                                <Text style={[styles.statValue, { color: colors.text }]}>{stat.value}</Text>
                                <Text style={[styles.statLabel, { color: colors.subtext }]}>{stat.label}</Text>
                            </View>
                        </React.Fragment>
                    ))}
                </View>

                {/* Languages used */}
                <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
                    <Text style={[styles.sectionTitle, { color: colors.subtext }]}>LANGUAGES USED</Text>
                    <View style={styles.langChips}>
                        {['Hindi', 'English', 'Tamil', 'Bengali'].map((lang) => (
                            <View key={lang} style={[styles.langChip, { backgroundColor: colors.tint + '20' }]}>
                                <Ionicons name="language" size={12} color={colors.tint} />
                                <Text style={[styles.langChipText, { color: colors.tint }]}>{lang}</Text>
                            </View>
                        ))}
                    </View>
                </View>

                {/* Settings */}
                <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
                    <Text style={[styles.sectionTitle, { color: colors.subtext }]}>SETTINGS</Text>
                    {settings.map((s) => <SettingItem key={s.label} {...s} />)}
                </View>

                {/* Logout */}
                <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}>
                    <SettingItem icon="log-out-outline" label="Sign Out" onPress={handleLogout} isDestructive />
                </View>

                <Text style={[styles.footerText, { color: colors.subtext }]}>
                    Made with ❤️ for Bharat 🇮🇳
                </Text>
            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1 },
    headerSection: { paddingHorizontal: Spacing.lg, paddingTop: Spacing.md, paddingBottom: Spacing.sm },
    pageTitle: { fontSize: 28, fontWeight: '800' },
    avatarCard: {
        flexDirection: 'row', alignItems: 'center', gap: 14,
        marginHorizontal: Spacing.md, marginVertical: Spacing.sm,
        padding: Spacing.md, borderRadius: Radius.lg, borderWidth: 1,
        shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.06, shadowRadius: 8, elevation: 3,
    },
    avatar: {
        width: 60, height: 60, borderRadius: 30, alignItems: 'center', justifyContent: 'center',
        shadowColor: '#5B6EF5', shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3, shadowRadius: 8, elevation: 4,
    },
    avatarText: { color: '#fff', fontSize: 22, fontWeight: '800' },
    userInfo: { flex: 1 },
    userName: { fontSize: 18, fontWeight: '700' },
    userEmail: { fontSize: 13, marginTop: 2 },
    editBtn: {
        width: 36, height: 36, borderRadius: 18, borderWidth: 1,
        alignItems: 'center', justifyContent: 'center',
    },
    statsRow: {
        flexDirection: 'row', marginHorizontal: Spacing.md, marginBottom: Spacing.sm,
        borderRadius: Radius.lg, borderWidth: 1, overflow: 'hidden',
    },
    stat: { flex: 1, alignItems: 'center', paddingVertical: Spacing.md },
    statValue: { fontSize: 22, fontWeight: '800' },
    statLabel: { fontSize: 12, marginTop: 2 },
    statDivider: { width: 1 },
    section: {
        marginHorizontal: Spacing.md, marginBottom: Spacing.sm,
        borderRadius: Radius.lg, borderWidth: 1, overflow: 'hidden',
        shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05, shadowRadius: 4, elevation: 2,
    },
    sectionTitle: { fontSize: 11, fontWeight: '700', letterSpacing: 1, paddingHorizontal: Spacing.md, paddingTop: Spacing.md, paddingBottom: Spacing.sm },
    settingRow: {
        flexDirection: 'row', alignItems: 'center', gap: 14,
        paddingHorizontal: Spacing.md, paddingVertical: 14,
        borderBottomWidth: StyleSheet.hairlineWidth,
    },
    settingIcon: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
    settingLabel: { flex: 1, fontSize: 15 },
    settingRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
    settingValue: { fontSize: 13 },
    langChips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, paddingHorizontal: Spacing.md, paddingBottom: Spacing.md },
    langChip: { flexDirection: 'row', alignItems: 'center', gap: 5, paddingHorizontal: 12, paddingVertical: 6, borderRadius: Radius.full },
    langChipText: { fontSize: 13, fontWeight: '600' },
    footerText: { textAlign: 'center', fontSize: 13, paddingVertical: Spacing.lg },
});
