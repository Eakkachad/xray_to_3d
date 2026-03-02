import { useState, useEffect } from 'react';
import { fetchSliceInfo, getSliceUrl } from '../api/client.js';

export default function CTViewer({ scene }) {
    const [axis, setAxis] = useState('H');
    const [sliceIndex, setSliceIndex] = useState(0);
    const [totalSlices, setTotalSlices] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        setSliceIndex(0);
        fetchSliceInfo(scene, axis)
            .then((info) => {
                setTotalSlices(info.total_slices);
                setSliceIndex(Math.floor(info.total_slices / 2));
                setLoading(false);
            })
            .catch(() => {
                setTotalSlices(0);
                setLoading(false);
            });
    }, [scene, axis]);

    const imageUrl = totalSlices > 0 ? getSliceUrl(scene, axis, sliceIndex) : null;

    return (
        <div className="ct-viewer">
            <div className="ct-viewer-label">
                <span>CT Cross-Section</span>
                <span className="mono">{axis} axis</span>
            </div>

            <div className="axis-tabs">
                {['H', 'W', 'L'].map((a) => (
                    <button
                        key={a}
                        className={`axis-tab ${axis === a ? 'active' : ''}`}
                        onClick={() => setAxis(a)}
                    >
                        {a === 'H' ? 'Axial (H)' : a === 'W' ? 'Coronal (W)' : 'Sagittal (L)'}
                    </button>
                ))}
            </div>

            <div className="ct-viewer-image">
                {loading ? (
                    <span className="placeholder-icon">⏳</span>
                ) : imageUrl ? (
                    <img
                        src={imageUrl}
                        alt={`CT slice ${axis}/${sliceIndex}`}
                        key={`${scene}-${axis}-${sliceIndex}`}
                    />
                ) : (
                    <span className="placeholder-icon">🚫</span>
                )}
            </div>

            {totalSlices > 0 && (
                <>
                    <input
                        type="range"
                        className="ct-slider"
                        min={0}
                        max={totalSlices - 1}
                        value={sliceIndex}
                        onChange={(e) => setSliceIndex(Number(e.target.value))}
                    />
                    <div className="ct-viewer-label" style={{ marginTop: 'var(--space-xs)' }}>
                        <span>Slice {sliceIndex + 1} / {totalSlices}</span>
                    </div>
                </>
            )}
        </div>
    );
}
