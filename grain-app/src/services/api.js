import axios from 'axios';
import { Platform } from 'react-native';

// ─── Configuration ───────────────────────────────────────────
// Web:              localhost
// Android emulator: 10.0.2.2 (maps to host machine's localhost)
// Physical device:  replace with your machine's local IP (e.g. 192.168.x.x)
// ──────────────────────────────────────────────────────────────

const getBaseURL = () => {
    if (Platform.OS === 'web') return 'http://localhost:8000';
    if (Platform.OS === 'android') return 'http://10.0.2.2:8000';
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
