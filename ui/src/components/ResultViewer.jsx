import React, { useState, useEffect } from 'react';
import { Loader2, FileJson, Network, AlertCircle } from 'lucide-react';
import NetworkGraph from './NetworkGraph';

const JsonNode = ({ data, name }) => {
    const [isOpen, setIsOpen] = useState(true);

    if (data === null) return <span className="text-gray-500 font-mono">null</span>;
    
    if (typeof data === 'boolean') {
        return <span className="text-blue-400 font-mono">{data ? 'true' : 'false'}</span>;
    }
    
    if (typeof data === 'number') {
        return <span className="text-orange-400 font-mono">{data}</span>;
    }
    
    if (typeof data === 'string') {
        return <span className="text-green-400 font-mono">"{data}"</span>;
    }

    if (Array.isArray(data)) {
        if (data.length === 0) return <span className="text-gray-500 font-mono">[]</span>;
        
        return (
            <div className="font-mono text-sm">
                <span 
                    className="cursor-pointer text-gray-400 hover:text-gray-200 select-none mr-1"
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? '[-]' : '[+]'}
                </span>
                <span className="text-gray-300">Array({data.length}) [</span>
                {isOpen && (
                    <div className="pl-6 border-l border-gray-700 ml-2 mt-1 mb-1">
                        {data.map((item, index) => (
                            <div key={index} className="flex">
                                <span className="text-gray-500 mr-2">{index}:</span>
                                <div><JsonNode data={item} /></div>
                            </div>
                        ))}
                    </div>
                )}
                {!isOpen && <span className="text-gray-500"> ... </span>}
                <span className="text-gray-300">]</span>
            </div>
        );
    }

    if (typeof data === 'object') {
        const keys = Object.keys(data);
        if (keys.length === 0) return <span className="text-gray-500 font-mono">&#123;&#125;</span>;

        return (
            <div className="font-mono text-sm">
                <span 
                    className="cursor-pointer text-gray-400 hover:text-gray-200 select-none mr-1"
                    onClick={() => setIsOpen(!isOpen)}
                >
                    {isOpen ? '[-]' : '[+]'}
                </span>
                <span className="text-gray-300">&#123;</span>
                {isOpen && (
                    <div className="pl-6 border-l border-gray-700 ml-2 mt-1 mb-1">
                        {keys.map((key) => (
                            <div key={key} className="flex flex-wrap">
                                <span className="text-purple-400 mr-2">"{key}":</span>
                                <div className="break-all" style={{width: 'calc(100% - 120px)'}}><JsonNode data={data[key]} name={key} /></div>
                            </div>
                        ))}
                    </div>
                )}
                {!isOpen && <span className="text-gray-500"> ... </span>}
                <span className="text-gray-300">&#125;</span>
            </div>
        );
    }

    return <span>{String(data)}</span>;
};

