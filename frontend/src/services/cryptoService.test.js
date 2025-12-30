// frontend/src/services/cryptoService.test.js
/**
 * Tests unitaires pour le service crypto
 */
import cryptoService from './cryptoService';
import axios from 'axios';
import authService from './authService';

jest.mock('axios');
jest.mock('./authService');

describe('CryptoService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    authService.getAuthHeader.mockReturnValue({
      Authorization: 'Bearer test-token'
    });
  });

  describe('getAllCryptos', () => {
    it('should fetch all cryptos successfully', async () => {
      const mockData = {
        prices: [
          {
            symbol: 'BTC',
            name: 'Bitcoin',
            price_usd: 94000,
            volume_24h: 28000000000
          },
          {
            symbol: 'ETH',
            name: 'Ethereum',
            price_usd: 3500,
            volume_24h: 15000000000
          }
        ],
        count: 2
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getAllCryptos();

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalled();
    });

    it('should handle 401 error and trigger logout', async () => {
      axios.get.mockRejectedValue({
        response: { status: 401 }
      });

      authService.logout = jest.fn();

      await expect(cryptoService.getAllCryptos()).rejects.toThrow();
    });

    it('should handle network error', async () => {
      axios.get.mockRejectedValue(new Error('Network Error'));

      await expect(cryptoService.getAllCryptos()).rejects.toThrow('Network Error');
    });
  });

  describe('getCryptoBySymbol', () => {
    it('should fetch specific crypto by symbol', async () => {
      const mockData = {
        symbol: 'BTC',
        name: 'Bitcoin',
        price_usd: 94000,
        volume_24h: 28000000000,
        market_cap: 1800000000000
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getCryptoBySymbol('BTC');

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('BTC'),
        expect.any(Object)
      );
    });

    it('should handle 404 for unknown symbol', async () => {
      axios.get.mockRejectedValue({
        response: { status: 404, data: { detail: 'Crypto not found' } }
      });

      await expect(cryptoService.getCryptoBySymbol('UNKNOWN')).rejects.toThrow();
    });
  });

  describe('getLatestPrices', () => {
    it('should fetch latest prices with limit', async () => {
      const mockData = {
        prices: [
          { symbol: 'BTC', price_usd: 94000 },
          { symbol: 'ETH', price_usd: 3500 }
        ],
        pagination: { limit: 10, offset: 0, total: 50 }
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getLatestPrices(10);

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('limit'),
        expect.any(Object)
      );
    });
  });

  describe('getPredictions', () => {
    it('should fetch predictions for a crypto', async () => {
      const mockData = {
        symbol: 'BTC',
        predictions: {
          sma: { value: 95000, confidence: 0.85 },
          ema: { value: 94800, confidence: 0.88 },
          linear_regression: { value: 96200, confidence: 0.82 },
          optimal: { value: 95300, confidence: 0.87 }
        },
        period_days: 90
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getPredictions('BTC', 90);

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('predictions'),
        expect.any(Object)
      );
    });

    it('should handle insufficient data error', async () => {
      axios.get.mockRejectedValue({
        response: { status: 400, data: { detail: 'Insufficient data' } }
      });

      await expect(cryptoService.getPredictions('NEW_COIN', 90)).rejects.toThrow();
    });
  });

  describe('getIndicators', () => {
    it('should fetch technical indicators', async () => {
      const mockData = {
        symbol: 'BTC',
        indicators: {
          rsi: { value: 65.4, signal: 'NEUTRAL' },
          macd: { macd: 125.3, signal: 98.7, histogram: 26.6, signal_type: 'BUY' },
          bollinger_bands: { upper: 96000, middle: 94500, lower: 93000 }
        }
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getIndicators('BTC', 90);

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('indicators'),
        expect.any(Object)
      );
    });
  });

  describe('getCandlestickData', () => {
    it('should fetch candlestick data', async () => {
      const mockData = {
        symbol: 'BTC',
        interval: '1h',
        data: [
          { timestamp: '2024-12-29T09:00:00Z', open: 94000, high: 94500, low: 93800, close: 94300 }
        ]
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getCandlestickData('BTC', '1h', 7);

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('candlestick'),
        expect.any(Object)
      );
    });
  });

  describe('getHeatmap', () => {
    it('should fetch heatmap data', async () => {
      const mockData = {
        period: '24h',
        data: [
          { symbol: 'BTC', change_percent: 2.5 },
          { symbol: 'ETH', change_percent: -1.2 }
        ],
        top_gainers: [{ symbol: 'SOL', change_percent: 8.5 }],
        top_losers: [{ symbol: 'ADA', change_percent: -3.2 }]
      };

      axios.get.mockResolvedValue({ data: mockData });

      const result = await cryptoService.getHeatmap('24h');

      expect(result).toBeDefined();
      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('heatmap'),
        expect.any(Object)
      );
    });
  });
});

describe('Data Formatting', () => {
  describe('formatPrice', () => {
    it('should format price with currency symbol', () => {
      const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(price);
      };

      expect(formatPrice(94000)).toBe('$94,000.00');
      expect(formatPrice(3500.50)).toBe('$3,500.50');
    });

    it('should handle small prices', () => {
      const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 2,
          maximumFractionDigits: 6
        }).format(price);
      };

      expect(formatPrice(0.00001234)).toContain('0.00001');
    });
  });

  describe('formatPercent', () => {
    it('should format positive percentage with plus sign', () => {
      const formatPercent = (value) => {
        const sign = value >= 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
      };

      expect(formatPercent(5.5)).toBe('+5.50%');
      expect(formatPercent(-3.2)).toBe('-3.20%');
    });
  });

  describe('formatVolume', () => {
    it('should format large volumes with abbreviations', () => {
      const formatVolume = (volume) => {
        if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
        if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
        if (volume >= 1e3) return `$${(volume / 1e3).toFixed(2)}K`;
        return `$${volume.toFixed(2)}`;
      };

      expect(formatVolume(28000000000)).toBe('$28.00B');
      expect(formatVolume(1500000)).toBe('$1.50M');
      expect(formatVolume(5000)).toBe('$5.00K');
    });
  });
});
