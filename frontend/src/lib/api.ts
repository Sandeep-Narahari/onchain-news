import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getNews = async (token_id?: string) => {
    const params = token_id ? { token_id } : {};
    const res = await api.get('/news', { params });
    return res.data;
};

export const loginUser = async (address: string, message: string, signature: string) => {
    const res = await api.post('/auth/login', { address, message, signature });
    return res.data;
};

export const ensureUser = async (address: string) => {
    // MVP: Auto-register user without signature verification for now
    return loginUser(address, "Auto-login", "0x");
};

export const getApiKeys = async (address: string) => {
    const res = await api.get('/api-keys', { params: { user_address: address } });
    return res.data;
};

export const createApiKey = async (address: string, name: string) => {
    const res = await api.post('/api-keys', { name }, { params: { user_address: address } });
    return res.data;
};

export const revokeApiKey = async (address: string, keyId: string) => {
    const res = await api.delete(`/api-keys/${keyId}`, { params: { user_address: address } });
    return res.data;
};

export const getBalance = async (address: string) => {
    const res = await api.get('/billing/balance', { params: { user_address: address } });
    return res.data;
};

export const getUsage = async (address: string) => {
    const res = await api.get('/billing/usage', { params: { user_address: address } });
    return res.data;
};

export const verifyPayment = async (address: string, txHash: string) => {
    const res = await api.post('/billing/verify', { user_address: address, tx_hash: txHash });
    return res.data;
};
