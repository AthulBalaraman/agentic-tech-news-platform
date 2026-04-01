import { useState, useEffect } from 'react'
import axios from 'axios'
import { RefreshCw, Check, X, ExternalLink, Activity, TrendingUp, Send, Users, Star, GitBranch, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react'

interface Insight {
  _id: string
  external_id: string
  title: string
  source: string
  what_is_it: string
  why_it_matters: string
  technical_implementation: string
  status: string
  tags: string[]
  metadata: any
}

interface Trend {
  _id: string
  trend_name: string
  description: string
  related_insights: string[]
}

interface Subscriber {
  _id: string
  chat_id: number
  user_name: string
  status: string
  registered_at: string
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [trends, setTrends] = useState<Trend[]>([])
  const [subscribers, setSubscribers] = useState<Subscriber[]>([])
  
  // Sent UI states
  const [sentInsights, setSentInsights] = useState<Set<string>>(new Set())
  const [sentTrends, setSentTrends] = useState<Set<string>>(new Set())

  // Pagination State
  const [insightPage, setInsightPage] = useState(1)
  const [insightTotalPages, setInsightTotalPages] = useState(1)
  const [trendPage, setTrendPage] = useState(1)
  const [trendTotalPages, setTrendTotalPages] = useState(1)
  
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'pending' | 'trends' | 'subscribers'>('pending')
  const [expandedInsight, setExpandedInsight] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      const [insightsRes, trendsRes, subsRes] = await Promise.all([
        axios.get<PaginatedResponse<Insight>>(`${API_BASE}/api/insights?status=pending&page=${insightPage}&limit=10`),
        axios.get<PaginatedResponse<Trend>>(`${API_BASE}/api/trends?page=${trendPage}&limit=10`),
        axios.get(`${API_BASE}/api/subscribers?status=pending`) // Assuming subs rarely exceed 100 for now
      ])
      
      setInsights(insightsRes.data.items)
      setInsightTotalPages(insightsRes.data.pages)
      
      setTrends(trendsRes.data.items)
      setTrendTotalPages(trendsRes.data.pages)
      
      setSubscribers(subsRes.data)
    } catch (err) {
      console.error('Error fetching data:', err)
    }
  }

  useEffect(() => {
    fetchData()
  }, [insightPage, trendPage]) // Re-fetch when page changes

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

  const clearSystemData = async () => {
    if (!window.confirm("⚠️ WARNING: This will permanently delete ALL insights, trends, and raw data from the database and vector store. Subscribers will NOT be deleted. Are you sure you want to proceed?")) {
      return;
    }
    
    setLoading(true)
    try {
      await axios.delete(`${API_BASE}/api/system/clear`)
      setInsightPage(1)
      setTrendPage(1)
      await fetchData()
      alert('System data cleared successfully.')
    } catch (err) {
      alert('Failed to clear system data')
    } finally {
      setLoading(false)
    }
  }

  const approveInsight = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/api/insights/${encodeURIComponent(id)}/approve`)
      setSentInsights(prev => new Set(prev).add(id))
      // Note: Not auto-filtering so user can see "Sent" state
    } catch (err) {
      alert('Failed to approve insight')
    }
  }

  const sendTrend = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/api/trends/${id}/send`)
      setSentTrends(prev => new Set(prev).add(id))
    } catch (err) {
      alert('Failed to send trend to Telegram')
    }
  }

  const approveSubscriber = async (chatId: number) => {
    try {
      await axios.post(`${API_BASE}/api/subscribers/${chatId}/approve`)
      setSubscribers(subscribers.filter(s => s.chat_id !== chatId))
    } catch (err) {
      alert('Failed to approve subscriber')
    }
  }

  const rejectSubscriber = async (chatId: number) => {
    try {
      await axios.post(`${API_BASE}/api/subscribers/${chatId}/reject`)
      setSubscribers(subscribers.filter(s => s.chat_id !== chatId))
    } catch (err) {
      alert('Failed to reject subscriber')
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
        
        <div className="flex items-center gap-4">
          <button 
            onClick={clearSystemData}
            disabled={loading}
            className="flex items-center gap-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 disabled:opacity-50 px-4 py-3 rounded-lg font-medium transition-all"
            title="Clear all insights, trends, and database records"
          >
            <Trash2 className="w-5 h-5" />
          </button>

          <button 
            onClick={triggerCollection}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 px-6 py-3 rounded-lg font-medium transition-all"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Processing Agents...' : 'Trigger All Agents'}
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto">
        <div className="flex gap-4 mb-8 border-b border-slate-800 pb-px">
          <button 
            onClick={() => setActiveTab('pending')}
            className={`pb-4 px-2 flex items-center gap-2 transition-all ${activeTab === 'pending' ? 'border-b-2 border-blue-500 text-blue-400 font-bold' : 'text-slate-400'}`}
          >
            <Activity className="w-4 h-4" />
            Review Queue
          </button>
          <button 
            onClick={() => setActiveTab('trends')}
            className={`pb-4 px-2 flex items-center gap-2 transition-all ${activeTab === 'trends' ? 'border-b-2 border-blue-500 text-blue-400 font-bold' : 'text-slate-400'}`}
          >
            <TrendingUp className="w-4 h-4" />
            Macro Trends
          </button>
          <button 
            onClick={() => setActiveTab('subscribers')}
            className={`pb-4 px-2 flex items-center gap-2 transition-all ${activeTab === 'subscribers' ? 'border-b-2 border-blue-500 text-blue-400 font-bold' : 'text-slate-400'}`}
          >
            <Users className="w-4 h-4" />
            Join Requests ({subscribers.length})
          </button>
        </div>

        {activeTab === 'pending' && (
          <div className="grid gap-6">
            {insights.length === 0 && (
              <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-xl">
                <p className="text-slate-500">The Review Queue is clear.</p>
              </div>
            )}
            {insights.map(i => (
              <div key={i._id} className={`bg-slate-800/50 border ${sentInsights.has(i.external_id) ? 'border-emerald-500/50 opacity-60' : 'border-slate-700'} p-6 rounded-xl group overflow-hidden transition-all duration-300`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-xl font-bold flex items-center gap-2">
                        {i.title}
                      </h3>
                      {i.source === 'github' && i.metadata?.stars !== undefined && (
                        <div className="flex items-center gap-1 bg-amber-900/20 text-amber-500 px-2 py-0.5 rounded text-xs font-bold border border-amber-900/30">
                          <Star className="w-3 h-3 fill-amber-500" /> {i.metadata.stars.toLocaleString()}
                        </div>
                      )}
                    </div>
                    
                    <div className="mb-3">
                       <a href={i.external_id} target="_blank" className="text-blue-400 hover:text-blue-300 flex items-center gap-1 text-sm font-medium w-fit">
                         <ExternalLink className="w-4 h-4" /> {i.external_id}
                       </a>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300 uppercase tracking-wider">{i.source}</span>
                      {i.tags.map(tag => (
                        <span key={tag} className="text-xs bg-emerald-900/30 text-emerald-400 px-2 py-1 rounded">#{tag}</span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    {sentInsights.has(i.external_id) ? (
                      <span className="flex items-center gap-1 px-4 py-2 bg-emerald-900/30 text-emerald-400 rounded-lg text-sm font-bold border border-emerald-500/30">
                         <Check className="w-4 h-4"/> Sent
                      </span>
                    ) : (
                      <div className="opacity-0 group-hover:opacity-100 transition-all flex gap-2">
                        <button onClick={() => approveInsight(i.external_id)} className="bg-emerald-600 hover:bg-emerald-500 rounded-lg flex items-center gap-2 px-4 py-2 text-sm font-bold transition-all shadow-lg" title="Approve & Send">
                          <Check className="w-4 h-4" /> Approve
                        </button>
                        <button className="p-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg" title="Reject">
                          <X className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                
                {i.metadata?.image_url && (
                  <div className="mb-6 rounded-lg overflow-hidden border border-slate-700 max-h-[300px] flex justify-center bg-slate-900">
                    <img src={i.metadata.image_url} alt={i.title} className="w-full h-full object-cover object-center max-w-[600px]" />
                  </div>
                )}
                
                <div className="grid md:grid-cols-2 gap-6 text-sm mb-4">
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">What it is</h4>
                      <p className="text-slate-200 leading-relaxed">{i.what_is_it}</p>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Why it matters</h4>
                      <p className="text-slate-200 leading-relaxed">{i.why_it_matters}</p>
                    </div>
                  </div>
                  <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 flex items-center gap-2">
                      <GitBranch className="w-3 h-3" /> Technical Implementation
                    </h4>
                    <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                      {expandedInsight === i._id ? i.technical_implementation : `${i.technical_implementation.substring(0, 150)}...`}
                    </p>
                    <button 
                      onClick={() => setExpandedInsight(expandedInsight === i._id ? null : i._id)}
                      className="mt-3 text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1 uppercase"
                    >
                      {expandedInsight === i._id ? <><ChevronUp className="w-3 h-3" /> Show Less</> : <><ChevronDown className="w-3 h-3" /> Read Detailed Implementation</>}
                    </button>
                  </div>
                </div>
                
                {i.metadata?.updated_at && (
                  <div className="pt-4 border-t border-slate-700/30 text-[10px] text-slate-500 flex justify-between">
                    <span>Last Updated: {new Date(i.metadata.updated_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            ))}
            
            {/* Pagination Controls */}
            {insightTotalPages > 1 && (
              <div className="flex justify-center items-center gap-4 mt-6">
                <button 
                  onClick={() => setInsightPage(p => Math.max(1, p - 1))}
                  disabled={insightPage === 1}
                  className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-lg flex items-center gap-1 font-medium"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <span className="text-slate-400 text-sm font-bold">
                  Page {insightPage} of {insightTotalPages}
                </span>
                <button 
                  onClick={() => setInsightPage(p => Math.min(insightTotalPages, p + 1))}
                  disabled={insightPage === insightTotalPages}
                  className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-lg flex items-center gap-1 font-medium"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="grid gap-6">
            <div className="grid md:grid-cols-2 gap-6">
              {trends.map(t => (
                <div key={t._id} className={`bg-slate-800/50 border ${sentTrends.has(t._id) ? 'border-emerald-500/50 opacity-60' : 'border-slate-700'} p-6 rounded-xl relative group transition-all duration-300`}>
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-bold text-emerald-400">{t.trend_name}</h3>
                    {sentTrends.has(t._id) ? (
                      <span className="flex items-center gap-1 px-3 py-1 bg-emerald-900/30 text-emerald-400 rounded-lg text-xs font-bold border border-emerald-500/30">
                        <Check className="w-3 h-3"/> Sent
                      </span>
                    ) : (
                      <button onClick={() => sendTrend(t._id)} className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-all flex items-center gap-2 text-xs font-bold shadow-lg" title="Send to Telegram">
                        <Send className="w-3 h-3" /> Send Alert
                      </button>
                    )}
                  </div>
                  <p className="text-slate-300 text-sm mb-4 leading-relaxed">{t.description}</p>
                  <div className="flex flex-wrap gap-2">{t.related_insights.map(r => (<span key={r} className="text-[10px] bg-slate-700 px-2 py-1 rounded text-slate-300 italic">{r}</span>))}</div>
                </div>
              ))}
            </div>
            
            {/* Pagination Controls */}
            {trendTotalPages > 1 && (
              <div className="flex justify-center items-center gap-4 mt-6">
                <button 
                  onClick={() => setTrendPage(p => Math.max(1, p - 1))}
                  disabled={trendPage === 1}
                  className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-lg flex items-center gap-1 font-medium"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <span className="text-slate-400 text-sm font-bold">
                  Page {trendPage} of {trendTotalPages}
                </span>
                <button 
                  onClick={() => setTrendPage(p => Math.min(trendTotalPages, p + 1))}
                  disabled={trendPage === trendTotalPages}
                  className="p-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 rounded-lg flex items-center gap-1 font-medium"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'subscribers' && (
          <div className="grid gap-4">
            {subscribers.length === 0 && (
              <div className="text-center py-20 border-2 border-dashed border-slate-800 rounded-xl">
                <p className="text-slate-500">No pending join requests.</p>
              </div>
            )}
            {subscribers.map(s => (
              <div key={s._id} className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl flex justify-between items-center hover:border-slate-600 transition-all">
                <div>
                  <h3 className="font-bold text-blue-400">{s.user_name}</h3>
                  <p className="text-xs text-slate-500">Telegram ID: {s.chat_id}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => approveSubscriber(s.chat_id)} className="flex items-center gap-1 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium"><Check className="w-4 h-4" /> Approve</button>
                  <button onClick={() => rejectSubscriber(s.chat_id)} className="flex items-center gap-1 px-4 py-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 rounded-lg text-sm font-medium"><X className="w-4 h-4" /> Reject</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
