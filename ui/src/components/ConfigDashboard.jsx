import React, { useState, useEffect } from 'react';
import { Play, Save, Loader2, CheckCircle2 } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

const JsonEditor = ({ data, onChange, path = [] }) => {
    if (typeof data === 'boolean') {
        return (
            <input 
                type="checkbox" 
                checked={data} 
                onChange={e => onChange(path, e.target.checked)} 
                className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
        );
    }
    if (typeof data === 'string' || typeof data === 'number') {
        return (
            <input 
                type={typeof data === 'number' ? 'number' : 'text'} 
                value={data} 
                onChange={e => onChange(path, typeof data === 'number' ? Number(e.target.value) : e.target.value)} 
                className="border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" 
            />
        );
    }
    if (Array.isArray(data)) {
        return (
            <div className="pl-4 border-l-2 border-gray-200 mt-2 space-y-4">
                {data.map((item, index) => (
                    <div key={index} className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 relative group">
                        <button 
                            onClick={() => {
                                const newData = [...data];
                                newData.splice(index, 1);
                                onChange(path, newData);
                            }}
                            className="absolute top-2 right-2 px-2 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200 text-xs transition-colors"
                            title="Remove item"
                        >
                            Remove
                        </button>
                        {typeof item === 'object' && item !== null && 'name' in item && (
                            <h4 className="text-lg font-semibold text-gray-800 mb-3 border-b pb-2 pr-16">{item.name}</h4>
                        )}
                        <JsonEditor data={item} onChange={onChange} path={[...path, index]} />
                    </div>
                ))}
                <button 
                    onClick={() => {
                        let newItem = '';
                        if (data.length > 0) {
                            if (typeof data[0] === 'string') newItem = '';
                            else if (typeof data[0] === 'number') newItem = 0;
                            else if (typeof data[0] === 'boolean') newItem = false;
                            else newItem = JSON.parse(JSON.stringify(data[data.length - 1]));
                        }
                        onChange(path, [...data, newItem]);
                    }}
                    className="mt-2 px-4 py-2 bg-slate-100 text-slate-700 rounded hover:bg-slate-200 text-sm font-medium transition-colors border border-slate-200"
                >
                    + Add Item
                </button>
            </div>
        );
    }
    if (typeof data === 'object' && data !== null) {
        const isModeObj = path.length === 1 && path[0] === 'mode';
        const isToolObj = path.length === 2 && path[0] === 'mode' && path[1].startsWith('launcher_');

        return (
            <div className="pl-4 border-l-2 border-slate-200 mt-2 pt-2">
                {Object.entries(data).map(([key, value]) => {
                    // Skip name as we rendered it as header
                    if (key === 'name' && Array.isArray(path) && typeof path[path.length - 1] === 'number') return null;
                    
                    if (isModeObj && data.enable_scan === false && key !== 'enable_scan') return null;
                    if (isToolObj && data.enabled === false && key !== 'enabled') return null;

                    return (
                        <div key={key} className="mb-4">
                            <label className="block text-sm font-medium text-slate-700 mb-1 capitalize">
                                {key.replace(/_/g, ' ')}
                            </label>
                            <JsonEditor data={value} onChange={onChange} path={[...path, key]} />
                        </div>
                    );
                })}
            </div>
        );
    }
    return <span className="text-gray-500 text-sm">Unsupported Type</span>;
};

export default function ConfigDashboard() {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [scanStarting, setScanStarting] = useState(false);
    const [toast, setToast] = useState(null);

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    useEffect(() => {
        fetch(`${API_BASE}/config`)
            .then(res => res.json())
            .then(data => {
                setConfig(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch config", err);
                setLoading(false);
            });
    }, []);

    const handleChange = (path, value) => {
        setConfig(prevConfig => {
            const newConfig = JSON.parse(JSON.stringify(prevConfig));
            let current = newConfig;
            for (let i = 0; i < path.length - 1; i++) {
                current = current[path[i]];
            }
            current[path[path.length - 1]] = value;
            return newConfig;
        });
        setSaveSuccess(false);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            await fetch(`${API_BASE}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (err) {
            console.error("Failed to save", err);
        } finally {
            setSaving(false);
        }
    };

    const handleStartScan = async () => {
        setScanStarting(true);
        try {
            const res = await fetch(`${API_BASE}/scan/start`, { method: 'POST' });
            const data = await res.json();
            
            if (data.message === "Scan already running!") {
                showToast('Scan already in progress.', 'error');
            } else if (res.ok) {
                showToast('Scan initiated successfully.', 'success');
                window.dispatchEvent(new Event('scanStarted'));
            } else {
                showToast('Failed to connect to backend.', 'error');
            }
        } catch (err) {
            console.error("Failed to start scan", err);
            showToast('Failed to connect to backend.', 'error');
        } finally {
            setScanStarting(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center p-12 text-gray-500">
            <Loader2 className="w-8 h-8 animate-spin mr-3" /> Loading configuration...
        </div>
    );

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between border-b pb-4 mb-6">
                <h2 className="text-xl font-bold text-gray-800">Configuration Editor</h2>
                <div className="flex space-x-3">
                    <button 
                        onClick={handleSave} 
                        disabled={saving}
                        className="flex items-center px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 disabled:opacity-50 transition-colors cursor-pointer"
                    >
                        {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : 
                         saveSuccess ? <CheckCircle2 className="w-4 h-4 mr-2 text-green-400" /> : 
                         <Save className="w-4 h-4 mr-2" />}
                        {saveSuccess ? 'Saved!' : 'Save Config'}
                    </button>
                    <button 
                        onClick={handleStartScan}
                        disabled={scanStarting || saving} 
                        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm cursor-pointer"
                    >
                        {scanStarting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                        Start Scan
                    </button>
                </div>
            </div>
            
            <div className="overflow-y-auto max-h-[70vh] pr-4">
                {config ? <JsonEditor data={config} onChange={handleChange} /> : <div className="text-red-500">Could not load config.</div>}
            </div>

            {toast && (
                <div className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg font-mono text-sm transition-all duration-300 transform translate-y-0 opacity-100 ${
                    toast.type === 'error' ? 'bg-gray-800 text-red-400 border-l-2 border-red-500' : 'bg-gray-800 text-green-400 border-l-2 border-green-500'
                }`}>
                    {toast.message}
                </div>
            )}
        </div>
    );
}
