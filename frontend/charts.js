/**
 * Charts.js - Advanced Charting Functions for Option Chain Analysis
 * Contains specialized chart functions for option data visualization
 */

class OptionCharts {
    constructor() {
        this.colors = {
            bullish: '#28a745',
            bearish: '#dc3545',
            neutral: '#6c757d',
            ce: '#ff6b6b',
            pe: '#51cf66',
            volume: '#ff922b',
            oi: '#339af0'
        };
    }

    /**
     * Create OI Skew Heatmap
     */
    createOISkewHeatmap(strikeData, spotPrice, containerId) {
        const strikes = strikeData.map(s => s.strike);
        const oiSkew = strikeData.map(s => s.oi_skew);
        
        // Create color scale for OI skew
        const colorscale = [
            [0, this.colors.bearish],    // Strong negative (Bearish)
            [0.5, this.colors.neutral],  // Neutral
            [1, this.colors.bullish]     // Strong positive (Bullish)
        ];

        const trace = {
            x: strikes,
            y: oiSkew,
            type: 'scatter',
            mode: 'markers',
            marker: {
                size: 8,
                color: oiSkew,
                colorscale: colorscale,
                showscale: true,
                colorbar: {
                    title: 'OI Skew',
                    titleside: 'right'
                }
            },
            name: 'OI Skew'
        };

        const layout = {
            title: 'OI Skew Heatmap',
            xaxis: { title: 'Strike Price' },
            yaxis: { title: 'OI Skew Ratio' },
            shapes: [
                {
                    type: 'line',
                    x0: spotPrice,
                    x1: spotPrice,
                    y0: Math.min(...oiSkew),
                    y1: Math.max(...oiSkew),
                    line: {
                        color: 'red',
                        width: 2,
                        dash: 'dash'
                    }
                }
            ],
            annotations: [
                {
                    x: spotPrice,
                    y: Math.max(...oiSkew),
                    text: `Spot: ${spotPrice}`,
                    showarrow: true,
                    arrowhead: 7,
                    ax: 0,
                    ay: -40
                }
            ],
            height: 400
        };

        Plotly.newPlot(containerId, [trace], layout);
    }

    /**
     * Create Volume-OI Efficiency Chart
     */
    createVolumeOIEfficiencyChart(strikeData, containerId) {
        const strikes = strikeData.map(s => s.strike);
        const ceEfficiency = strikeData.map(s => s.ce_volume_oi_ratio || 0);
        const peEfficiency = strikeData.map(s => s.pe_volume_oi_ratio || 0);

        const trace1 = {
            x: strikes,
            y: ceEfficiency,
            type: 'bar',
            name: 'CE Volume/OI',
            marker: { color: this.colors.ce }
        };

        const trace2 = {
            x: strikes,
            y: peEfficiency,
            type: 'bar',
            name: 'PE Volume/OI',
            marker: { color: this.colors.pe }
        };

        const layout = {
            title: 'Volume-OI Efficiency Ratio',
            xaxis: { title: 'Strike Price' },
            yaxis: { title: 'Volume / OI Ratio' },
            barmode: 'group',
            height: 400,
            legend: { orientation: 'h', y: -0.2 }
        };

        Plotly.newPlot(containerId, [trace1, trace2], layout);
    }

    /**
     * Create OI Distribution Chart
     */
    createOIDistributionChart(strikeData, spotPrice, containerId) {
        const strikes = strikeData.map(s => s.strike);
        const ceOI = strikeData.map(s => s.ce_oi);
        const peOI = strikeData.map(s => s.pe_oi);

        const trace1 = {
            x: strikes,
            y: ceOI,
            type: 'bar',
            name: 'Call OI',
            marker: { color: this.colors.ce }
        };

        const trace2 = {
            x: strikes,
            y: peOI,
            type: 'bar',
            name: 'Put OI',
            marker: { color: this.colors.pe }
        };

        const layout = {
            title: 'Open Interest Distribution',
            xaxis: { title: 'Strike Price' },
            yaxis: { title: 'Open Interest' },
            barmode: 'overlay',
            height: 400,
            shapes: [
                {
                    type: 'line',
                    x0: spotPrice,
                    x1: spotPrice,
                    y0: 0,
                    y1: Math.max(...ceOI, ...peOI),
                    line: {
                        color: 'red',
                        width: 3,
                        dash: 'dot'
                    }
                }
            ],
            annotations: [
                {
                    x: spotPrice,
                    y: Math.max(...ceOI, ...peOI) * 0.9,
                    text: `Spot: ${spotPrice}`,
                    showarrow: true,
                    arrowhead: 7,
                    bgcolor: 'red',
                    bordercolor: 'red',
                    font: { color: 'white' }
                }
            ]
        };

        Plotly.newPlot(containerId, [trace1, trace2], layout);
    }

