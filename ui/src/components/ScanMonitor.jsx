import React, { useState, useEffect, useRef } from 'react';
import { Activity, Clock, Terminal, Target } from 'lucide-react';

export default function ScanMonitor() {
    const [scans, setScans] = useState([]);
    const [isRunning, setIsRunning] = useState(false);
    const [error, setError] = useState(null);
    const [toast, setToast] = useState(null);
    const prevIsRunning = useRef(isRunning);

    const showToast = (message, type = 'success') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    useEffect(() => {
        if (prevIsRunning.current === true && isRunning === false) {
            showToast('Output file is ready!', 'success');
            window.dispatchEvent(new Event('scanFinished'));
        }
        prevIsRunning.current = isRunning;
    }, [isRunning]);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/scan/status');
                if (!res.ok) throw new Error("Failed to fetch");
                const data = await res.json();

                setScans(data.tasks || []);
                setIsRunning(data.is_running);
            } catch (err) {
                console.error(err);
                setError("Error fetching scan status");
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);

        const handleScanStarted = () => {
            setIsRunning(true);
            setScans([]);
        };
        window.addEventListener('scanStarted', handleScanStarted);

        return () => {
            clearInterval(interval);
            window.removeEventListener('scanStarted', handleScanStarted);
        };
    }, []);

    // 1. Define the main content based on state, but DO NOT return early.
    let content;

    if (scans.length === 0 && !error) {
        if (isRunning) {
            content = (
                <div className="bg-gray-900 shadow rounded-lg p-6 border border-gray-800">
                    <div className="flex items-center text-yellow-400 justify-center font-mono">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span className="animate-pulse">Initializing scanning engine...</span>
                    </div>
                </div>
            );
        } else {
            content = (
                <div className="bg-gray-900 shadow rounded-lg p-6 border border-gray-800">
                    <div className="flex items-center text-gray-500 justify-center font-mono">
                        <Terminal className="w-5 h-5 mr-2 opacity-50" />
                        &gt;_ No scans currently running
                    </div>
                </div>
            );
        }
    } else {
        content = (
            <div className="bg-gray-900 shadow rounded-lg overflow-hidden border border-gray-800">
                <div className="flex items-center justify-between border-b border-gray-800 p-6 pb-4">
                    <h2 className="text-lg font-bold text-gray-200 flex items-center font-mono tracking-wide">
                        <Activity className="w-5 h-5 mr-2 text-cyan-500" />
                        [ SCAN MONITOR ]
                    </h2>
                    {isRunning && (
                        <div className="flex items-center text-sm font-medium text-cyan-400 font-mono">
                            <span className="relative flex h-3 w-3 mr-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                            </span>
                            SYS_ACTIVE
                        </div>
                    )}
                </div>

                {error && <div className="text-red-500 mb-4 px-6 font-mono text-sm">[!] {error}</div>}

                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-800">
                        <thead className="bg-gray-800">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">Tool</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">Target</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">Duration</th>
                                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono w-1/3">Command</th>
                            </tr>
                        </thead>
                        <tbody className="bg-gray-900 divide-y divide-gray-800">
                            {scans.map((scan, i) => (
                                <tr key={i} className="hover:bg-gray-800/50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="font-mono text-cyan-400 font-medium">{scan.tool}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center text-fuchsia-400 font-mono text-sm">
                                            <Target className="w-4 h-4 mr-2" />
                                            {scan.target}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-bold uppercase tracking-wide">
                                        {scan.status === 'RUNNING' && (
                                            <span className="text-yellow-400 animate-pulse">
                                                RUNNING...
                                            </span>
                                        )}
                                        {scan.status === 'DONE' && (
                                            <span className="text-green-400">
                                                DONE
                                            </span>
                                        )}
                                        {scan.status === 'ERROR' && (
                                            <span className="text-red-500">
                                                ERROR
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center text-gray-300 text-sm font-mono">
                                            <Clock className="w-4 h-4 mr-2 text-gray-500" />
                                            {scan.duration}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 max-w-sm">
                                        <div className="flex items-center font-mono text-sm text-gray-500" title={scan.command}>
                                            <Terminal className="w-4 h-4 mr-2 text-gray-600 flex-shrink-0" />
                                            <span className="truncate">{scan.command}</span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }

    // 2. Wrap everything in a fragment. The Toast is now bulletproof.
    return (
        <>
            {content}
            {toast && (
                <div className={`fixed bottom-4 right-4 z-[9999] px-4 py-2 rounded shadow-lg font-mono text-sm transition-all duration-300 transform translate-y-0 opacity-100 ${toast.type === 'error' ? 'bg-gray-800 text-red-400 border-l-2 border-red-500' : 'bg-gray-800 text-green-400 border-l-2 border-green-500'
                    }`}>
                    {toast.message}
                </div>
            )}
        </>
    );
}