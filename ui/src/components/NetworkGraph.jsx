import React, { useMemo, useRef, useEffect, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { forceCollide } from 'd3-force-3d';
import HostDetailsPanel from './HostDetailsPanel';
import { getHostnames, countOpenPorts, targetFromFilename } from './hostUtils';

const COLORS = {
    network: '#ec4899',
    hostOpen: '#06b6d4',
    hostNoOpen: '#6b7280',
    selected: '#facc15',
    link: '#374151',
    label: '#e5e7eb',
    subLabel: '#9ca3af',
};
const NODE_REL_SIZE = 4;
// Labels are drawn in graph units so they scale with zoom; this lets the
// collision force reserve room for them.
const LABEL_FONT_SIZE = 4;
const LABEL_LINE_HEIGHT = LABEL_FONT_SIZE * 1.2;
const LABEL_CHAR_WIDTH = LABEL_FONT_SIZE * 0.62; // monospace approximation
const LABEL_MAX_CHARS = 24;
const MIN_LABEL_SCREEN_PX = 5; // below this the labels are hidden (except selected/hovered)
const HOSTS_PER_RING = 20;

const nodeRadius = (node) => Math.sqrt(node.val) * NODE_REL_SIZE;

const truncate = (text) => (text.length > LABEL_MAX_CHARS ? `${text.slice(0, LABEL_MAX_CHARS - 1)}…` : text);

const labelLines = (node) => {
    if (node.type === 'network') return [node.label];
    return node.hostname ? [truncate(node.hostname), node.ip] : [node.ip];
};

// Radius of a circle that roughly contains the node plus its label below it
const collisionRadius = (node) => {
    const lines = labelLines(node);
    const halfWidth = (Math.max(...lines.map(l => l.length)) * LABEL_CHAR_WIDTH) / 2;
    const r = nodeRadius(node);
    return Math.max(r + lines.length * LABEL_LINE_HEIGHT, halfWidth) + 3;
};

export default function NetworkGraph({ data }) {
    const containerRef = useRef(null);
    const graphRef = useRef(null);
    const hasFitRef = useRef(false);
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [selectedIp, setSelectedIp] = useState(null);
    const [hoveredId, setHoveredId] = useState(null);

    // Keep the canvas sized to its container (also when the details panel opens/closes)
    useEffect(() => {
        if (!containerRef.current) return;
        const observer = new ResizeObserver(([entry]) => {
            const { width, height } = entry.contentRect;
            setDimensions({ width: Math.floor(width), height: Math.floor(height) });
        });
        observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    const report = data?.data ?? data;
    const hosts = report?.hosts && typeof report.hosts === 'object' ? report.hosts : {};

    const graphData = useMemo(() => {
        const nodes = [];
        const links = [];
        const hostEntries = Object.entries(hosts);
        if (hostEntries.length === 0) return { nodes, links };

        const networkId = '__network__';
        const networkLabel = targetFromFilename(data?.filename) || 'Network';
        nodes.push({ id: networkId, type: 'network', label: networkLabel, val: 10, color: COLORS.network, fx: 0, fy: 0 });

        // Stagger hosts on concentric rings so big scans don't pile up on one circle
        const rings = Math.max(1, Math.ceil(hostEntries.length / HOSTS_PER_RING));

        hostEntries.forEach(([ip, host], index) => {
            const openPorts = countOpenPorts(host);
            const hostname = getHostnames(host)[0]?.name;
            nodes.push({
                id: ip,
                type: 'host',
                ip,
                hostname,
                host: { ...host, ip: host?.ip || ip },
                openPorts,
                val: 3 + Math.min(openPorts, 20),
                color: openPorts > 0 ? COLORS.hostOpen : COLORS.hostNoOpen,
            });
            links.push({ source: networkId, target: ip, ring: index % rings });
        });

        return { nodes, links };
    }, [hosts, data?.filename]);

    // Spread the layout: longer, ring-staggered links, stronger repulsion and label-aware collisions
    useEffect(() => {
        const fg = graphRef.current;
        if (!fg || graphData.nodes.length === 0) return;
        const hostCount = graphData.nodes.length - 1;
        const baseDistance = 60 + Math.sqrt(hostCount) * 8;
        const ringGap = 45;

        fg.d3Force('link').distance(link => baseDistance + link.ring * ringGap).strength(0.6);
        fg.d3Force('charge').strength(-80).distanceMax(400);
        fg.d3Force('collide', forceCollide(collisionRadius).strength(0.9).iterations(2));
        fg.d3ReheatSimulation();
    }, [graphData]);

    // New file loaded: reset selection and re-fit the view once the layout settles
    useEffect(() => {
        setSelectedIp(null);
        hasFitRef.current = false;
    }, [data]);

    const selectedHost = selectedIp ? graphData.nodes.find(n => n.id === selectedIp)?.host : null;

    const paintNode = useCallback((node, ctx, globalScale) => {
        const r = nodeRadius(node);

        if (node.id === selectedIp) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, r + 3, 0, 2 * Math.PI);
            ctx.fillStyle = COLORS.selected;
            ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
        ctx.fillStyle = node.color;
        ctx.fill();

        const isFocused = node.id === selectedIp || node.id === hoveredId;
        const tooSmall = LABEL_FONT_SIZE * globalScale < MIN_LABEL_SCREEN_PX;
        if (tooSmall && !isFocused && node.type !== 'network') return;

        // Focused nodes keep a readable label even when zoomed out
        const fontSize = tooSmall ? MIN_LABEL_SCREEN_PX / globalScale : LABEL_FONT_SIZE;
        const lines = labelLines(node);
        ctx.font = `${fontSize}px monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';

        let y = node.y + r + 1.5;
        if (isFocused) {
            const width = Math.max(...lines.map(l => ctx.measureText(l).width));
            ctx.fillStyle = 'rgba(10, 10, 10, 0.85)';
            ctx.fillRect(node.x - width / 2 - 1, y - 0.5, width + 2, lines.length * fontSize * 1.2 + 1);
        }
        lines.forEach((line, i) => {
            if (node.type === 'network') ctx.fillStyle = COLORS.network;
            else ctx.fillStyle = i === 0 ? COLORS.label : COLORS.subLabel;
            ctx.fillText(line, node.x, y);
            y += fontSize * 1.2;
        });
    }, [selectedIp, hoveredId]);

    const paintPointerArea = useCallback((node, color, ctx) => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius(node) + 2, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
    }, []);

    const handleNodeClick = useCallback((node) => {
        if (node.type !== 'host') return;
        setSelectedIp(prev => (prev === node.id ? null : node.id));
    }, []);

    const handleEngineStop = useCallback(() => {
        if (!hasFitRef.current && graphRef.current) {
            graphRef.current.zoomToFit(400, 60);
            hasFitRef.current = true;
        }
    }, []);

    const hostCount = graphData.nodes.filter(n => n.type === 'host').length;

    return (
        <div className="w-full h-full flex gap-4">
            <div ref={containerRef} className="flex-1 min-w-0 h-full flex items-center justify-center bg-gray-950 rounded-md border border-gray-800 overflow-hidden relative">
                {!data ? (
                    <span className="text-gray-500 font-mono">No data available for graph rendering.</span>
                ) : hostCount === 0 ? (
                    <span className="text-gray-500 font-mono">No hosts found in this scan.</span>
                ) : (
                    <>
                        <ForceGraph2D
                            ref={graphRef}
                            width={dimensions.width}
                            height={dimensions.height}
                            graphData={graphData}
                            nodeRelSize={NODE_REL_SIZE}
                            nodeLabel={n => (n.type === 'host' ? `${n.ip} — ${n.openPorts} open ports` : n.label)}
                            nodeCanvasObject={paintNode}
                            nodePointerAreaPaint={paintPointerArea}
                            linkColor={() => COLORS.link}
                            onNodeClick={handleNodeClick}
                            onNodeHover={node => setHoveredId(node ? node.id : null)}
                            onBackgroundClick={() => setSelectedIp(null)}
                            onEngineStop={handleEngineStop}
                            autoPauseRedraw={false}
                            backgroundColor="#0a0a0a"
                        />
                        <div className="absolute top-3 left-3 bg-gray-900/80 border border-gray-800 rounded p-2 text-xs font-mono text-gray-400 space-y-1 pointer-events-none">
                            <div className="text-gray-200">{hostCount} hosts</div>
                            <div className="flex items-center"><span className="w-2.5 h-2.5 rounded-full mr-2" style={{ background: COLORS.hostOpen }} />open ports</div>
                            <div className="flex items-center"><span className="w-2.5 h-2.5 rounded-full mr-2" style={{ background: COLORS.hostNoOpen }} />no open ports</div>
                            <div className="text-gray-500 pt-1">click a host for details</div>
                            <div className="text-gray-500">zoom in to read all labels</div>
                        </div>
                    </>
                )}
            </div>
            {selectedHost && (
                <HostDetailsPanel host={selectedHost} onClose={() => setSelectedIp(null)} />
            )}
        </div>
    );
}
