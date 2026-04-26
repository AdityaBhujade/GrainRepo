import axios from 'axios';
import { Platform } from 'react-native';

// ─── Configuration ───────────────────────────────────────────
// Web:              localhost
// Android emulator: 10.0.2.2 (maps to host machine's localhost)
// Physical device:  replace with your machine's local IP (e.g. 192.168.x.x)
// ──────────────────────────────────────────────────────────────

const getBaseURL = () => {
    if (Platform.OS === 'web') {
        // In production behind nginx, /api is proxied to the backend.
        return process.env.EXPO_PUBLIC_API_BASE_URL || '/api';
    }
    if (Platform.OS === 'android') return 'http://192.168.1.6:8000'; // your PC's local IP
    return 'http://localhost:8000'; // iOS simulator
};

const API = axios.create({
    baseURL: getBaseURL(),
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ─── Customer Endpoints ──────────────────────────────────────

export const getCustomers = (params = {}) =>
    API.get('/customers', { params });

export const getCustomerById = (rowNumber) =>
    API.get(`/customers/${rowNumber}`);

export const updateCustomer = (rowNumber, updates) =>
    API.patch(`/customers/${rowNumber}`, { updates });

// ─── Column Metadata ─────────────────────────────────────────

export const getColumns = () =>
    API.get('/columns');

// ─── Sync ────────────────────────────────────────────────────

export const triggerSync = () =>
    API.post('/sync');

export const getSyncLogs = (limit = 10) =>
    API.get('/sync/logs', { params: { limit } });

// ─── Health ──────────────────────────────────────────────────

export const getHealth = () =>
    API.get('/health');

export default API;
