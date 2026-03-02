export default function Footer() {
    return (
        <footer className="footer">
            <div className="container">
                <p>
                    SAX-NeRF — Structure-Aware Sparse-View X-ray 3D Reconstruction
                </p>
                <p style={{ marginTop: 'var(--space-sm)' }}>
                    <a href="https://arxiv.org/abs/2311.10959" target="_blank" rel="noreferrer">Paper</a>
                    {' · '}
                    <a href="https://github.com/caiyuanhao1998/SAX-NeRF" target="_blank" rel="noreferrer">GitHub</a>
                    {' · '}
                    CVPR 2024 — Yuanhao Cai et al.
                </p>
            </div>
        </footer>
    );
}
