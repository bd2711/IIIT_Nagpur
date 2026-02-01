import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [filesList, setFilesList] = useState([])
  const [uploadStatus, setUploadStatus] = useState('')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState([])
  const messagesEndRef = useRef(null)

  const API_URL = 'http://localhost:8000'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    fetchFiles()
    scrollToBottom()
  }, [messages])

  const fetchFiles = async () => {
    try {
      const resp = await fetch(`${API_URL}/files`)
      const data = await resp.json()
      setFilesList(data)
    } catch (err) {
      console.error('Failed to fetch files:', err)
    }
  }

  const handleFileUpload = async (e) => {
    const selectedFiles = Array.from(e.target.files)
    if (selectedFiles.length === 0) return

    setUploadStatus('Processing documents...')
    const formData = new FormData()
    selectedFiles.forEach(file => {
      formData.append('files', file)
    })

    try {
      const resp = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      })
      const data = await resp.json()
      setUploadStatus(`Ready! ${data.files.length} documents indexed.`)
      fetchFiles()
    } catch (err) {
      setUploadStatus('Indexing failed. Try again.')
      console.error(err)
    }
  }

  const handleClear = async () => {
    if (!window.confirm('Delete all indexed documents?')) return
    try {
      await fetch(`${API_URL}/clear`, { method: 'POST' })
      setUploadStatus('All cleared.')
      setFilesList([])
      setMessages([])
    } catch (err) {
      console.error(err)
    }
  }

  const handleQuery = async () => {
    if (!query.trim()) return

    const userMsg = { role: 'user', content: query }
    setMessages(prev => [...prev, userMsg])
    setQuery('')
    setLoading(true)

    try {
      const resp = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })
      const data = await resp.json()

      const botMsg = {
        role: 'bot',
        content: data.answer,
        sources: data.sources,
        refused: data.refused
      }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Connection lost. Check backend.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <span style={{ fontSize: '2rem' }}>📑</span>
          MindFlow AI
        </div>

        <div className="upload-section">
          <div className="upload-button-wrapper">
            <div className="custom-upload-btn">
              <span style={{ fontSize: '24px', display: 'block' }}>+</span>
              Upload Documents
              <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px' }}>PDF or TXT</p>
            </div>
            <input type="file" multiple onChange={handleFileUpload} accept=".pdf,.txt" />
          </div>
          {uploadStatus && <p style={{ fontSize: '0.8rem', textAlign: 'center' }}>{uploadStatus}</p>}
        </div>

        <div className="file-list-container">
          <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '1px' }}>
            Knowledge Base ({filesList.length})
          </p>
          {filesList.map((fname, i) => (
            <div key={i} className="file-item">
              <span>📄</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{fname}</span>
            </div>
          ))}
        </div>

        <button className="btn-danger" onClick={handleClear}>
          Reset Knowledge Base
        </button>
      </aside>

      <main className="main-content">
        <div className="chat-window">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '20vh', opacity: 0.5 }}>
              <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>How can I help you?</h2>
              <p>Upload your research papers or hackathon themes and start asking questions.</p>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              <div className="text">{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="sources-box">
                  <div style={{ marginBottom: '8px', color: 'var(--text-dim)', fontWeight: 600 }}>Sources:</div>
                  {m.sources.map((s, si) => (
                    <div key={si} className="source-pill">
                      {s.doc_name} (Chunk {s.chunk_index + 1})
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="message bot">Analyzing documents...</div>}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="glass-input-group">
            <input
              type="text"
              placeholder="Query your knowledge base..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
            />
            <button className="btn-premium" onClick={handleQuery} disabled={loading}>
              Ask AI
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