export default function ResultViewer() {
    const [fileList, setFileList] = useState([]);
    const [selectedFile, setSelectedFile] = useState('');
    const [result, setResult] = useState(null);
    const [loadingFiles, setLoadingFiles] = useState(true);
    const [isFetchingFile, setIsFetchingFile] = useState(false);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('structured');

    // Fetch the list of files on mount
    useEffect(() => {
        const fetchFileList = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/results');
                if (!res.ok) throw new Error("Failed to fetch file list.");
                const files = await res.json();
                setFileList(files);
                if (files.length > 0) {
                    setSelectedFile(files[0]);
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoadingFiles(false);
            }
        };

        fetchFileList();
    }, []);

    // Fetch specific file when selectedFile changes
    useEffect(() => {
        if (!selectedFile) return;

        const fetchFileContent = async () => {
            setIsFetchingFile(true);
            setError(null);
            try {
                const res = await fetch(`http://localhost:8000/api/results/${selectedFile}`);
                if (!res.ok) {
                    if (res.status === 404) throw new Error("File not found.");
                    throw new Error("Failed to fetch file content.");
                }
                const data = await res.json();
                setResult(data);
            } catch (err) {
                setError(err.message);
                setResult(null);
            } finally {
                setIsFetchingFile(false);
            }
        };

        fetchFileContent();
    }, [selectedFile]);

    if (loadingFiles) {
        return (
            <div className="flex items-center justify-center p-12 text-gray-500 bg-gray-900 rounded-lg shadow border border-gray-800">
                <Loader2 className="w-8 h-8 animate-spin mr-3 text-cyan-500" /> 
                <span className="font-mono text-cyan-400 animate-pulse">Loading scan history...</span>
            </div>
        );
    }

    if (fileList.length === 0) {
        return (
            <div className="bg-gray-900 shadow rounded-lg p-8 border border-gray-800 text-center">
                <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4 opacity-80" />
                <h3 className="text-xl font-bold text-gray-300 mb-2 font-mono">No scan history available</h3>
                <p className="text-gray-500 font-mono">Run a scan from the dashboard to see results here.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-900 shadow rounded-lg overflow-hidden border border-gray-800 flex flex-col" style={{ minHeight: '600px' }}>
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-gray-800 p-6 pb-4 bg-gray-800/50">
                <div className="flex items-center md:w-[50%] mb-4 md:mb-0">
                    <FileJson className="w-5 h-5 mr-3 text-fuchsia-500 flex-shrink-0" />
                    <div className="flex-1 overflow-hidden pr-4">
                        <h2 className="text-lg font-bold text-gray-200 font-mono tracking-wide whitespace-nowrap overflow-hidden text-ellipsis mb-2">
                            [ SCAN RESULT ]
                        </h2>
                        <select
                            className="bg-gray-950 border border-gray-700 text-gray-300 text-sm rounded-md focus:ring-fuchsia-500 focus:border-fuchsia-500 block w-full p-2 font-mono"
                            value={selectedFile}
                            onChange={(e) => setSelectedFile(e.target.value)}
                            disabled={isFetchingFile}
                        >
                            {fileList.map((file) => (
                                <option key={file} value={file}>{file}</option>
                            ))}
                        </select>
                    </div>
                </div>
                
                <div className="flex bg-gray-900 rounded-lg p-1 border border-gray-700 flex-shrink-0 ml-0 md:ml-4">
                    <button
                        onClick={() => setActiveTab('structured')}
                        className={`flex items-center px-4 py-2 rounded-md text-sm font-mono transition-colors ${
                            activeTab === 'structured' 
                                ? 'bg-gray-800 text-fuchsia-400 shadow-sm border border-gray-700' 
                                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                        }`}
                    >
                        <FileJson className="w-4 h-4 mr-2" />
                        Structured View
                    </button>
                    <button
                        onClick={() => setActiveTab('graph')}
                        className={`flex items-center px-4 py-2 rounded-md text-sm font-mono transition-colors ${
                            activeTab === 'graph' 
                                ? 'bg-gray-800 text-cyan-400 shadow-sm border border-gray-700' 
                                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                        }`}
                    >
                        <Network className="w-4 h-4 mr-2" />
                        Graph View
                    </button>
                </div>
            </div>

            <div className="p-6 flex-1 overflow-auto bg-gray-900 relative">
                {error && (
                    <div className="bg-red-900/20 border border-red-500/50 text-red-400 p-4 rounded mb-4 font-mono text-sm flex items-center">
                        <AlertCircle className="w-4 h-4 mr-2" />
                        {error}
                    </div>
                )}
                
                {isFetchingFile ? (
                     <div className="flex items-center justify-center p-12 text-gray-500">
                        <Loader2 className="w-8 h-8 animate-spin mr-3 text-fuchsia-500" /> 
                     </div>
                ) : (
                    <>
                        {activeTab === 'structured' && result && (
                            <div className="bg-gray-950 p-4 rounded border border-gray-800 box-border text-left relative z-0">
                                <JsonNode data={result?.data || result} />
                            </div>
                        )}
                        
                        {activeTab === 'graph' && (
                            <div className="h-[70vh] min-h-[500px] w-full font-mono">
                                <NetworkGraph data={result} />
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
