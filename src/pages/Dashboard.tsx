import { useEffect, useState } from 'react';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { api } from '../services/api';
import { StatsResponse, HealthResponse } from '../types/api';
import {
  Database,
  Activity,
  RefreshCw,
  CheckCircle,
} from 'lucide-react';

export function Dashboard() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, healthData] = await Promise.all([
        api.getStats(),
        api.health(),
      ]);
      setStats(statsData);
      setHealth(healthData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await api.runScraper();
      await loadData();
    } catch (error) {
      console.error('Failed to refresh data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-slate-900 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-slate-600 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 mb-1">
            Dashboard
          </h1>
          <p className="text-slate-600">
            Monitor AI model pricing and optimize costs
          </p>
        </div>
        <Button
          variant="secondary"
          onClick={handleRefresh}
          disabled={refreshing}
          size="sm"
        >
          <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
          {refreshing ? 'Refreshing' : 'Refresh'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Models</p>
                <p className="text-3xl font-semibold text-slate-900">
                  {stats?.total_models || 0}
                </p>
              </div>
              <div className="p-2 bg-slate-100 rounded-lg">
                <Database className="text-slate-700" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Providers</p>
                <p className="text-3xl font-semibold text-slate-900">
                  {stats?.providers.length || 0}
                </p>
              </div>
              <div className="p-2 bg-slate-100 rounded-lg">
                <Activity className="text-slate-700" size={20} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">System Status</p>
                <div className="flex items-center gap-2 mt-2">
                  <CheckCircle className="text-emerald-600" size={20} />
                  <p className="text-lg font-medium text-slate-900">
                    {health?.status === 'healthy' ? 'Healthy' : 'Unknown'}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Monitored Providers
            </h2>
            <div className="space-y-3">
              {stats?.providers.map((provider) => (
                <div
                  key={provider}
                  className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-slate-900 flex items-center justify-center text-white text-sm font-medium">
                      {provider.charAt(0)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{provider}</p>
                      <p className="text-xs text-slate-600">
                        {stats?.provider_counts[provider]} models
                      </p>
                    </div>
                  </div>
                  <Badge variant="success">Active</Badge>
                </div>
              ))}
              {(!stats?.providers || stats.providers.length === 0) && (
                <div className="text-center py-8 text-slate-500">
                  <Database className="mx-auto mb-2" size={32} />
                  <p className="text-sm">No providers found</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Getting Started
            </h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                  1
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-900 mb-1">
                    Ask the Oracle
                  </h4>
                  <p className="text-sm text-slate-600">
                    Query pricing data using natural language
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                  2
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-900 mb-1">
                    Optimize with Architect
                  </h4>
                  <p className="text-sm text-slate-600">
                    Get AI-powered recommendations to reduce costs
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                  3
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-900 mb-1">
                    Track Savings
                  </h4>
                  <p className="text-sm text-slate-600">
                    Monitor your cost optimizations over time
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
