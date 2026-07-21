import { useParams } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from 'react-leaflet';
import { useState, useEffect } from 'react';
import { api } from '../services/api.js';

const SOURCE_COLOR = { phone: '#00C8FF', vehicle: '#5CFFB1' };

export default function MapView() {
  const { id } = useParams();
  const [c, setC] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCase(id).then(setC).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-forensic-muted p-10 text-center animate-pulse">Loading data...</div>;
  const points = c?.gps || [];

  if (!points.length)
    return (
      <div className="panel panel-pad text-forensic-muted text-sm">
        No GPS data ingested for this case.
      </div>
    );

  const center = [
    points.reduce((a, p) => a + p.lat, 0) / points.length,
    points.reduce((a, p) => a + p.lng, 0) / points.length,
  ];

  // group by source for polylines
  const groups = {};
  points.forEach((p) => {
    (groups[p.source] = groups[p.source] || []).push(p);
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold">Movement reconstruction</h2>
        <div className="flex gap-2 ml-auto">
          {Object.keys(groups).map((g) => (
            <span key={g} className="chip border-forensic-border text-forensic-muted">
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: SOURCE_COLOR[g] || '#7A8899' }}
              />
              {g}
            </span>
          ))}
        </div>
      </div>
      <div className="panel overflow-hidden" style={{ height: 520 }}>
        <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}{r}.png"
          />
          {Object.entries(groups).map(([source, pts]) => (
            <Polyline
              key={source}
              positions={pts.map((p) => [p.lat, p.lng])}
              pathOptions={{
                color: SOURCE_COLOR[source] || '#7A8899',
                weight: 2,
                dashArray: source === 'phone' ? null : '5,6',
                opacity: 0.85,
              }}
            />
          ))}
          {points.map((p) => (
            <CircleMarker
              key={p.id}
              center={[p.lat, p.lng]}
              radius={6}
              pathOptions={{
                color: SOURCE_COLOR[p.source] || '#7A8899',
                fillColor: SOURCE_COLOR[p.source] || '#7A8899',
                fillOpacity: 0.9,
                weight: 2,
              }}
            >
              <Tooltip direction="top" offset={[0, -6]}>
                <div className="text-xs">
                  <div className="font-mono">{new Date(p.timestamp).toLocaleTimeString()}</div>
                  <div className="font-mono">
                    {p.lat.toFixed(4)}, {p.lng.toFixed(4)}
                  </div>
                  <div>±{p.accuracy_m} m · {p.source}</div>
                </div>
              </Tooltip>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
      <div className="panel panel-pad text-xs text-forensic-muted">
        Used by the deterministic contradiction engine. Distances between points are
        computed via the Haversine formula and compared against minimum travel time per mode.
      </div>
    </div>
  );
}
