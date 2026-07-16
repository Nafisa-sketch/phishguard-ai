import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

// HONEST NOTE: without a real threat-intelligence feed or reliable sender
// geolocation, we can't show genuine attacker locations for every scan.
// This renders a real, interactive world map (not a static image), but
// the highlighted countries reflect the *demo/sample breakdown* passed
// in via `data`, not live-verified attacker geolocation. Treat it as
// an illustrative view of the concept, not a verified threat feed.
const geoUrl = 'https://unpkg.com/world-atlas@2.0.2/countries-110m.json';

interface CountryThreat {
  name: string;
  percent: number;
  color: string;
}

interface WorldThreatMapProps {
  data: CountryThreat[];
}

export default function WorldThreatMap({ data }: WorldThreatMapProps) {
  const colorByName = Object.fromEntries(data.map((d) => [d.name, d.color]));

  return (
    <div className="w-full">
      <ComposableMap projectionConfig={{ scale: 130 }} style={{ width: '100%', height: '160px' }}>
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const name = geo.properties.name as string;
              const fill = colorByName[name] ?? '#1E2740';
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={fill}
                  stroke="#0B0F19"
                  strokeWidth={0.5}
                  style={{
                    default: { outline: 'none' },
                    hover: { outline: 'none', fill: '#6C63FF' },
                    pressed: { outline: 'none' },
                  }}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>
      <div className="space-y-1.5 mt-2">
        {data.map((d) => (
          <div key={d.name} className="flex items-center justify-between text-[11.5px]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />
              <span className="text-slate-300">{d.name}</span>
            </div>
            <span className="text-slate-500">{d.percent}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
