/**
 * SAX-NeRF API Client
 * Fetch wrapper for backend communication.
 */

const BASE_URL = '/api';

async function request(path, options = {}) {
    const url = `${BASE_URL}${path}`;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API Error: ${res.status}`);
    }

    // Return raw response for file endpoints
    if (options.raw) return res;
    return res.json();
}

/** List all available scenes */
export async function fetchScenes() {
    return request('/scenes');
}

/** Start inference for a scene */
export async function startInference(scene) {
    return request(`/inference/${scene}`, { method: 'POST' });
}

/** Check job status */
export async function checkJobStatus(jobId) {
    return request(`/status/${jobId}`);
}

/** Get metrics for a scene */
export async function fetchMetrics(scene) {
    return request(`/results/${scene}/metrics`);
}

/** Get slice info (total count) for an axis */
export async function fetchSliceInfo(scene, axis) {
    return request(`/results/${scene}/slices/${axis}/info`);
}

/** Get CT slice image URL */
export function getSliceUrl(scene, axis, index) {
    return `${BASE_URL}/results/${scene}/slices/${axis}/${index}`;
}

/** Get 3D GIF URL */
export function getGifUrl(scene) {
    return `${BASE_URL}/results/${scene}/gif`;
}

/** Get projection image URL */
export function getProjectionUrl(scene, type, index) {
    return `${BASE_URL}/results/${scene}/projections/${type}/${index}`;
}

/** Health check */
export async function healthCheck() {
    return request('/health');
}
