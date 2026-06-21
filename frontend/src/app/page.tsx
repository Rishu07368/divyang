'use client';

import { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import {
  Users, MapPin, AlertTriangle, Heart, ChevronRight, Menu, X,
  Home, Map, BarChart2, Shield, Lightbulb, Calendar, Upload, Settings
} from 'lucide-react';

// Types
interface DashboardData {
  summary: {
    total_beneficiaries: number;
    last_updated: string;
    by_gender: Record<string, number>;
    by_age_group: Record<string, number>;
    by_social_status: Record<string, number>;
  };
  disability_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  village_distribution: Record<string, number>;
  key_metrics: {
    severity_avg_score: number;
    welfare_eligible_total: number;
    without_ayushman: number;
    not_in_school: number;
    high_priority_beneficiaries: number;
  };
  resource_needs: {
    staff: {
      special_educators: number;
      physiotherapists: number;
      speech_therapists: number;
      cbr_workers: number;
    };
  };
  top_insights: { id: string; title: string; urgency: string; impact: number }[];
}

interface Insight {
  id: string;
  category: string;
  title: string;
  description: string;
  evidence: string[];
  impact_score: number;
  confidence: number;
  urgency: string;
  recommendations: string[];
  affected_count: number;
  location: string;
}

const CHART_COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#11998e', '#38ef7d'];

const SEVERITY_COLORS: Record<string, string> = {
  MILD: '#22c55e',
  MODERATE: '#eab308',
  SEVERE: '#f97316',
  CRITICAL: '#dc2626',
};

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashboardRes, insightsRes] = await Promise.all([
        fetch('/data/dashboard_data.json'),
        fetch('/data/processed/ai_insights.json'),
      ]);
      
      const dashboardData = await dashboardRes.json();
      const insightsData = await insightsRes.json();
      
      setData(dashboardData);
      setInsights(insightsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Disability Intelligence Platform...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-600">Failed to load data. Please run the analytics pipeline.</p>
      </div>
    );
  }

  const disabilityChartData = Object.entries(data.disability_distribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name: name.length > 20 ? name.substring(0, 20) + '...' : name, value }));

  const severityChartData = Object.entries(data.severity_distribution).map(([name, value]) => ({
    name,
    value,
    fill: SEVERITY_COLORS[name] || '#6b7280'
  }));

  const genderChartData = Object.entries(data.summary.by_gender).map(([name, value]) => ({ name, value }));

  const ageChartData = Object.entries(data.summary.by_age_group)
    .sort((a, b) => {
      const order = ['0-2', '3-5', '6-10', '11-14', '15-18', '19+'];
      const getOrder = (s: string) => order.findIndex(o => s.includes(o));
      return getOrder(a[0]) - getOrder(b[0]);
    })
    .map(([name, value]) => ({ name: name.replace(/\s+/g, ''), value }));

  const villageChartData = Object.entries(data.village_distribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, value]) => ({ name: name.substring(0, 15), value }));

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'maps', label: 'Maps', icon: Map },
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
    { id: 'welfare', label: 'Welfare', icon: Shield },
    { id: 'insights', label: 'AI Insights', icon: Lightbulb },
    { id: 'planning', label: 'Planning', icon: Calendar },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-indigo-700 text-white transition-all duration-300 flex flex-col`}>
        <div className="p-4 border-b border-indigo-600">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 flex-shrink-0" />
            {sidebarOpen && (
              <div>
                <h1 className="font-bold text-lg">DIP</h1>
                <p className="text-xs text-indigo-200">Disability Platform</p>
              </div>
            )}
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`sidebar-item w-full ${activeTab === tab.id ? 'active' : ''}`}
            >
              <tab.icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span>{tab.label}</span>}
            </button>
          ))}
        </nav>

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 border-t border-indigo-600 flex items-center justify-center"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 capitalize">{activeTab}</h2>
              <p className="text-sm text-gray-500">
                Last updated: {new Date(data.summary.last_updated).toLocaleString()}
              </p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
              <Upload className="w-4 h-4" />
              Upload Data
            </button>
          </div>
        </header>

        <div className="p-6">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Total Beneficiaries"
                  value={data.summary.total_beneficiaries}
                  icon={Users}
                  gradient="stat-gradient-blue"
                />
                <StatCard
                  title="Villages Covered"
                  value={Object.keys(data.village_distribution).length}
                  icon={MapPin}
                  gradient="stat-gradient-green"
                />
                <StatCard
                  title="High Priority"
                  value={data.key_metrics.high_priority_beneficiaries}
                  icon={AlertTriangle}
                  gradient="stat-gradient-orange"
                />
                <StatCard
                  title="Welfare Eligible"
                  value={data.key_metrics.welfare_eligible_total}
                  icon={Heart}
                  gradient="stat-gradient-purple"
                />
              </div>

              {/* Charts Row */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Disability Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={disabilityChartData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        dataKey="value"
                        label={({ name, percent }) => `${name.substring(0, 10)} (${(percent * 100).toFixed(0)}%)`}
                      >
                        {disabilityChartData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Severity Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={severityChartData}>
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                        {severityChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* More Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={genderChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        dataKey="value"
                        label
                      >
                        <Cell fill="#667eea" />
                        <Cell fill="#f5576c" />
                        <Cell fill="#11998e" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Top Villages</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={villageChartData} layout="vertical">
                      <XAxis type="number" />
                      <YAxis type="category" dataKey="name" width={100} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#4facfe" radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Resource Requirements */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Staff Requirements</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <ResourceCard title="Special Educators" count={data.resource_needs.staff.special_educators} color="bg-blue-100 text-blue-800" />
                  <ResourceCard title="Physiotherapists" count={data.resource_needs.staff.physiotherapists} color="bg-green-100 text-green-800" />
                  <ResourceCard title="Speech Therapists" count={data.resource_needs.staff.speech_therapists} color="bg-purple-100 text-purple-800" />
                  <ResourceCard title="CBR Workers" count={data.resource_needs.staff.cbr_workers} color="bg-orange-100 text-orange-800" />
                </div>
              </div>
            </>
          )}

          {/* Maps Tab */}
          {activeTab === 'maps' && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Beneficiary Map</h3>
              <div className="map-container bg-gray-100 flex items-center justify-center">
                <p className="text-gray-500">Interactive maps available in /data/maps/</p>
              </div>
              <div className="mt-4 flex gap-4 justify-center">
                <a href="/data/maps/beneficiary_map.html" target="_blank" className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                  Open Beneficiary Map
                </a>
                <a href="/data/maps/severity_heatmap.html" target="_blank" className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  Open Heatmap
                </a>
                <a href="/data/maps/village_summary_map.html" target="_blank" className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">
                  Village Summary
                </a>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Key Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard title="Without Ayushman Card" value={data.key_metrics.without_ayushman} />
                  <MetricCard title="Not in School" value={data.key_metrics.not_in_school} />
                  <MetricCard title="Avg Severity Score" value={data.key_metrics.severity_avg_score.toFixed(1)} />
                </div>
              </div>
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Age Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={ageChartData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#4facfe" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Welfare Tab */}
          {activeTab === 'welfare' && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Welfare Scheme Recommendations</h3>
              <p className="text-gray-600 mb-4">
                Total eligible scheme matches: <span className="font-bold text-indigo-600">{data.key_metrics.welfare_eligible_total}</span>
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <SchemeCard name="Disability Pension" agency="Central Govt" benefits="₹300-500/month" />
                <SchemeCard name="ADIP Scheme" agency="Ministry of Social Justice" benefits="Free aids & appliances" />
                <SchemeCard name="UP Disability Pension" agency="UP Government" benefits="₹500-1000/month" />
                <SchemeCard name="Scholarship for Disabled" agency="Central Govt" benefits="₹500-1600/month" />
                <SchemeCard name="Health Insurance (Ayushman)" agency="PMJAY" benefits="₹5 lakh coverage" />
                <SchemeCard name="UP Free Education" agency="UP Government" benefits="Free education 1-12 to PhD" />
              </div>
            </div>
          )}

          {/* Insights Tab */}
          {activeTab === 'insights' && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-red-100 rounded-xl p-6 text-center">
                  <p className="text-4xl font-bold text-red-600">
                    {insights.filter(i => i.urgency === 'CRITICAL').length}
                  </p>
                  <p className="text-red-800">Critical Insights</p>
                </div>
                <div className="bg-orange-100 rounded-xl p-6 text-center">
                  <p className="text-4xl font-bold text-orange-600">
                    {insights.filter(i => i.urgency === 'HIGH').length}
                  </p>
                  <p className="text-orange-800">High Priority</p>
                </div>
                <div className="bg-indigo-100 rounded-xl p-6 text-center">
                  <p className="text-4xl font-bold text-indigo-600">{insights.length}</p>
                  <p className="text-indigo-800">Total Insights</p>
                </div>
              </div>

              {insights.slice(0, 10).map((insight) => (
                <div key={insight.id} className={`insight-card insight-${insight.urgency.toLowerCase()} p-6 rounded-xl`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        insight.urgency === 'CRITICAL' ? 'bg-red-200 text-red-800' :
                        insight.urgency === 'HIGH' ? 'bg-orange-200 text-orange-800' :
                        insight.urgency === 'MEDIUM' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-green-200 text-green-800'
                      }`}>{insight.urgency}</span>
                      <h4 className="font-semibold mt-2">{insight.title}</h4>
                      <p className="text-gray-600 text-sm mt-1">{insight.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">{insight.impact_score}</p>
                      <p className="text-xs text-gray-500">Impact</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm font-semibold text-gray-700">Recommendations:</p>
                    <ul className="text-sm text-gray-600 list-disc list-inside mt-1">
                      {insight.recommendations.slice(0, 3).map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                  <p className="text-xs text-gray-400 mt-3">
                    Affected: {insight.affected_count} beneficiaries | Location: {insight.location}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Planning Tab */}
          {activeTab === 'planning' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Resource Allocation</h3>
                <p className="text-gray-600">View detailed allocation plans in the analytics output.</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

// Helper Components
function StatCard({ title, value, icon: Icon, gradient }: {
  title: string;
  value: number;
  icon: any;
  gradient: string;
}) {
  return (
    <div className={`${gradient} rounded-xl p-6 text-white card-hover`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white/80 text-sm">{title}</p>
          <p className="text-4xl font-bold mt-2">{value}</p>
        </div>
        <Icon className="w-12 h-12 opacity-50" />
      </div>
    </div>
  );
}

function ResourceCard({ title, count, color }: { title: string; count: number; color: string }) {
  return (
    <div className={`${color} rounded-lg p-4 text-center`}>
      <p className="text-3xl font-bold">{count}</p>
      <p className="text-sm mt-1">{title}</p>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: number | string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
    </div>
  );
}

function SchemeCard({ name, agency, benefits }: { name: string; agency: string; benefits: string }) {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
      <h4 className="font-semibold text-gray-800">{name}</h4>
      <p className="text-xs text-indigo-600 mt-1">{agency}</p>
      <p className="text-sm text-gray-600 mt-2">{benefits}</p>
    </div>
  );
}