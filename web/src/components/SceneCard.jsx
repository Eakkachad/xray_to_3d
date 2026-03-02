const SCENE_ICONS = {
    chest: '🫁', abdomen: '🫀', head: '🧠', foot: '🦶', leg: '🦵',
    pelvis: '🦴', pancreas: '🫘', jaw: '🦷', backpack: '🎒', box: '📦',
    bonsai: '🌳', teapot: '🫖', engine: '⚙️', carp: '🐟', aneurism: '💉',
};

export default function SceneCard({ scene, active, onClick }) {
    const icon = SCENE_ICONS[scene.name] || '📷';

    return (
        <div
            className={`scene-card ${active ? 'active' : ''}`}
            onClick={() => onClick(scene)}
            id={`scene-${scene.name}`}
        >
            <div className="scene-card-thumb">
                <span>{icon}</span>
            </div>
            <div className="scene-card-body">
                <div className="scene-card-name">{scene.display_name}</div>
                <div className="scene-card-status">
                    {scene.cached ? (
                        <>
                            <span className="status-dot cached" />
                            <span style={{ color: 'var(--color-blue)' }}>Cached</span>
                        </>
                    ) : scene.ready ? (
                        <>
                            <span className="status-dot ready" />
                            <span style={{ color: 'var(--color-green)' }}>Ready</span>
                        </>
                    ) : (
                        <>
                            <span className="status-dot unavailable" />
                            <span style={{ color: 'var(--text-muted)' }}>Not available</span>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
