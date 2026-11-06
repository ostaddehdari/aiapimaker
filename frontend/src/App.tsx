import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { LoginPage } from './pages/LoginPage';
import { AdminOverview, AdminProviders, AdminSupervisor, AdminUsers } from './pages/AdminPages';
import { UserAccounts, UserChat, UserTokens } from './pages/UserPages';
import { ThemeProvider } from './theme';
import { appBasePath } from './config';

export function App() {
  return (
    <ThemeProvider>
      <BrowserRouter basename={appBasePath}>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/admin" element={<AppShell role="admin" />}>
            <Route index element={<AdminOverview />} />
            <Route path="providers" element={<AdminProviders />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="supervisor" element={<AdminSupervisor />} />
          </Route>
          <Route path="/app" element={<AppShell role="user" />}>
            <Route index element={<UserChat />} />
            <Route path="accounts" element={<UserAccounts />} />
            <Route path="api-tokens" element={<UserTokens />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
