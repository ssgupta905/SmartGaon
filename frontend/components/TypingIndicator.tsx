import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View } from 'react-native';

export function TypingIndicator() {
    const colorScheme = useColorScheme() ?? 'dark';
    const colors = Colors[colorScheme];

    const dot1 = useRef(new Animated.Value(0)).current;
    const dot2 = useRef(new Animated.Value(0)).current;
    const dot3 = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        const animate = (dot: Animated.Value, delay: number) =>
            Animated.loop(
                Animated.sequence([
                    Animated.delay(delay),
                    Animated.timing(dot, { toValue: -6, duration: 300, useNativeDriver: true }),
                    Animated.timing(dot, { toValue: 0, duration: 300, useNativeDriver: true }),
                    Animated.delay(600 - delay),
                ])
            );

        const a1 = animate(dot1, 0);
        const a2 = animate(dot2, 200);
        const a3 = animate(dot3, 400);
        a1.start(); a2.start(); a3.start();
        return () => { a1.stop(); a2.stop(); a3.stop(); };
    }, [dot1, dot2, dot3]);

    return (
        <View style={[styles.wrapper, { paddingHorizontal: 12 }]}>
            <View style={[styles.avatar, { backgroundColor: colors.accent }]}>
                <View style={styles.avatarDot} />
            </View>
            <View style={[styles.bubble, { backgroundColor: colors.aiBubble, borderColor: colors.border }]}>
                {[dot1, dot2, dot3].map((dot, i) => (
                    <Animated.View
                        key={i}
                        style={[styles.dot, { backgroundColor: colors.subtext, transform: [{ translateY: dot }] }]}
                    />
                ))}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    wrapper: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        marginVertical: 6,
    },
    avatar: {
        width: 32, height: 32, borderRadius: 16,
        alignItems: 'center', justifyContent: 'center', marginRight: 8,
    },
    avatarDot: {
        width: 8, height: 8, borderRadius: 4, backgroundColor: '#fff',
    },
    bubble: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 14,
        borderRadius: 20,
        borderBottomLeftRadius: 4,
        borderWidth: 1,
        gap: 5,
    },
    dot: {
        width: 7, height: 7, borderRadius: 4,
    },
});
