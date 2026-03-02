export default function Hero({ onExplore }) {
    return (
        <section className="hero">
            <div className="hero-content">
                <p className="hero-subtitle">Sparse-View X-ray 3D Reconstruction</p>
                <h1>
                    <span className="gradient-text">SAX-NeRF</span> Interactive Demo
                </h1>
                <p className="hero-description">
                    Explore 3D CT reconstructions from sparse X-ray views using
                    Structure-Aware Neural Radiance Fields. Select a scene below
                    and watch as AI reconstructs its full 3D volume from just 50 X-ray images.
                </p>
                <div className="hero-cta">
                    <button className="btn btn-primary" onClick={onExplore}>
                        🔬 Explore Scenes
                    </button>
                    <a
                        className="btn btn-secondary"
                        href="https://arxiv.org/abs/2311.10959"
                        target="_blank"
                        rel="noreferrer"
                    >
                        📄 Read Paper
                    </a>
                </div>
            </div>
        </section>
    );
}
