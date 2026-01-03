import { useState } from 'react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input, Textarea } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { api } from '../services/api';
import { ArchitectResponse } from '../types/api';
import {
  Sparkles,
  Loader2,
  DollarSign,
  Check,
  TrendingDown,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function Architect() {
  const [formData, setFormData] = useState({
    use_case_description: '',
    monthly_input_tokens: '',
    monthly_output_tokens: '',
    current_model: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ArchitectResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.use_case_description || !formData.monthly_input_tokens) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await api.optimizeCosts({
        use_case_description: formData.use_case_description,
        monthly_input_tokens: parseInt(formData.monthly_input_tokens),
        monthly_output_tokens: formData.monthly_output_tokens
          ? parseInt(formData.monthly_output_tokens)
          : undefined,
        current_model: formData.current_model || undefined,
      });

      setResult(response);
    } catch (error: any) {
      alert(`Error: ${error.message || 'Failed to optimize costs'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      use_case_description: '',
      monthly_input_tokens: '',
      monthly_output_tokens: '',
      current_model: '',
    });
    setResult(null);
  };

  const chartData = result?.current_model
    ? [
        {
          name: 'Current',
          cost: result.current_model.monthly_cost_raw,
        },
        {
          name: 'Recommended',
          cost: result.recommendation.monthly_cost_raw,
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      <div className="mb-6">
        <h1 className="text-3xl font-semibold text-slate-900 mb-1">
          Cost Architect
        </h1>
        <p className="text-slate-600">
          Get AI-powered recommendations to optimize your infrastructure costs
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <Card className="lg:col-span-2">
          <CardContent className="pt-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Optimization Request
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Textarea
                label="Use Case Description"
                placeholder="e.g., Customer support chatbot with function calling"
                value={formData.use_case_description}
                onChange={(e) =>
                  setFormData({ ...formData, use_case_description: e.target.value })
                }
                rows={4}
                required
              />

              <Input
                label="Monthly Input Tokens"
                type="number"
                placeholder="e.g., 10000000"
                value={formData.monthly_input_tokens}
                onChange={(e) =>
                  setFormData({ ...formData, monthly_input_tokens: e.target.value })
                }
                required
              />

              <Input
                label="Monthly Output Tokens (Optional)"
                type="number"
                placeholder="Auto-calculated if empty"
                value={formData.monthly_output_tokens}
                onChange={(e) =>
                  setFormData({ ...formData, monthly_output_tokens: e.target.value })
                }
              />

              <Input
                label="Current Model (Optional)"
                placeholder="e.g., gpt-4"
                value={formData.current_model}
                onChange={(e) =>
                  setFormData({ ...formData, current_model: e.target.value })
                }
              />

              <div className="flex gap-2 pt-2">
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  disabled={loading || !formData.use_case_description || !formData.monthly_input_tokens}
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      Optimize
                    </>
                  )}
                </Button>
                {result && (
                  <Button type="button" variant="ghost" onClick={handleReset}>
                    Reset
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="lg:col-span-3 space-y-6">
          {!result && !loading && (
            <Card className="h-full flex items-center justify-center min-h-[400px]">
              <CardContent className="text-center py-16">
                <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
                  <TrendingDown className="text-slate-700" size={32} />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Ready to optimize
                </h3>
                <p className="text-slate-600 max-w-md mx-auto">
                  Enter your use case details to get cost recommendations
                </p>
              </CardContent>
            </Card>
          )}

          {loading && (
            <Card className="h-full flex items-center justify-center min-h-[400px]">
              <CardContent className="text-center py-16">
                <Loader2 className="w-12 h-12 text-slate-900 animate-spin mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Analyzing your requirements
                </h3>
                <p className="text-slate-600">
                  Finding the best model for your use case
                </p>
              </CardContent>
            </Card>
          )}

          {result && result.status === 'success' && (
            <>
              {result.savings && (
                <Card>
                  <CardContent className="py-8">
                    <div className="text-center">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-100 mb-4">
                        <DollarSign className="text-emerald-700" size={24} />
                      </div>
                      <h2 className="text-4xl font-bold text-slate-900 mb-2">
                        {result.savings.annual}
                        <span className="text-xl text-slate-600 font-normal">/year</span>
                      </h2>
                      <p className="text-emerald-700 font-medium mb-1">
                        Potential Annual Savings
                      </p>
                      <p className="text-slate-600 text-sm">
                        {result.savings.percentage} cost reduction
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardContent className="pt-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">
                    Recommendation
                  </h2>
                  <div className="space-y-6">
                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center flex-shrink-0">
                          <Sparkles className="text-white" size={20} />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-slate-900 mb-2">
                            {result.recommendation.model}
                          </h3>
                          <p className="text-sm text-slate-700 mb-3">
                            {result.recommendation.reasoning}
                          </p>
                          <Badge variant="success">
                            {result.recommendation.monthly_cost}/month
                          </Badge>
                        </div>
                      </div>
                    </div>

                    {chartData.length > 0 && (
                      <div>
                        <h4 className="font-medium text-slate-900 mb-3">
                          Monthly Cost Comparison
                        </h4>
                        <div className="h-64 bg-slate-50 rounded-lg p-4">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                              <YAxis stroke="#64748b" fontSize={12} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: '#ffffff',
                                  border: '1px solid #e2e8f0',
                                  borderRadius: '8px',
                                }}
                              />
                              <Bar dataKey="cost" radius={[6, 6, 0, 0]}>
                                {chartData.map((_, index) => (
                                  <Cell
                                    key={`cell-${index}`}
                                    fill={index === 0 ? '#ef4444' : '#10b981'}
                                  />
                                ))}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <h2 className="text-lg font-semibold text-slate-900 mb-4">
                    Alternative Options
                  </h2>
                  <div className="space-y-3">
                    {result.alternatives.slice(0, 3).map((alt, index) => (
                      <div
                        key={index}
                        className="p-4 bg-slate-50 rounded-lg border border-slate-200"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="text-sm font-medium text-slate-900">
                              {alt.provider} {alt.model_name}
                            </h4>
                            <p className="text-xs text-slate-600 mt-1">
                              {alt.reasons.slice(0, 2).join(' • ')}
                            </p>
                          </div>
                          <Badge variant="default">{alt.monthly_cost}/mo</Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-slate-600 mt-3">
                          {alt.supports_vision && (
                            <span className="flex items-center gap-1">
                              <Check size={12} className="text-emerald-600" />
                              Vision
                            </span>
                          )}
                          {alt.supports_function_calling && (
                            <span className="flex items-center gap-1">
                              <Check size={12} className="text-emerald-600" />
                              Functions
                            </span>
                          )}
                          {alt.context_window && (
                            <span>
                              {(alt.context_window / 1000).toFixed(0)}K context
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
