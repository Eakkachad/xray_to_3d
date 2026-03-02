import { useState, useEffect, useRef, useCallback } from 'react';
import Navbar from './components/Navbar.jsx';
import Hero from './components/Hero.jsx';
import SceneGallery from './components/SceneGallery.jsx';
import ResultPanel from './components/ResultPanel.jsx';
import LoadingOverlay from './components/LoadingOverlay.jsx';
import Footer from './components/Footer.jsx';
import { fetchScenes, startInference, checkJobStatus } from './api/client.js';

export default function App() {
    const [scenes, setScenes] = useState([]);
    const [activeScene, setActiveScene] = useState(null);
    const [status, setStatus] = useState('idle'); // idle | loading | running | done | error
    const [progress, setProgress] = useState('');
    const [error, setError] = useState('');
    const resultRef = useRef(null);
    const pollRef = useRef(null);

    // Load available scenes on mount
    useEffect(() => {
        fetchScenes()
            .then((data) => setScenes(data.scenes))
            .catch((err) => console.error('Failed to load scenes:', err));
    }, []);

    // Cleanup polling on unmount
    useEffect(() => {
        return () => {
            if (pollRef.current) clearInterval(pollRef.current);
        };
    }, []);

    const scrollToResults = () => {
        setTimeout(() => {
            resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
    };

    const pollJobStatus = useCallback((jobId, sceneName) => {
        if (pollRef.current) clearInterval(pollRef.current);

        pollRef.current = setInterval(async () => {
            try {
                const job = await checkJobStatus(jobId);
                setProgress(job.progress || '');

                if (job.status === 'done') {
                    clearInterval(pollRef.current);
                    pollRef.current = null;
                    setStatus('done');
                    // Refresh scenes to update cache status
                    fetchScenes().then((data) => setScenes(data.scenes));
                } else if (job.status === 'error') {
                    clearInterval(pollRef.current);
                    pollRef.current = null;
                    setStatus('error');
                    setError(job.error || 'An unknown error occurred');
                }
            } catch (err) {
                console.error('Poll error:', err);
            }
        }, 2000);
    }, []);

    const handleSelectScene = async (scene) => {
        if (!scene.ready) return;

        setActiveScene(scene);
        setStatus('loading');
        setProgress('');
        setError('');

        try {
            const result = await startInference(scene.name);

            if (result.status === 'done') {
                // Cached result — show immediately
                setStatus('done');
                scrollToResults();
            } else {
                // Running in background — start polling
                setStatus('running');
                scrollToResults();
                pollJobStatus(result.job_id, scene.name);
            }
        } catch (err) {
            setStatus('error');
            setError(err.message);
        }
    };

    const handleExplore = () => {
        document.getElementById('gallery')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <>
            <Navbar />
            <main>
                <Hero onExplore={handleExplore} />

                <SceneGallery
                    scenes={scenes}
                    activeScene={activeScene}
                    onSelect={handleSelectScene}
                />

                {/* Results Section */}
                {activeScene && (
                    <section className="section" ref={resultRef}>
                        <div className="container">
                            {status === 'loading' && (
                                <LoadingOverlay progress="Connecting to server..." />
                            )}

                            {status === 'running' && (
                                <LoadingOverlay progress={progress} />
                            )}

                            {status === 'done' && (
                                <ResultPanel scene={activeScene.name} />
                            )}

                            {status === 'error' && (
                                <div className="empty-state fade-in">
                                    <span style={{ fontSize: '3rem' }}>⚠️</span>
                                    <h3 style={{ marginTop: 'var(--space-md)', color: 'var(--color-red)' }}>
                                        Inference Error
                                    </h3>
                                    <p style={{ marginTop: 'var(--space-sm)' }}>{error}</p>
                                    <button
                                        className="btn btn-secondary"
                                        style={{ marginTop: 'var(--space-lg)' }}
                                        onClick={() => handleSelectScene(activeScene)}
                                    >
                                        🔄 Retry
                                    </button>
                                </div>
                            )}
                        </div>
                    </section>
                )}

                <Footer />
            </main>
        </>
    );
}
