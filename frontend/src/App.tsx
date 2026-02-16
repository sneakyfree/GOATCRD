import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { IntakePage } from './pages/IntakePage';
import { ScenariosPage } from './pages/ScenariosPage';
import { WhatIfPage } from './pages/WhatIfPage';
import { DataExportPage } from './pages/DataExportPage';
import AdminDashboard from './pages/AdminDashboard';
import ReviewQueue from './pages/ReviewQueue';
import AgentMonitor from './pages/AgentMonitor';
import AlternativeDataPage from './pages/AlternativeDataPage';
import PulseAlertsPage from './pages/PulseAlertsPage';
import AuditViewerPage from './pages/AuditViewerPage';
import AccessLogPage from './pages/AccessLogPage';
import MyDataPage from './pages/MyDataPage';
import RetentionSettingsPage from './pages/RetentionSettingsPage';
import ConsentsPage from './pages/ConsentsPage';
// Admin Governance
import AdminProgramsPage from './pages/AdminProgramsPage';
import AdminRulesetsPage from './pages/AdminRulesetsPage';
import AdminReasonCodesPage from './pages/AdminReasonCodesPage';
import AdminPartnersPage from './pages/AdminPartnersPage';
// Fairness CI/CD
import FairnessDashboardPage from './pages/FairnessDashboardPage';
import FairnessArtifactViewer from './pages/FairnessArtifactViewer';
import PostDeployMonitoring from './pages/PostDeployMonitoring';
// LaaS/SDK
import PartnerAuditLog from './pages/PartnerAuditLog';
import PartnerAPIDocs from './pages/PartnerAPIDocs';
// Launch Hardening
import FAQPage from './pages/FAQPage';
import PricingPage from './pages/PricingPage';
// Helix Repair (Gap Closure)
import ObservabilityPage from './pages/ObservabilityPage';
import NotificationsPage from './pages/NotificationsPage';

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="faq" element={<FAQPage />} />
                <Route path="pricing" element={<PricingPage />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="intake/:caseId" element={<IntakePage />} />
                <Route path="scenarios" element={<ScenariosPage />} />
                <Route path="what-if" element={<WhatIfPage />} />
                <Route path="export" element={<DataExportPage />} />
                {/* Consumer Data Rights */}
                <Route path="my-data" element={<MyDataPage />} />
                <Route path="alternative-data" element={<AlternativeDataPage />} />
                <Route path="pulse-alerts" element={<PulseAlertsPage />} />
                <Route path="audit-viewer" element={<AuditViewerPage />} />
                <Route path="access-log" element={<AccessLogPage />} />
                <Route path="retention" element={<RetentionSettingsPage />} />
                <Route path="consents" element={<ConsentsPage />} />
                {/* Admin routes */}
                <Route path="admin" element={<AdminDashboard />} />
                <Route path="admin/review" element={<ReviewQueue />} />
                <Route path="admin/agents" element={<AgentMonitor />} />
                {/* Admin Governance (S1) */}
                <Route path="admin/programs" element={<AdminProgramsPage />} />
                <Route path="admin/rulesets" element={<AdminRulesetsPage />} />
                <Route path="admin/reason-codes" element={<AdminReasonCodesPage />} />
                <Route path="admin/partners" element={<AdminPartnersPage />} />
                {/* Fairness CI/CD (S2) */}
                <Route path="admin/fairness" element={<FairnessDashboardPage />} />
                <Route path="admin/fairness/artifacts" element={<FairnessArtifactViewer />} />
                <Route path="admin/fairness/monitoring" element={<PostDeployMonitoring />} />
                {/* LaaS/SDK Partner (S3) */}
                <Route path="admin/partners/audit" element={<PartnerAuditLog />} />
                <Route path="admin/partners/api-docs" element={<PartnerAPIDocs />} />
                {/* Observability (GAP-6) */}
                <Route path="admin/observability" element={<ObservabilityPage />} />
                {/* Notifications (GAP-7) */}
                <Route path="notifications" element={<NotificationsPage />} />
            </Route>
        </Routes>
    );
}

export default App;



