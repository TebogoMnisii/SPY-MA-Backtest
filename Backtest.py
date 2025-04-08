import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import os

def prepare_data():
    """Load and clean SPY data"""
    df = pd.read_csv('SPY-CLEAN.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

class SpyStrategy(bt.Strategy):
    params = (('fast', 50), ('slow', 200), ('commission', 0.01))

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(period=self.p.slow)
        
    def next(self):
        if not self.position and self.fast_ma[0] > self.slow_ma[0]:
            self.buy()
        elif self.position and self.fast_ma[0] < self.slow_ma[0]:
            self.close()

def annotate_performance(cerebro, results):
    """Generate annotated performance chart"""
    fig = cerebro.plot(style='candlestick', volume=False)[0][0]
    ax = fig.axes[0]
    
    # Key performance annotation
    ax.text(0.02, 0.95, 
            f"Final Portfolio Value: ${results[0].broker.getvalue():,.2f}\n"
            f"Commission: {results[0].params.commission*100:.0f}%",
            transform=ax.transAxes,
            bbox=dict(facecolor='white', alpha=0.8))
    
    # Save high-res image
    plt.savefig('results/equity_curve.png', dpi=600, bbox_inches='tight')
    plt.close()

def run_backtest():
    cerebro = bt.Cerebro()
    
    # 1. Load data
    df = prepare_data()
    data = bt.feeds.PandasData(dataname=df.set_index('Date'))
    
    # 2. Configure backtest
    cerebro.adddata(data)
    cerebro.addstrategy(SpyStrategy)
    cerebro.broker.setcash(10000.0)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # 3. Run backtest
    print('\n=== BACKTEST STARTED ===')
    print(f'Initial Portfolio Value: ${cerebro.broker.getvalue():,.2f}')
    results = cerebro.run()
    print(f'Final Portfolio Value: ${results[0].broker.getvalue():,.2f}')
    
    # 4. Generate annotated chart
    os.makedirs('results', exist_ok=True)
    annotate_performance(cerebro, results)
    
    return results

if __name__ == '__main__':
    run_backtest()