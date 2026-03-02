import { getGifUrl } from '../api/client.js';

export default function GifViewer({ scene }) {
    const gifUrl = getGifUrl(scene);

    return (
        <div className="gif-viewer">
            <div className="ct-viewer-label">
                <span>3D Reconstruction</span>
                <span className="mono">360° rotation</span>
            </div>
            <div className="gif-viewer-image">
                <img
                    src={gifUrl}
                    alt={`3D reconstruction of ${scene}`}
                    onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.innerHTML =
                            '<span class="placeholder-icon" style="opacity:0.3">🔄 GIF not available</span>';
                    }}
                />
            </div>
        </div>
    );
}
