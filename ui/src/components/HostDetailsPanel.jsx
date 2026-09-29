import React, { useState } from 'react';
import { X, Server, ChevronRight, ChevronDown, Cpu, Tag, Terminal } from 'lucide-react';
import { getHostnames, getOsGuesses, getHostCpes, getDiscoveryCommands, getPorts } from './hostUtils';

const stateBadge = (state) => {
    if (state === 'open') return 'bg-green-900/40 text-green-400 border-green-700/50';
    if (state.includes('filtered')) return 'bg-yellow-900/40 text-yellow-400 border-yellow-700/50';
    if (state === 'closed') return 'bg-red-900/40 text-red-400 border-red-700/50';
    return 'bg-gray-800 text-gray-400 border-gray-700';
};

const Section = ({ icon: Icon, title, children, defaultOpen = true }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    return (
        <div className="border-t border-gray-800 pt-3 mt-3">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center w-full text-left text-xs uppercase tracking-wider text-gray-400 hover:text-gray-200 mb-2"
            >
                {isOpen ? <ChevronDown className="w-3 h-3 mr-1" /> : <ChevronRight className="w-3 h-3 mr-1" />}
                <Icon className="w-3 h-3 mr-2 text-fuchsia-400" />
                {title}
            </button>
            {isOpen && children}
        </div>
    );
};

const Field = ({ label, value }) => {
    if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) return null;
    return (
        <div className="flex text-xs">
            <span className="text-gray-500 w-20 flex-shrink-0">{label}</span>
            <span className="text-gray-300 break-all">{Array.isArray(value) ? value.join(', ') : String(value)}</span>
        </div>
    );
};

const PortRow = ({ port }) => {
    const [expanded, setExpanded] = useState(false);
    return (
        <>
            <tr
                className="border-b border-gray-800/60 hover:bg-gray-800/40 cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <td className="py-1.5 pr-2 text-cyan-300 whitespace-nowrap">
                    {expanded ? <ChevronDown className="w-3 h-3 inline mr-1" /> : <ChevronRight className="w-3 h-3 inline mr-1" />}
                    {port.key}
                </td>
                <td className="py-1.5 pr-2">
                    <span className={`px-1.5 py-0.5 rounded border text-[10px] ${stateBadge(port.state)}`}>{port.state}</span>
                </td>
                <td className="py-1.5 pr-2 text-gray-300 break-all">{port.services.join(', ') || '-'}</td>
                <td className="py-1.5 text-gray-500">{port.sources.join(', ')}</td>
            </tr>
            {expanded && (
                <tr className="border-b border-gray-800/60 bg-gray-950/60">
                    <td colSpan={4} className="p-2 space-y-2">
                        {port.entries.map((entry, i) => (
                            <div key={i} className="space-y-0.5 border-l-2 border-fuchsia-800/60 pl-2">
                                <Field label="source" value={entry.source} />
                                <Field label="state" value={entry.state} />
                                <Field label="service" value={entry.service} />
                                <Field label="banner" value={entry.banner} />
                                <Field label="reason" value={entry.reason} />
                                <Field label="ttl" value={entry.ttl} />
                                <Field label="type" value={entry.port_type !== 'unknown' ? entry.port_type : null} />
                                <Field label="cpes" value={entry.cpes} />
                                <Field label="command" value={entry.command !== 'unknown' ? entry.command : null} />
                            </div>
                        ))}
                    </td>
                </tr>
            )}
        </>
    );
};

export default function HostDetailsPanel({ host, onClose }) {
    const [onlyOpen, setOnlyOpen] = useState(false);

    const hostnames = getHostnames(host);
    const osGuesses = getOsGuesses(host);
    const cpes = getHostCpes(host);
    const commands = getDiscoveryCommands(host);
    const ports = getPorts(host);
    const openCount = ports.filter(p => p.state === 'open').length;
    const visiblePorts = onlyOpen ? ports.filter(p => p.state === 'open') : ports;

    return (
        <div className="w-96 flex-shrink-0 h-full overflow-y-auto bg-gray-900 border border-gray-800 rounded-md p-4 font-mono text-left">
            <div className="flex items-start justify-between">
                <div className="flex items-start min-w-0">
                    <Server className="w-5 h-5 mr-2 mt-0.5 text-cyan-400 flex-shrink-0" />
                    <div className="min-w-0">
                        <h3 className="text-lg font-bold text-gray-100 break-all">{host.ip}</h3>
                        {hostnames.map(h => (
                            <div key={h.name} className="text-sm text-fuchsia-300 break-all" title={h.sources.join('\n')}>
                                {h.name}
                            </div>
                        ))}
                    </div>
                </div>
                <button onClick={onClose} className="text-gray-500 hover:text-gray-200 p-1" title="Close">
                    <X className="w-4 h-4" />
                </button>
            </div>

            <div className="flex gap-2 mt-3 text-xs">
                <span className="px-2 py-1 rounded bg-green-900/30 text-green-400 border border-green-800/50">{openCount} open</span>
                <span className="px-2 py-1 rounded bg-gray-800 text-gray-300 border border-gray-700">{ports.length} ports</span>
            </div>

            <Section icon={Tag} title={`Ports (${visiblePorts.length})`}>
                {ports.length === 0 ? (
                    <p className="text-xs text-gray-500">No ports found.</p>
                ) : (
                    <>
                        <label className="flex items-center text-xs text-gray-400 mb-2 cursor-pointer select-none">
                            <input
                                type="checkbox"
                                className="mr-2 accent-cyan-500"
                                checked={onlyOpen}
                                onChange={e => setOnlyOpen(e.target.checked)}
                            />
                            Show only open
                        </label>
                        <table className="w-full text-xs">
                            <thead>
                                <tr className="text-gray-500 border-b border-gray-800 text-left">
                                    <th className="pb-1 font-normal">port</th>
                                    <th className="pb-1 font-normal">state</th>
                                    <th className="pb-1 font-normal">service</th>
                                    <th className="pb-1 font-normal">tools</th>
                                </tr>
                            </thead>
                            <tbody>
                                {visiblePorts.map(p => <PortRow key={p.key} port={p} />)}
                            </tbody>
                        </table>
                    </>
                )}
            </Section>

            {osGuesses.length > 0 && (
                <Section icon={Cpu} title="Operating system">
                    <ul className="space-y-1">
                        {osGuesses.map((os, i) => (
                            <li key={i} className="text-xs">
                                <div className="text-gray-200">{os.name}</div>
                                {os.cpes?.length > 0 && <div className="text-gray-500 break-all">{os.cpes.join(', ')}</div>}
                            </li>
                        ))}
                    </ul>
                </Section>
            )}

            {cpes.length > 0 && (
                <Section icon={Tag} title="CPE">
                    <ul className="space-y-1">
                        {cpes.map(c => (
                            <li key={c.cpe} className="text-xs text-gray-300 break-all" title={c.sources.join('\n')}>{c.cpe}</li>
                        ))}
                    </ul>
                </Section>
            )}

            {commands.length > 0 && (
                <Section icon={Terminal} title={`Discovery commands (${commands.length})`} defaultOpen={false}>
                    <ul className="space-y-1">
                        {commands.map((cmd, i) => (
                            <li key={i} className="text-[11px] text-gray-400 bg-gray-950 border border-gray-800 rounded p-1.5 break-all">{cmd}</li>
                        ))}
                    </ul>
                </Section>
            )}
        </div>
    );
}
