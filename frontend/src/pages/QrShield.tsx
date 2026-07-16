import { useState } from 'react';
import { QrCode, Upload, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { scanQrImage } from '../api/client';

export default function QrShield() {
  const [preview, setPreview] = useState<string | null>(null);
  const [findings, setFindings] = useState<{ qr_content: string; is_url: boolean }[] | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFile = async (file: File) => {
    setPreview(URL.createObjectURL(file));
    setLoading(true);
    setFindings(null);
    try {
      const res = await scanQrImage(file);
      setFindings(res.findings);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center gap-2 mb-1">
        <QrCode size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">QR Shield</h1>
      </div>
      <p className="text-slate-500 text-[13.5px] mb-8">
        Upload a QR code image (e.g. a screenshot from an email) to see exactly where it leads before you scan it with your phone.
      </p>

      <label className="glass rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer hover:border-primary/40 border-2 border-dashed border-border transition-colors mb-6">
        <Upload size={22} className="text-slate-500 mb-3" />
        <span className="text-[13px] text-slate-400">Click to upload a QR code image</span>
        <span className="text-[11px] text-slate-600 mt-1">PNG or JPG</span>
        <input
          type="file"
          accept="image/png,image/jpeg"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </label>

      {preview && (
        <div className="glass rounded-2xl p-6 mb-6 flex gap-6 items-start">
          <img src={preview} alt="Uploaded QR" className="w-32 h-32 rounded-xl object-contain bg-card-raised p-2" />
          <div className="flex-1">
            {loading && <div className="text-slate-500 text-[13px]">Scanning...</div>}
            {!loading && findings && findings.length === 0 && (
              <div className="flex items-center gap-2 text-success text-[13px]">
                <CheckCircle2 size={16} /> No QR code detected in this image.
              </div>
            )}
            {!loading && findings && findings.length > 0 && findings.map((f, i) => (
              <div key={i} className="mb-3">
                <div className="flex items-center gap-2 text-warning text-[13px] mb-2">
                  <AlertTriangle size={15} /> QR code decoded — verify before visiting.
                </div>
                <div className="font-mono text-[12px] text-slate-200 bg-card-raised border border-border rounded-lg px-3 py-2 break-all">
                  {f.qr_content}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
