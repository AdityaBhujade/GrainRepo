import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const ACCENT_COLORS = {
    'Customer Info': '#4F8EF7',
    'Location Info': '#34C759',
    'Transport Info': '#FF9500',
    'Grain Info': '#AF52DE',
    'Received Grain': '#FF3B30',
};

const ICONS = {
    'Customer Info': '👤',
    'Location Info': '📍',
    'Transport Info': '🚛',
    'Grain Info': '🌾',
    'Received Grain': '📦',
};

export default function InfoCard({ title, data }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const accent = ACCENT_COLORS[title] || '#4F8EF7';
    const icon = ICONS[title] || '📋';

    return (
        <View style={styles.card}>
            {/* Accent strip */}
            <View style={[styles.accentStrip, { backgroundColor: accent }]} />

            <View style={styles.cardInner}>
                {/* Header */}
                <TouchableOpacity 
                    style={styles.headerRow}
                    onPress={() => setIsExpanded(!isExpanded)}
                    activeOpacity={0.7}
                >
                    <Text style={styles.icon}>{icon}</Text>
                    <Text style={[styles.title, { color: accent }]}>{title}</Text>
                    <Text style={[styles.chevron, { color: accent }]}>
                        {isExpanded ? '▲' : '▼'}
                    </Text>
                </TouchableOpacity>

                {isExpanded && (
                    <>
                        <View style={styles.divider} />

                        {/* Data rows */}
                        {data.map((item, index) => (
                            <View
                                key={index}
                                style={[
                                    styles.row,
                                    index < data.length - 1 && styles.rowBorder,
                                ]}
                            >
                                <Text style={styles.label}>{item.label}</Text>
                                <Text style={styles.value}>
                                    {item.value !== null && item.value !== undefined && item.value !== ''
                                        ? String(item.value)
                                        : 'N/A'}
                                </Text>
                            </View>
                        ))}
                    </>
                )}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#FFFFFF',
        borderRadius: 16,
        marginBottom: 16,
        flexDirection: 'row',
        overflow: 'hidden',
        // Shadow
        shadowColor: '#1B2A4A',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.08,
        shadowRadius: 12,
        elevation: 4,
    },
    accentStrip: {
        width: 5,
    },
    cardInner: {
        flex: 1,
        padding: 18,
    },
    headerRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
    },
    icon: {
        fontSize: 18,
        marginRight: 8,
    },
    title: {
        fontSize: 14,
        fontWeight: '800',
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    chevron: {
        fontSize: 12,
        marginLeft: 'auto',
    },
    divider: {
        height: 1,
        backgroundColor: '#F0F2F5',
        marginBottom: 8,
    },
    row: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 10,
    },
    rowBorder: {
        borderBottomWidth: 1,
        borderBottomColor: '#F8F9FA',
    },
    label: {
        fontSize: 14,
        color: '#8492A6',
        fontWeight: '500',
        flex: 1,
    },
    value: {
        fontSize: 14,
        color: '#1B2A4A',
        fontWeight: '700',
        flex: 1,
        textAlign: 'right',
    },
});