    /**
     * Create Buildup Analysis Chart
     */
    createBuildupChart(strikeData, containerId) {
        const strikes = strikeData.map(s => s.strike);
        
        const ceLongBuildup = strikes.map((strike, i) => 
            strikeData[i].ce_buildup === 'LONG' ? strikeData[i].ce_change_oi : 0
        );
        
        const ceShortBuildup = strikes.map((strike, i) => 
            strikeData[i].ce_buildup === 'SHORT' ? strikeData[i].ce_change_oi : 0
        );
        
        const peLongBuildup = strikes.map((strike, i) => 
            strikeData[i].pe_buildup === 'LONG' ? strikeData[i].pe_change_oi : 0
        );
        
        const peShortBuildup = strikes.map((strike, i) => 
            strikeData[i].pe_buildup === 'SHORT' ? strikeData[i].pe_change_oi : 0
        );

        const trace1 = {
            x: strikes,
            y: ceLongBuildup,
            type: 'bar',
            name: 'CE Long Buildup',
            marker: { color: '#2ecc71' }
        };

        const trace2 = {
            x: strikes,
            y: ceShortBuildup,
            type: 'bar',
            name: 'CE Short Buildup',
            marker: { color: '#e74c3c' }
        };

        const trace3 = {
            x: strikes,
            y: peLongBuildup,
            type: 'bar',
            name: 'PE Long Buildup',
            marker: { color: '#27ae60' }
        };

        const trace4 = {
            x: strikes,
            y: peShortBuildup,
            type: 'bar',
            name: 'PE Short Buildup',
            marker: { color: '#c0392b' }
        };

        const layout = {
            title: 'Option Buildup Analysis',
            xaxis: { title: 'Strike Price' },
            yaxis: { title: 'Change in OI' },
            barmode: 'stack',
            height: 500,
            legend: { orientation: 'h', y: -0.3 }
        };

        Plotly.newPlot(containerId, [trace1, trace2, trace3, trace4], layout);
    }

    /**
     * Create PCR Trend Chart (if historical data available)
     */
    createPCRTrendChart(historicalData, containerId) {
        if (!historicalData || historicalData.length === 0) {
            this.showNoDataMessage(containerId);
            return;
        }

        const timestamps = historicalData.map(d => new Date(d.timestamp));
        const pcrValues = historicalData.map(d => d.pcr_oi);

        const trace = {
            x: timestamps,
            y: pcrValues,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'PCR OI',
            line: { color: this.colors.oi },
            marker: { size: 4 }
        };

        // Add reference lines
        const shapes = [
            // Overbought line
            {
                type: 'line',
                x0: timestamps[0],
                x1: timestamps[timestamps.length - 1],
                y0: 1.4,
                y1: 1.4,
                line: { color: 'red', width: 1, dash: 'dash' }
            },
            // Oversold line
            {
                type: 'line',
                x0: timestamps[0],
                x1: timestamps[timestamps.length - 1],
                y0: 0.6,
                y1: 0.6,
                line: { color: 'green', width: 1, dash: 'dash' }
            }
        ];

        const layout = {
            title: 'PCR Trend Analysis',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Put-Call Ratio (OI)' },
            height: 300,
            shapes: shapes,
            annotations: [
                {
                    x: timestamps[timestamps.length - 1],
                    y: 1.4,
                    text: 'Overbought',
                    showarrow: false,
                    bgcolor: 'red',
                    bordercolor: 'red',
                    font: { color: 'white' }
                },
                {
                    x: timestamps[timestamps.length - 1],
                    y: 0.6,
                    text: 'Oversold',
                    showarrow: false,
                    bgcolor: 'green',
                    bordercolor: 'green',
                    font: { color: 'white' }
                }
            ]
        };

        Plotly.newPlot(containerId, [trace], layout);
    }

    /**
     * Create Sentiment Gauge
     */
    createSentimentGauge(sentimentScore, containerId) {
        const gaugeData = [
            {
                domain: { x: [0, 1], y: [0, 1] },
                value: sentimentScore,
                title: { text: "Market Sentiment" },
                type: "indicator",
                mode: "gauge+number",
                gauge: {
                    axis: { range: [0, 100] },
                    steps: [
                        { range: [0, 30], color: "red" },
                        { range: [30, 70], color: "yellow" },
                        { range: [70, 100], color: "green" }
                    ],
                    threshold: {
                        line: { color: "black", width: 4 },
                        thickness: 0.75,
                        value: sentimentScore
                    }
                }
            }
        ];

        const layout = {
            width: 400,
            height: 300,
            margin: { t: 0, b: 0 }
        };

        Plotly.newPlot(containerId, gaugeData, layout);
    }

    /**
     * Show no data message
     */
    showNoDataMessage(containerId) {
        const element = document.getElementById(containerId);
        if (element) {
            element.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="fas fa-chart-bar fa-3x mb-3"></i>
                    <p>No historical data available yet</p>
                    <small>Data will appear after a few refresh cycles</small>
                </div>
            `;
        }
    }

    /**
     * Update all charts for a symbol
     */
    updateAllCharts(symbolData, containerPrefix) {
        if (!symbolData || !symbolData.analysis) return;

        const { strike_data, spot_price, analysis } = symbolData;

        this.createOISkewHeatmap(strike_data, spot_price, `${containerPrefix}-oi-skew`);
        this.createVolumeOIEfficiencyChart(strike_data, `${containerPrefix}-volume-oi`);
        this.createOIDistributionChart(strike_data, spot_price, `${containerPrefix}-oi-dist`);
        this.createBuildupChart(strike_data, `${containerPrefix}-buildup`);
        this.createSentimentGauge(analysis.sentiment_score, `${containerPrefix}-sentiment`);
    }
}

// Initialize charts instance
const optionCharts = new OptionCharts();
