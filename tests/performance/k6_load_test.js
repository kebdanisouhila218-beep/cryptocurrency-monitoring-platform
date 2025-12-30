// tests/performance/k6_load_test.js
/**
 * Tests de performance avec k6 pour CryptoTracker API
 * 
 * Installation: https://k6.io/docs/getting-started/installation/
 * 
 * Usage:
 *   k6 run k6_load_test.js
 *   k6 run --vus 50 --duration 30s k6_load_test.js
 *   k6 run --out json=results.json k6_load_test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ===== CONFIGURATION =====
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Métriques personnalisées
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const pricesDuration = new Trend('prices_duration');
const successfulRequests = new Counter('successful_requests');

// Options de test
export const options = {
    // Scénarios de charge
    scenarios: {
        // Test de charge progressive
        load_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '30s', target: 10 },   // Montée à 10 utilisateurs
                { duration: '1m', target: 10 },    // Maintien à 10
                { duration: '30s', target: 50 },   // Montée à 50
                { duration: '1m', target: 50 },    // Maintien à 50
                { duration: '30s', target: 0 },    // Descente à 0
            ],
            gracefulRampDown: '10s',
        },
    },
    
    // Seuils de performance
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% < 500ms, 99% < 1s
        http_req_failed: ['rate<0.05'],                   // Moins de 5% d'erreurs
        errors: ['rate<0.1'],                             // Moins de 10% d'erreurs custom
        login_duration: ['p(95)<1000'],                   // Login < 1s
        prices_duration: ['p(95)<500'],                   // Prix < 500ms
    },
};

// ===== HELPERS =====

function getAuthToken() {
    const loginRes = http.post(`${BASE_URL}/auth/login`, {
        username: 'admin',
        password: 'admin123',
    }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    loginDuration.add(loginRes.timings.duration);
    
    if (loginRes.status === 200) {
        return JSON.parse(loginRes.body).access_token;
    }
    return null;
}

function authHeaders(token) {
    return {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    };
}

// ===== TESTS =====

export default function () {
    let token = null;
    
    // ===== Tests API Publiques =====
    group('Public API', function () {
        // Health check
        const healthRes = http.get(`${BASE_URL}/health`);
        check(healthRes, {
            'health status 200': (r) => r.status === 200,
            'health response time < 100ms': (r) => r.timings.duration < 100,
        });
        errorRate.add(healthRes.status !== 200);
        if (healthRes.status === 200) successfulRequests.add(1);
        
        // Root endpoint
        const rootRes = http.get(`${BASE_URL}/`);
        check(rootRes, {
            'root status 200': (r) => r.status === 200,
        });
        
        // Public stats
        const statsRes = http.get(`${BASE_URL}/public/stats`);
        check(statsRes, {
            'public stats status 200': (r) => r.status === 200,
        });
        
        sleep(0.5);
    });
    
    // ===== Authentification =====
    group('Authentication', function () {
        const loginRes = http.post(`${BASE_URL}/auth/login`, {
            username: 'admin',
            password: 'admin123',
        }, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        
        const loginSuccess = check(loginRes, {
            'login status 200': (r) => r.status === 200,
            'login has token': (r) => JSON.parse(r.body).access_token !== undefined,
            'login response time < 500ms': (r) => r.timings.duration < 500,
        });
        
        loginDuration.add(loginRes.timings.duration);
        errorRate.add(!loginSuccess);
        
        if (loginRes.status === 200) {
            token = JSON.parse(loginRes.body).access_token;
            successfulRequests.add(1);
        }
        
        sleep(0.3);
    });
    
    // ===== Tests API Protégées =====
    if (token) {
        group('Protected API - Prices', function () {
            // Get prices
            const pricesRes = http.get(`${BASE_URL}/prices`, authHeaders(token));
            check(pricesRes, {
                'prices status 200': (r) => r.status === 200,
                'prices has data': (r) => JSON.parse(r.body).prices !== undefined,
                'prices response time < 500ms': (r) => r.timings.duration < 500,
            });
            pricesDuration.add(pricesRes.timings.duration);
            if (pricesRes.status === 200) successfulRequests.add(1);
            
            // Latest prices
            const latestRes = http.get(`${BASE_URL}/prices/latest?limit=10`, authHeaders(token));
            check(latestRes, {
                'latest prices status 200': (r) => r.status === 200,
            });
            
            sleep(0.5);
        });
        
        group('Protected API - User', function () {
            // User info
            const meRes = http.get(`${BASE_URL}/auth/me`, authHeaders(token));
            check(meRes, {
                'me status 200': (r) => r.status === 200,
                'me has username': (r) => JSON.parse(r.body).username !== undefined,
            });
            if (meRes.status === 200) successfulRequests.add(1);
            
            sleep(0.3);
        });
        
        group('Protected API - Alerts', function () {
            // Get alerts
            const alertsRes = http.get(`${BASE_URL}/alerts`, authHeaders(token));
            check(alertsRes, {
                'alerts status 200': (r) => r.status === 200,
            });
            if (alertsRes.status === 200) successfulRequests.add(1);
            
            sleep(0.3);
        });
        
        group('Protected API - Portfolio', function () {
            // Get virtual portfolios
            const portfolioRes = http.get(`${BASE_URL}/virtual-portfolio`, authHeaders(token));
            check(portfolioRes, {
                'portfolio status 200': (r) => r.status === 200,
            });
            if (portfolioRes.status === 200) successfulRequests.add(1);
            
            sleep(0.3);
        });
        
        group('Protected API - Analytics', function () {
            // Heatmap
            const heatmapRes = http.get(`${BASE_URL}/analytics/heatmap`, authHeaders(token));
            check(heatmapRes, {
                'heatmap status 200': (r) => r.status === 200,
            });
            
            // Candlestick
            const candleRes = http.get(`${BASE_URL}/analytics/candlestick/BTC`, authHeaders(token));
            check(candleRes, {
                'candlestick status 200': (r) => r.status === 200,
            });
            
            // Predictions
            const predRes = http.get(`${BASE_URL}/predictions/indicators/BTC`, authHeaders(token));
            check(predRes, {
                'predictions status 200': (r) => r.status === 200,
            });
            
            sleep(0.5);
        });
    }
    
    sleep(1);
}

// ===== RAPPORT =====

export function handleSummary(data) {
    console.log('');
    console.log('='.repeat(60));
    console.log('📊 RÉSUMÉ DES TESTS DE PERFORMANCE K6');
    console.log('='.repeat(60));
    console.log(`✅ Requêtes réussies: ${data.metrics.successful_requests?.values?.count || 0}`);
    console.log(`❌ Taux d'erreur: ${(data.metrics.errors?.values?.rate * 100 || 0).toFixed(2)}%`);
    console.log(`⏱️  Durée moyenne: ${(data.metrics.http_req_duration?.values?.avg || 0).toFixed(2)}ms`);
    console.log(`⏱️  P95: ${(data.metrics.http_req_duration?.values['p(95)'] || 0).toFixed(2)}ms`);
    console.log(`⏱️  P99: ${(data.metrics.http_req_duration?.values['p(99)'] || 0).toFixed(2)}ms`);
    console.log('='.repeat(60));
    
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'results/k6_summary.json': JSON.stringify(data, null, 2),
    };
}

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
