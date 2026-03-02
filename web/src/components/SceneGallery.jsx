import SceneCard from './SceneCard.jsx';

export default function SceneGallery({ scenes, activeScene, onSelect }) {
    return (
        <section className="section" id="gallery">
            <div className="container">
                <h2 style={{ marginBottom: 'var(--space-sm)' }}>
                    <span className="gradient-text">Scene Gallery</span>
                </h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-xl)' }}>
                    Select a scene to reconstruct its 3D CT volume from sparse X-ray views
                </p>
                <div className="gallery-grid">
                    {scenes.map((scene) => (
                        <SceneCard
                            key={scene.name}
                            scene={scene}
                            active={activeScene?.name === scene.name}
                            onClick={onSelect}
                        />
                    ))}
                </div>
            </div>
        </section>
    );
}
