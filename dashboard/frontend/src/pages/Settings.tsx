import { Routes, Route, Navigate } from 'react-router-dom';
import BotSettings from './settings/BotSettings';
import AISettings from './settings/AISettings';
import ModerationSettings from './settings/ModerationSettings';
import LevelingSettings from './settings/LevelingSettings';
import EconomySettings from './settings/EconomySettings';
import FeatureToggles from './settings/FeatureToggles';

export default function Settings() {
  return (
    <Routes>
      <Route index element={<Navigate to="bot" replace />} />
      <Route path="bot" element={<BotSettings />} />
      <Route path="ai" element={<AISettings />} />
      <Route path="moderation" element={<ModerationSettings />} />
      <Route path="leveling" element={<LevelingSettings />} />
      <Route path="economy" element={<EconomySettings />} />
      <Route path="features" element={<FeatureToggles />} />
    </Routes>
  );
}
