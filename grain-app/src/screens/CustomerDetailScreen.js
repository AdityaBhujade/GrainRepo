import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    ActivityIndicator,
    TouchableOpacity,
    StyleSheet,
} from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { getCustomerById } from '../services/api';


export default function CustomerDetailScreen({ route, navigation }) {
    const { customerId } = route.params;
    const [customer, setCustomer] = useState(null);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCustomer = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await getCustomerById(customerId);
            setCustomer(response.data.customer);
            setColumns(response.data.columns);
        } catch (err) {
            setError('Failed to load customer details. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCustomer();
    }, [customerId]);

    useEffect(() => {
        // Try to set a meaningful title from common column names
        if (customer) {
            const name =
                customer['कार्ड धारकांचे नाव'] ||
                customer['owner_name'] ||
                customer['name'] ||
                `Customer #${customerId}`;
            navigation.setOptions({ title: String(name) });
        }
    }, [customer, navigation]);

    const safe = (val) =>
        val !== null && val !== undefined && val !== '' ? String(val) : 'N/A';

    // ─── Loading ─────────────
    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#3B82F6" />
                <Text style={styles.loadingText}>Loading details...</Text>
            </View>
        );
    }

    // ─── Error ───────────────
    if (error) {
        return (
            <View style={styles.centerContainer}>
                <Ionicons name="alert-circle-outline" size={52} color="#EF4444" />
                <Text style={styles.errorTitle}>Something went wrong</Text>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={fetchCustomer}>
                    <Text style={styles.retryButtonText}>Try Again</Text>
                </TouchableOpacity>
            </View>
        );
    }

    if (!customer) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>Customer not found.</Text>
            </View>
        );
    }

    // ─── Dynamic table data from ALL columns ──────────
    // Filter out internal fields (id, row_number) from display
    const skipKeys = new Set(['id', 'row_number']);

    const tableRows = columns
        .filter((colName) => !skipKeys.has(colName))
        .map((colName) => ({
            label: colName,
            value: safe(customer[colName]),
            icon: 'ellipse-outline',
        }));

    // If columns array is empty, fall back to object keys
    const displayRows =
        tableRows.length > 0
            ? tableRows
            : Object.entries(customer)
                .filter(([key]) => !skipKeys.has(key))
                .map(([key, value]) => ({
                    label: key,
                    value: safe(value),
                    icon: 'ellipse-outline',
                }));

    return (
        <ScrollView
            style={styles.container}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
        >
            {/* ─── Customer Information Table ──────────────────── */}
            <View style={styles.tableCard}>
                <View style={styles.tableHeader}>
                    <Ionicons name="document-text-outline" size={16} color="#3B82F6" />
                    <Text style={styles.tableHeaderText}>Customer Information</Text>
                    <View style={styles.badge}>
                        <Text style={styles.badgeText}>{displayRows.length} fields</Text>
                    </View>
                </View>
                <View style={styles.table}>
                    {displayRows.map((row, index) => (
                        <View
                            key={index}
                            style={[
                                styles.tableRow,
                                index % 2 === 0 && styles.tableRowAlt,
                                index === displayRows.length - 1 && styles.tableRowLast,
                            ]}
                        >
                            <View style={styles.labelCell}>
                                <Ionicons
                                    name={row.icon}
                                    size={14}
                                    color="#64748B"
                                    style={styles.rowIcon}
                                />
                                <Text style={styles.labelText} numberOfLines={2}>
                                    {row.label}
                                </Text>
                            </View>
                            <View style={styles.valueCell}>
                                <Text
                                    style={[
                                        styles.valueText,
                                        row.value === 'N/A' && styles.naText,
                                    ]}
                                    numberOfLines={3}
                                >
                                    {row.value}
                                </Text>
                            </View>
                        </View>
                    ))}
                </View>
            </View>
        </ScrollView>
    );
}

// ─── Styles ────────────────────────────────────────────────────
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#F8FAFC',
    },
    scrollContent: {
        padding: 16,
        paddingBottom: 40,
    },

    // ─── Table Card ────────────
    tableCard: {
        backgroundColor: '#FFFFFF',
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: 16,
        borderWidth: 1,
        borderColor: '#E2E8F0',
    },
    tableHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 14,
        borderBottomWidth: 1,
        borderBottomColor: '#E2E8F0',
        backgroundColor: '#F8FAFC',
        gap: 8,
    },
    tableHeaderText: {
        fontSize: 13,
        fontWeight: '700',
        color: '#334155',
        textTransform: 'uppercase',
        letterSpacing: 0.6,
        flex: 1,
    },
    badge: {
        backgroundColor: '#EFF6FF',
        paddingHorizontal: 8,
        paddingVertical: 3,
        borderRadius: 10,
    },
    badgeText: {
        fontSize: 11,
        color: '#3B82F6',
        fontWeight: '600',
    },
    table: {},
    tableRow: {
        flexDirection: 'row',
        borderBottomWidth: 1,
        borderBottomColor: '#F1F5F9',
        minHeight: 46,
    },
    tableRowAlt: {
        backgroundColor: '#FAFBFC',
    },
    tableRowLast: {
        borderBottomWidth: 0,
    },
    labelCell: {
        width: '38%',
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 16,
        borderRightWidth: 1,
        borderRightColor: '#F1F5F9',
    },
    rowIcon: {
        marginRight: 8,
        width: 16,
    },
    labelText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#475569',
        letterSpacing: 0.1,
        flex: 1,
    },
    valueCell: {
        flex: 1,
        paddingVertical: 12,
        paddingHorizontal: 16,
        justifyContent: 'center',
    },
    valueText: {
        fontSize: 13,
        color: '#1E293B',
        fontWeight: '500',
        letterSpacing: 0.1,
    },
    naText: {
        color: '#CBD5E1',
        fontStyle: 'italic',
    },

    // ─── Center / Loading / Error ──
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F8FAFC',
        padding: 32,
    },
    loadingText: {
        marginTop: 14,
        fontSize: 14,
        color: '#64748B',
        fontWeight: '500',
    },
    errorTitle: {
        fontSize: 17,
        fontWeight: '600',
        color: '#1E293B',
        marginTop: 12,
        marginBottom: 6,
    },
    errorText: {
        fontSize: 13,
        color: '#64748B',
        textAlign: 'center',
        lineHeight: 20,
        marginBottom: 20,
    },
    retryButton: {
        backgroundColor: '#3B82F6',
        paddingHorizontal: 28,
        paddingVertical: 11,
        borderRadius: 8,
    },
    retryButtonText: {
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '600',
    },
});
