export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="container">
                <a href="#" className="navbar-brand">
                    <div className="logo-icon">🩻</div>
                    SAX-NeRF
                </a>
                <ul className="navbar-links">
                    <li><a href="#gallery">Gallery</a></li>
                    <li><a href="https://arxiv.org/abs/2311.10959" target="_blank" rel="noreferrer">Paper</a></li>
                    <li><a href="https://github.com/caiyuanhao1998/SAX-NeRF" target="_blank" rel="noreferrer">GitHub</a></li>
                    <li><span className="navbar-badge">CVPR 2024</span></li>
                </ul>
            </div>
        </nav>
    );
}
