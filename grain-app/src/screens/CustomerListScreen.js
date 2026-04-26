import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    ActivityIndicator,
    StyleSheet,
    RefreshControl,
    TextInput,
    Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { getCustomers } from '../services/api';


const FILTERS = [
    { key: 'rcid', label: 'R-CID', icon: 'id-card-outline', placeholder: 'Search by R-CID...' },
    { key: 'mobile_number', label: 'Mobile No.', icon: 'call-outline', placeholder: 'Search by mobile number...' },
    { key: 'all', label: 'All', icon: 'search-outline', placeholder: 'Search all columns...' },
];

const PAGE_SIZE = 100;

export default function CustomerListScreen({ navigation }) {
    const [customers, setCustomers] = useState([]);
    const [filteredCustomers, setFilteredCustomers] = useState([]);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);

    // ─── Pagination state ─────────────────────
    const [page, setPage] = useState(1);
    const [totalCustomers, setTotalCustomers] = useState(0);
    const [loadingMore, setLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);

    // ─── Search state ────────────────────────
    const [activeFilters, setActiveFilters] = useState(['rcid']);
    const [inputText, setInputText] = useState('');
    const [debouncedQuery, setDebouncedQuery] = useState('');
    const debounceTimer = useRef(null);

    const handleSearchChange = useCallback((text) => {
        setInputText(text);
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
        debounceTimer.current = setTimeout(() => setDebouncedQuery(text), 400);
    }, []);

    const handleClearSearch = useCallback(() => {
        setInputText('');
        setDebouncedQuery('');
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
    }, []);

    // Toggle filter on/off — at least one must stay active
    const handleFilterToggle = useCallback((filterKey) => {
        setActiveFilters((prev) => {
            if (prev.includes(filterKey)) {
                if (prev.length === 1) return prev;
                return prev.filter((k) => k !== filterKey);
            }
            return [...prev, filterKey];
        });
    }, []);

    useEffect(() => () => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
    }, []);

    // ─── Helper: get display value from a customer ────────
    const getFieldValue = useCallback((customer, fieldName) => {
        // For API data: customer is the whole object from data[]
        // For mock data: customer.data holds the column values
        const data = customer.data || customer;
        if (!data) return null;

        // Search by various possible field names
        if (typeof data === 'object') {
            // Direct key match
            if (data[fieldName] !== undefined) return data[fieldName];

            // Search all values for common names
            for (const [key, val] of Object.entries(data)) {
                const keyLower = key.toLowerCase();
                if (fieldName === 'name' && (
                    keyLower.includes('नाव') ||
                    keyLower.includes('name') ||
                    keyLower.includes('कार्ड धारकांचे')
                )) {
                    return val;
                }
                if (fieldName === 'rcid' && (
                    keyLower.includes('r cid') ||
                    keyLower.includes('rcid') ||
                    keyLower.includes('r_cid')
                )) {
                    return val;
                }
                if (fieldName === 'mobile_number' && (
                    keyLower.includes('mobile') ||
                    keyLower.includes('phone') ||
                    keyLower.includes('मोबाईल') ||
                    keyLower.includes('फोन') ||
                    keyLower.includes('mob') ||
                    keyLower.includes('contact') ||
                    keyLower === 'column 20'
                )) {
                    return val;
                }
            }
        }
        return null;
    }, []);

    // ─── Fetch ───────────────────────────────
    const fetchCustomers = useCallback(async (isRefresh = false) => {
        try {
            if (isRefresh) setRefreshing(true);
            else setLoading(true);
            setError(null);
            const response = await getCustomers({ page: 1, page_size: PAGE_SIZE });
            const newData = response.data.data || response.data;
            setCustomers(newData);
            setColumns(response.data.columns || []);
            setFilteredCustomers(newData);
            setTotalCustomers(response.data.total || newData.length);
            setPage(1);
            setHasMore(newData.length < (response.data.total || 0));
        } catch (err) {
            setError('Failed to load customers. Make sure the backend is running.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    const loadMore = useCallback(async () => {
        if (loadingMore || !hasMore || debouncedQuery.trim()) return;
        setLoadingMore(true);
        try {
            const nextPage = page + 1;
            const response = await getCustomers({ page: nextPage, page_size: PAGE_SIZE });
            const newData = response.data.data || response.data;
            if (newData.length === 0) {
                setHasMore(false);
            } else {
                setCustomers((prev) => [...prev, ...newData]);
                setPage(nextPage);
                setHasMore(nextPage * PAGE_SIZE < (response.data.total || 0));
            }
        } catch (err) {
            // Silently fail — user can still scroll
        } finally {
            setLoadingMore(false);
        }
    }, [page, loadingMore, hasMore, debouncedQuery]);

    useFocusEffect(
        useCallback(() => {
            fetchCustomers(true);
        }, [fetchCustomers])
    );

    // ─── Filter logic ────────────────────────
    useEffect(() => {
        if (!debouncedQuery.trim()) {
            setFilteredCustomers(customers);
            return;
        }

        const q = debouncedQuery.toLowerCase().trim();

        setFilteredCustomers(
            customers.filter((c) => {
                if (activeFilters.includes('all')) {
                    // Search across all column values
                    return Object.values(c).some(
                        (v) => v && String(v).toLowerCase().includes(q)
                    );
                }

                return activeFilters.some((key) => {
                    if (key === 'rcid') {
                        const rcid = getFieldValue(c, 'rcid');
                        return rcid && String(rcid).toLowerCase().includes(q);
                    }
                    if (key === 'mobile_number') {
                        const mobile = getFieldValue(c, 'mobile_number');
                        return mobile && String(mobile).toLowerCase().includes(q);
                    }
                    return false;
                });
            })
        );
    }, [debouncedQuery, customers, activeFilters, getFieldValue]);

    const handlePress = (customer) => {
        navigation.navigate('CustomerDetail', { customerId: customer.row_number });
    };

    const getInitials = (name) => {
        if (!name) return '?';
        const nameStr = String(name).trim();
        if (!nameStr) return '?';
        const parts = nameStr.split(/\s+/).filter(Boolean);
        if (parts.length === 0) return '?';
        const first = parts[0][0] || '?';
        const second = parts.length >= 2 ? (parts[1][0] || '') : '';
        return (first + second).toUpperCase() || '?';
    };

    const COLORS = ['#2563EB', '#059669', '#D97706', '#7C3AED', '#DC2626', '#0891B2', '#4F46E5', '#DB2777'];
    const getColor = (id) => COLORS[(id || 0) % COLORS.length];

    // Build dynamic placeholder from active filters
    const activeLabelList = FILTERS.filter((f) => activeFilters.includes(f.key)).map((f) => f.label.toLowerCase());
    const searchPlaceholder = `Search by ${activeLabelList.join(', ')}...`;

    // ─── Render ───────────────────────────────
    const renderItem = ({ item }) => {
        const name = getFieldValue(item, 'name') || 'N/A';
        const rcid = getFieldValue(item, 'rcid');
        const mobile = getFieldValue(item, 'mobile_number');

        return (
            <TouchableOpacity style={styles.card} activeOpacity={0.6} onPress={() => handlePress(item)}>
                <View style={[styles.cardAccent, { backgroundColor: getColor(item.id) }]} />
                <View style={[styles.avatar, { backgroundColor: getColor(item.id) }]}>
                    <Text style={styles.avatarText}>{getInitials(name)}</Text>
                </View>
                <View style={styles.cardBody}>
                    <Text style={styles.ownerName} numberOfLines={1}>{String(name)}</Text>
                    <Text style={styles.shopName} numberOfLines={1}>
                        Row {item.row_number || '—'}
                    </Text>
                    <View style={styles.metaRow}>
                        {rcid && (
                            <View style={[styles.metaBadge, styles.metaBadgeId]}>
                                <Ionicons name="id-card-outline" size={10} color="#7C3AED" />
                                <Text style={[styles.metaText, { color: '#7C3AED' }]}>{rcid}</Text>
                            </View>
                        )}
                        {mobile && (
                            <View style={[styles.metaBadge, styles.metaBadgeMobile]}>
                                <Ionicons name="call-outline" size={10} color="#059669" />
                                <Text style={[styles.metaText, { color: '#059669' }]}>{mobile}</Text>
                            </View>
                        )}
                    </View>
                </View>
                <Ionicons name="chevron-forward" size={16} color="#D1D5DB" />
            </TouchableOpacity>
        );
    };

    const renderEmpty = () => (
        <View style={styles.emptyContainer}>
            <View style={styles.emptyCard}>
                <Ionicons name="search-outline" size={64} color="#D1D5DB" />
                <Text style={styles.emptyTitle}>Customer Not Found</Text>
                <Text style={styles.emptySubtitle}>
                    {inputText
                        ? `No results for "${inputText}"`
                        : 'No customers available. Pull down to refresh.'}
                </Text>
                {inputText.length > 0 && (
                    <TouchableOpacity style={styles.clearBtn} onPress={handleClearSearch}>
                        <Ionicons name="refresh-outline" size={14} color="#2563EB" />
                        <Text style={styles.clearBtnText}>Clear Search</Text>
                    </TouchableOpacity>
                )}
            </View>
        </View>
    );

    if (loading) {
        return (
            <View style={styles.center}>
                <ActivityIndicator size="large" color="#2563EB" />
                <Text style={styles.centerText}>Loading...</Text>
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.center}>
                <Ionicons name="cloud-offline-outline" size={48} color="#EF4444" />
                <Text style={[styles.centerText, { color: '#EF4444', fontWeight: '600', marginTop: 12 }]}>{error}</Text>
                <TouchableOpacity
                    style={{ marginTop: 16, backgroundColor: '#2563EB', paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 }}
                    onPress={() => fetchCustomers()}
                >
                    <Text style={{ color: '#FFF', fontWeight: '600' }}>Retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.screen}>
            {/* ── Search + Filter Area ── */}
            <View style={styles.searchArea}>
                {/* Search input */}
                <View style={styles.searchBox}>
                    <Ionicons name="search" size={16} color="#9CA3AF" />
                    <TextInput
                        style={styles.searchInput}
                        placeholder={searchPlaceholder}
                        placeholderTextColor="#9CA3AF"
                        value={inputText}
                        onChangeText={handleSearchChange}
                        autoCorrect={false}
                        returnKeyType="search"
                    />
                    {inputText.length > 0 && (
                        <TouchableOpacity onPress={handleClearSearch} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
                            <Ionicons name="close-circle" size={16} color="#9CA3AF" />
                        </TouchableOpacity>
                    )}
                </View>

                {/* Filter tabs */}
                <View style={styles.filterRow}>
                    <Text style={styles.filterLabel}>Filter by:</Text>
                    {FILTERS.map((f) => {
                        const isActive = activeFilters.includes(f.key);
                        return (
                            <TouchableOpacity
                                key={f.key}
                                style={[styles.filterChip, isActive && styles.filterChipActive]}
                                activeOpacity={0.7}
                                onPress={() => handleFilterToggle(f.key)}
                            >
                                <Ionicons
                                    name={isActive ? 'checkbox' : 'square-outline'}
                                    size={12}
                                    color={isActive ? '#FFFFFF' : '#6B7280'}
                                />
                                <Text style={[styles.filterChipText, isActive && styles.filterChipTextActive]}>
                                    {f.label}
                                </Text>
                            </TouchableOpacity>
                        );
                    })}
                </View>
            </View>

            {/* ── List ── */}
            <FlatList
                data={filteredCustomers}
                keyExtractor={(item, index) => `${item.id}-${index}`}
                renderItem={renderItem}
                ListEmptyComponent={renderEmpty}
                ListHeaderComponent={
                    <View style={styles.listHeader}>
                        <Text style={styles.sectionLabel}>
                            {debouncedQuery.trim()
                                ? `Results (${filteredCustomers.length})`
                                : `All Customers (${filteredCustomers.length} of ${totalCustomers})`
                            }
                        </Text>
                    </View>
                }
                ListFooterComponent={
                    loadingMore ? (
                        <View style={styles.footerLoader}>
                            <ActivityIndicator size="small" color="#2563EB" />
                            <Text style={styles.footerText}>Loading more...</Text>
                        </View>
                    ) : hasMore && !debouncedQuery.trim() ? (
                        <View style={styles.footerLoader}>
                            <Text style={styles.footerText}>Scroll for more</Text>
                        </View>
                    ) : null
                }
                onEndReached={loadMore}
                onEndReachedThreshold={0.3}
                contentContainerStyle={styles.listContent}
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={() => fetchCustomers(true)}
                        colors={['#2563EB']}
                        tintColor="#2563EB"
                    />
                }
            />
        </View>
    );
}

