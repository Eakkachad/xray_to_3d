import { useState, useEffect } from 'react';
import { fetchMetrics } from '../api/client.js';
import CTViewer from './CTViewer.jsx';
import GifViewer from './GifViewer.jsx';

export default function ResultPanel({ scene }) {
    const [metrics, setMetrics] = useState(null);

    useEffect(() => {
        fetchMetrics(scene)
            .then(setMetrics)
            .catch(() => setMetrics(null));
    }, [scene]);

    return (
        <div className="result-panel fade-in">
            <div className="result-header">
                <div>
                    <h2>{scene.replace(/_/g, ' ')}</h2>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        3D Reconstruction Results
                    </span>
                </div>
                <span className="navbar-badge" style={{ fontSize: '0.75rem' }}>
                    SAX-NeRF / Lineformer
                </span>
            </div>

            <div className="result-body">
                <CTViewer scene={scene} />
                <GifViewer scene={scene} />
            </div>

            {metrics && (
                <div className="metrics-grid">
                    <div className="metric-card">
                        <div className="metric-label">2D PSNR</div>
                        <div className="metric-value">
                            {metrics.proj_psnr?.toFixed(2) ?? '—'} <span style={{ fontSize: '0.8rem' }}>dB</span>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">2D SSIM</div>
                        <div className="metric-value">
                            {metrics.proj_ssim?.toFixed(4) ?? '—'}
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">3D PSNR</div>
                        <div className="metric-value">
                            {metrics.psnr_3d?.toFixed(2) ?? '—'} <span style={{ fontSize: '0.8rem' }}>dB</span>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-label">3D SSIM</div>
                        <div className="metric-value">
                            {metrics.ssim_3d?.toFixed(4) ?? '—'}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
