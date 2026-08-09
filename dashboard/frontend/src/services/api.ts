import api from '../lib/api';

// Auth
export const authApi = {
  getDiscordAuthUrl: () => api.get('/api/auth/discord'),
  handleCallback: (code: string, state: string) =>
    api.get(`/api/auth/callback?code=${code}&state=${state}`),
  getCurrentUser: () => api.get('/api/auth/me'),
  logout: () => api.post('/api/auth/logout'),
};

// Bot Settings
export const settingsApi = {
  // Bot Global
  getBotGlobal: () => api.get('/api/settings/bot/global'),
  updateBotGlobal: (data: any) => api.put('/api/settings/bot/global', data),
  
  // AI
  getAI: () => api.get('/api/settings/ai'),
  updateAI: (data: any) => api.put('/api/settings/ai', data),
  
  // Moderation
  getModeration: () => api.get('/api/settings/moderation'),
  updateModeration: (data: any) => api.put('/api/settings/moderation', data),
  
  // Leveling
  getLeveling: () => api.get('/api/settings/leveling'),
  updateLeveling: (data: any) => api.put('/api/settings/leveling', data),
  
  // Economy
  getEconomy: () => api.get('/api/settings/economy'),
  updateEconomy: (data: any) => api.put('/api/settings/economy', data),
  
  // Features
  getFeatures: () => api.get('/api/settings/features'),
  updateFeatures: (data: any) => api.put('/api/settings/features', data),
  
  // Guild
  getGuild: (guildId: string) => api.get(`/api/settings/guild/${guildId}`),
  updateGuild: (guildId: string, data: any) =>
    api.put(`/api/settings/guild/${guildId}`, data),
};

// Bot Status
export const botApi = {
  getStatus: () => api.get('/api/bot/status'),
  getConfig: () => api.get('/api/bot/config'),
};

// Servers
export const serversApi = {
  list: () => api.get('/api/servers'),
  get: (guildId: string) => api.get(`/api/servers/${guildId}`),
  updateConfig: (guildId: string, config: any) =>
    api.put(`/api/servers/${guildId}/config`, config),
  getLeaderboard: (guildId: string, limit = 10) =>
    api.get(`/api/servers/${guildId}/leaderboard?limit=${limit}`),
  getAnalytics: (guildId: string) => api.get(`/api/servers/${guildId}/analytics`),
};