const styles = StyleSheet.create({
    screen: {
        flex: 1,
        backgroundColor: '#F9FAFB',
    },

    // Search area
    searchArea: {
        backgroundColor: '#FFFFFF',
        paddingHorizontal: 16,
        paddingTop: 12,
        paddingBottom: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#F3F4F6',
    },
    searchBox: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#F3F4F6',
        borderRadius: 10,
        paddingHorizontal: 12,
        height: 40,
        gap: 8,
    },
    searchInput: {
        flex: 1,
        fontSize: 15,
        color: '#111827',
        ...Platform.select({ web: { outlineStyle: 'none' } }),
    },

    // Filter tabs
    filterRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 10,
        gap: 6,
    },
    filterLabel: {
        fontSize: 12,
        color: '#9CA3AF',
        fontWeight: '500',
        marginRight: 2,
    },
    filterChip: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 16,
        backgroundColor: '#F3F4F6',
        gap: 4,
    },
    filterChipActive: {
        backgroundColor: '#2563EB',
    },
    filterChipText: {
        fontSize: 12,
        fontWeight: '600',
        color: '#6B7280',
    },
    filterChipTextActive: {
        color: '#FFFFFF',
    },

    // List
    listContent: {
        paddingBottom: 24,
    },
    footerLoader: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: 16,
        gap: 8,
    },
    footerText: {
        fontSize: 12,
        color: '#9CA3AF',
        fontWeight: '500',
    },
    listHeader: {
        paddingHorizontal: 16,
        paddingTop: 14,
        paddingBottom: 6,
    },
    sectionLabel: {
        fontSize: 13,
        fontWeight: '600',
        color: '#6B7280',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    demoBanner: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FFFBEB',
        paddingVertical: 8,
        paddingHorizontal: 12,
        borderRadius: 8,
        marginBottom: 12,
        gap: 6,
        borderWidth: 1,
        borderColor: '#FDE68A',
    },
    demoText: {
        fontSize: 12,
        color: '#92400E',
        fontWeight: '500',
    },

    // Card
    card: {
        backgroundColor: '#FFFFFF',
        marginHorizontal: 16,
        marginTop: 8,
        borderRadius: 12,
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 14,
        paddingRight: 14,
        paddingLeft: 0,
        overflow: 'hidden',
        borderWidth: 1,
        borderColor: '#F3F4F6',
        ...Platform.select({
            ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 3 },
            android: { elevation: 1 },
            web: { shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.04, shadowRadius: 3 },
        }),
    },
    cardAccent: {
        width: 4,
        alignSelf: 'stretch',
        borderTopLeftRadius: 12,
        borderBottomLeftRadius: 12,
    },
    avatar: {
        width: 42,
        height: 42,
        borderRadius: 21,
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: 12,
        marginRight: 12,
    },
    avatarText: {
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: '700',
    },
    cardBody: {
        flex: 1,
    },
    ownerName: {
        fontSize: 15,
        fontWeight: '600',
        color: '#111827',
        marginBottom: 2,
    },
    shopName: {
        fontSize: 13,
        color: '#6B7280',
        marginBottom: 4,
    },
    metaRow: {
        flexDirection: 'row',
        gap: 8,
    },
    metaBadge: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 3,
    },
    metaBadgeId: {
        backgroundColor: '#F5F3FF',
        paddingHorizontal: 5,
        paddingVertical: 1,
        borderRadius: 4,
    },
    metaBadgeMobile: {
        backgroundColor: '#ECFDF5',
        paddingHorizontal: 5,
        paddingVertical: 1,
        borderRadius: 4,
    },
    metaText: {
        fontSize: 11,
        color: '#6B7280',
        fontWeight: '500',
    },

    // Center / Empty
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F9FAFB',
    },
    centerText: {
        marginTop: 12,
        fontSize: 14,
        color: '#6B7280',
    },
    emptyContainer: {
        alignItems: 'center',
        paddingTop: 60,
        paddingHorizontal: 24,
    },
    emptyCard: {
        alignItems: 'center',
        backgroundColor: '#FFFFFF',
        borderRadius: 16,
        paddingVertical: 40,
        paddingHorizontal: 24,
        width: '100%',
        borderWidth: 1,
        borderColor: '#F3F4F6',
    },
    emptyTitle: {
        fontSize: 18,
        fontWeight: '700',
        color: '#1F2937',
        marginTop: 16,
    },
    emptySubtitle: {
        fontSize: 14,
        color: '#9CA3AF',
        marginTop: 6,
        textAlign: 'center',
        lineHeight: 20,
    },
    clearBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: 20,
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 8,
        backgroundColor: '#EFF6FF',
        gap: 6,
    },
    clearBtnText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#2563EB',
    },
});
