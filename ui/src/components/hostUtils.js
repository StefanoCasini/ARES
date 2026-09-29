// Helpers to read HostDTO objects from the report JSON.
// Tolerant to the old output format (os_info / commands instead of os / discovery_commands).

const STATE_PRIORITY = ['open', 'open|filtered', 'filtered', 'closed|filtered', 'closed', 'unknown'];

export function getHostnames(host) {
    const hostnames = host?.hostnames;
    if (!hostnames || typeof hostnames !== 'object') return [];
    if (Array.isArray(hostnames)) return hostnames.map(name => ({ name, sources: [] }));
    return Object.entries(hostnames).map(([name, sources]) => ({
        name,
        sources: Array.isArray(sources) ? sources : [],
    }));
}

export function getOsGuesses(host) {
    const os = host?.os ?? host?.os_info;
    if (!os) return [];
    if (Array.isArray(os)) return os.map(o => (typeof o === 'string' ? { name: o, cpes: [] } : o));
    if (typeof os === 'object') return Object.keys(os).map(name => ({ name, cpes: [] }));
    return [];
}

export function getHostCpes(host) {
    const cpes = host?.cpes;
    if (!cpes || typeof cpes !== 'object') return [];
    if (Array.isArray(cpes)) return cpes.map(cpe => ({ cpe, sources: [] }));
    return Object.entries(cpes).map(([cpe, sources]) => ({
        cpe,
        sources: Array.isArray(sources) ? sources : [],
    }));
}

export function getDiscoveryCommands(host) {
    const cmds = host?.discovery_commands ?? host?.commands;
    return Array.isArray(cmds) ? cmds : [];
}

// Merge the per-tool entries of each port into a single summary row.
export function getPorts(host) {
    const ports = host?.ports;
    if (!ports || typeof ports !== 'object') return [];

    return Object.entries(ports)
        .map(([key, rawEntries]) => {
            const entries = Array.isArray(rawEntries) ? rawEntries : [rawEntries];
            const [number, protocol = ''] = key.split('/');
            const states = entries.map(e => (e?.state || 'unknown').toLowerCase());
            const state = STATE_PRIORITY.find(s => states.includes(s)) || states[0] || 'unknown';
            const services = [...new Set(entries.map(e => e?.service).filter(Boolean))];
            const sources = [...new Set(entries.map(e => e?.source).filter(Boolean))];
            return { key, number: parseInt(number, 10), protocol, state, services, sources, entries };
        })
        .sort((a, b) => (a.number - b.number) || a.protocol.localeCompare(b.protocol));
}

export function countOpenPorts(host) {
    return getPorts(host).filter(p => p.state === 'open').length;
}

// "2026-04-14_1129_192.168.1.0_24.json" -> "192.168.1.0/24"
export function targetFromFilename(filename) {
    if (!filename) return null;
    const match = filename.replace(/\.json$/, '').match(/^\d{4}-\d{2}-\d{2}_\d{4}_(.+)$/);
    if (!match) return null;
    return match[1].replace(/_(\d{1,3})$/, '/$1');
}
