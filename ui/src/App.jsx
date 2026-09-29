import React, { useState } from 'react';
import ConfigDashboard from './components/ConfigDashboard';
import ScanMonitor from './components/ScanMonitor';
import ResultViewer from './components/ResultViewer';
import { LayoutDashboard, FileText } from 'lucide-react';

function App() {
  const [activeGlobalTab, setActiveGlobalTab] = useState('dashboard');

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <header className="mb-6 flex flex-col md:flex-row md:items-center justify-between border-b pb-4">
        <div className="mb-4 md:mb-0">
          <h1 className="text-3xl font-bold text-gray-900">ARES Web Interface</h1>
          <p className="text-gray-500 mt-1">Control center and configuration for ARES</p>
        </div>
        
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveGlobalTab('dashboard')}
            className={`flex items-center px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              activeGlobalTab === 'dashboard' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 mr-2" />
            Scanner Dashboard
          </button>
          <button
            onClick={() => setActiveGlobalTab('results')}
            className={`flex items-center px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              activeGlobalTab === 'results' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }`}
          >
            <FileText className="w-4 h-4 mr-2" />
            Results Viewer
          </button>
        </div>
      </header>

      <main className="space-y-8">
        {activeGlobalTab === 'dashboard' && (
          <>
            <ConfigDashboard />
            <ScanMonitor />
          </>
        )}
        
        {activeGlobalTab === 'results' && (
          <ResultViewer />
        )}
      </main>
    </div>
  );
}

export default App;
