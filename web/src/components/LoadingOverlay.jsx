export default function LoadingOverlay({ progress }) {
    return (
        <div className="loading-overlay">
            <div className="loading-spinner" />
            <div className="loading-text">Reconstructing 3D volume...</div>
            {progress && <div className="loading-progress">{progress}</div>}
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', maxWidth: '400px', textAlign: 'center' }}>
                The neural network is processing X-ray projections to build a complete 3D CT volume.
                This may take a few minutes on the first run.
            </p>
        </div>
    );
}
