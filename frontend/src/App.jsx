import { useState } from 'react'
import './App.css'
import FileBrowser from './components/FileBrowser'

function App() {
  const [currentView, setCurrentView] = useState('dashboard')

  return (
    <div className="app-container">
      <nav className="app-nav">
        <div className="nav-brand">
          <span className="nav-icon">🤖</span>
          <div>
            <h1 className="nav-title">EntrepEAI</h1>
            <p className="nav-subtitle">AI File Manager</p>
          </div>
        </div>

        <div className="nav-links">
          <a href="#" className="nav-link active">Dashboard</a>
          <a href="#" className="nav-link">Files</a>
          <a href="#" className="nav-link">Upload</a>
          <a href="#" className="nav-link">Settings</a>
        </div>
      </nav>

      <main className="app-main">
        <FileBrowser initialPath="/" viewMode="grid" />
      </main>
    </div>
  )
}

export default App
