import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Ionicons } from '@expo/vector-icons';
import React, { useEffect, useRef } from 'react';
import {
    Animated,
    StyleSheet,
    TouchableOpacity,
    View,
} from 'react-native';

type Props = {
    isRecording: boolean;
    onPressIn: () => void;
    onPressOut: () => void;
};

export function MicButton({ isRecording, onPressIn, onPressOut }: Props) {
    const colorScheme = useColorScheme() ?? 'dark';
    const colors = Colors[colorScheme];
    const pulse = useRef(new Animated.Value(1)).current;

    useEffect(() => {
        if (isRecording) {
            Animated.loop(
                Animated.sequence([
                    Animated.timing(pulse, { toValue: 1.4, duration: 600, useNativeDriver: true }),
                    Animated.timing(pulse, { toValue: 1, duration: 600, useNativeDriver: true }),
                ])
            ).start();
        } else {
            pulse.stopAnimation();
            Animated.timing(pulse, { toValue: 1, duration: 200, useNativeDriver: true }).start();
        }
    }, [isRecording, pulse]);

    return (
        <View style={styles.container}>
            {isRecording && (
                <Animated.View
                    style={[
                        styles.pulseRing,
                        {
                            borderColor: colors.danger,
                            transform: [{ scale: pulse }],
                            opacity: pulse.interpolate({ inputRange: [1, 1.4], outputRange: [0.6, 0] }),
                        },
                    ]}
                />
            )}
            <TouchableOpacity
                onPressIn={onPressIn}
                onPressOut={onPressOut}
                activeOpacity={0.8}
                style={[
                    styles.button,
                    {
                        backgroundColor: isRecording ? colors.danger : colors.tint,
                    },
                ]}>
                <Ionicons
                    name={isRecording ? 'stop' : 'mic'}
                    size={22}
                    color="#FFFFFF"
                />
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        width: 48,
        height: 48,
        alignItems: 'center',
        justifyContent: 'center',
    },
    pulseRing: {
        position: 'absolute',
        width: 48,
        height: 48,
        borderRadius: 24,
        borderWidth: 2,
    },
    button: {
        width: 48,
        height: 48,
        borderRadius: 24,
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 4,
        elevation: 4,
    },
});
