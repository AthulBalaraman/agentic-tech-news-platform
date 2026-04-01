import { useState, useEffect } from 'react'
import axios from 'axios'
import { RefreshCw, Check, X, ExternalLink, Activity, TrendingUp, Send } from 'lucide-react'

interface Insight {
  _id: string
  external_id: string
  title: string
  source: str
  what_is_it: str
  why_it_matters: str
  technical_implementation: str
  status: str
  tags: string[]
}

interface Trend {
  _id: string
  trend_name: string
  description: string
  related_insights: string[]
}

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [trends, setTrends] = useState<Trend[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'pending' | 'trends'>('pending')

  const fetchData = async () => {
    try {
      const [insightsRes, trendsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/insights?status=pending`),
        axios.get(`${API_BASE}/api/trends`)
      ])
      setInsights(insightsRes.data)
      setTrends(trendsRes.data)
    } catch (err) {
      console.error('Error fetching data:', err)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const triggerCollection = async () => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/trigger-collection`)
      await fetchData()
      alert('Collection trigger successful!')
    } catch (err) {
      alert('Failed to trigger collection')
    } finally {
      setLoading(false)
    }
  }

  const approveInsight = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/api/insights/${encodeURIComponent(id)}/approve`)
      setInsights(insights.filter(i => i.external_id !== id))
    } catch (err) {
      alert('Failed to approve insight')
    }
  }

  const sendTrend = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/api/trends/${id}/send`)
      alert('Trend sent to Telegram successfully!')
    } catch (err) {
      alert('Failed to send trend to Telegram')
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <header className="max-w-6xl mx-auto mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            AI Tech Intel Control
          </h1>
          <p className="text-slate-400 mt-2">Multi-agent technical synthesis engine</p>
        </div>
        
        <button 
          onClick={triggerCollection}
          disabled={loading}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 px-6 py-3 rounded-lg font-medium transition-all"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Processing Agents...' : 'Trigger All Agents'}
        </button>
      </header>

      <main className="max-w-6xl mx-auto">
        <div className="flex gap-4 mb-8 border-b border-slate-800 pb-px">
          <button 
            onClick={() => setActiveTab('pending')}
            className={`pb-4 px-2 flex items-center gap-2 transition-all ${activeTab === 'pending' ? 'border-b-2 border-blue-500 text-blue-400 font-bold' : 'text-slate-400'}`}
          >
            <Activity className="w-4 h-4" />
            Review Queue ({insights.length})
          </button>
          <button 
            onClick={() => setActiveTab('trends')}
            className={`pb-4 px-2 flex items-center gap-2 transition-all ${activeTab === 'trends' ? 'border-b-2 border-blue-500 text-blue-400 font-bold' : 'text-slate-400'}`}
          >
            <TrendingUp className="w-4 h-4" />
            Macro Trends ({trends.length})
          </button>
        </div>

        {activeTab === 'pending' ? (
          <div className="grid gap-6">
            {insights.length === 0 && (
              <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-xl">
                <p className="text-slate-500">The Review Queue is clear. Trigger agents to find new intel.</p>
              </div>
            )}
            
            {insights.map(i => (
              <div key={i._id} className="bg-slate-800/50 border border-slate-700 p-6 rounded-xl hover:border-slate-600 transition-all group">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
                      {i.title}
                      <a href={i.external_id} target="_blank" className="text-slate-500 hover:text-blue-400">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </h3>
                    <div className="flex gap-2">
                      <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300 uppercase tracking-wider">{i.source}</span>
                      {i.tags.map(tag => (
                        <span key={tag} className="text-xs bg-emerald-900/30 text-emerald-400 px-2 py-1 rounded">#{tag}</span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all">
                    <button 
                      onClick={() => approveInsight(i.external_id)}
                      className="p-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg"
                      title="Approve & Send"
                    >
                      <Check className="w-5 h-5" />
                    </button>
                    <button className="p-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg" title="Reject">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6 text-sm">
                  <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">What it is</h4>
                    <p className="text-slate-300 leading-relaxed">{i.what_is_it}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Why it matters</h4>
                    <p className="text-slate-300 leading-relaxed">{i.why_it_matters}</p>
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Tech Details</h4>
                    <p className="text-slate-300 leading-relaxed">{i.technical_implementation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {trends.map(t => (
              <div key={t._id} className="bg-slate-800/50 border border-slate-700 p-6 rounded-xl relative group">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-bold text-emerald-400">{t.trend_name}</h3>
                  <button 
                    onClick={() => sendTrend(t._id)}
                    className="p-2 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                    title="Send Trend to Telegram"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-slate-400 text-sm mb-4 leading-relaxed">{t.description}</p>
                <div className="flex flex-wrap gap-2">
                  {t.related_insights.map(r => (
                    <span key={r} className="text-[10px] bg-slate-700 px-2 py-1 rounded text-slate-300 italic">{r}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
