"""
Demand Forecasting using Prophet
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import joblib
import os

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not installed. Using simple moving average for forecasting.")


class DemandForecaster:
    """
    Time series forecasting for product demand using Facebook Prophet.
    
    Features:
    - Daily/weekly/yearly seasonality detection
    - Holiday effects (Azerbaijan public holidays)
    - Trend analysis
    - Confidence intervals
    """
    
    # Azerbaijan public holidays
    AZ_HOLIDAYS = [
        {'holiday': 'novruz', 'ds': '2024-03-20', 'lower_window': 0, 'upper_window': 4},
        {'holiday': 'novruz', 'ds': '2025-03-20', 'lower_window': 0, 'upper_window': 4},
        {'holiday': 'ramazan', 'ds': '2024-04-10', 'lower_window': 0, 'upper_window': 2},
        {'holiday': 'ramazan', 'ds': '2025-03-30', 'lower_window': 0, 'upper_window': 2},
        {'holiday': 'qurban', 'ds': '2024-06-16', 'lower_window': 0, 'upper_window': 2},
        {'holiday': 'qurban', 'ds': '2025-06-06', 'lower_window': 0, 'upper_window': 2},
        {'holiday': 'newyear', 'ds': '2024-01-01', 'lower_window': -1, 'upper_window': 1},
        {'holiday': 'newyear', 'ds': '2025-01-01', 'lower_window': -1, 'upper_window': 1},
    ]
    
    def __init__(self):
        self.models = {}  # Store separate model per product
        self.training_data = {}  # Store training data for reference
        
    def train(
        self, 
        product_id: str, 
        sales_df: pd.DataFrame,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False
    ) -> Optional['Prophet']:
        """
        Train Prophet model for a product.
        
        Args:
            product_id: Product identifier
            sales_df: DataFrame with columns 'date' and 'quantity'
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            daily_seasonality: Enable daily seasonality
            
        Returns:
            Trained Prophet model or None
        """
        if sales_df.empty:
            print(f"Cannot train for {product_id}: Empty sales data")
            return None
        
        if len(sales_df) < 14:
            print(f"Cannot train for {product_id}: Need at least 14 days of data")
            return None
        
        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_df = sales_df[['date', 'quantity']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Remove any invalid values
        prophet_df = prophet_df.dropna()
        prophet_df = prophet_df[prophet_df['y'] >= 0]
        
        # Store training data
        self.training_data[product_id] = prophet_df.copy()
        
        if PROPHET_AVAILABLE:
            return self._train_prophet(
                product_id, prophet_df,
                yearly_seasonality, weekly_seasonality, daily_seasonality
            )
        else:
            return self._train_simple(product_id, prophet_df)
    
    def _train_prophet(
        self, 
        product_id: str, 
        df: pd.DataFrame,
        yearly_seasonality: bool,
        weekly_seasonality: bool,
        daily_seasonality: bool
    ) -> 'Prophet':
        """Train using Prophet model."""
        # Create holidays dataframe
        holidays = pd.DataFrame(self.AZ_HOLIDAYS)
        holidays['ds'] = pd.to_datetime(holidays['ds'])
        
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality,
            holidays=holidays,
            changepoint_prior_scale=0.05,  # Flexibility of trend
            seasonality_prior_scale=10,
            interval_width=0.8  # 80% confidence interval
        )
        
        # Fit model
        model.fit(df)
        
        # Store model
        self.models[product_id] = {'model': model, 'type': 'prophet'}
        
        print(f"Prophet model trained for product {product_id}")
        print(f"  - Training samples: {len(df)}")
        print(f"  - Date range: {df['ds'].min().date()} to {df['ds'].max().date()}")
        
        return model
    
    def _train_simple(self, product_id: str, df: pd.DataFrame) -> Dict:
        """Train using simple moving average (fallback)."""
        # Calculate statistics
        stats = {
            'mean': df['y'].mean(),
            'std': df['y'].std(),
            'weekly_pattern': df.groupby(df['ds'].dt.dayofweek)['y'].mean().to_dict()
        }
        
        self.models[product_id] = {'stats': stats, 'type': 'simple'}
        
        print(f"Simple model trained for product {product_id}")
        return stats
    
    def forecast(self, product_id: str, periods: int = 7) -> pd.DataFrame:
        """
        Forecast demand for next N days.
        
        Args:
            product_id: Product identifier
            periods: Number of days to forecast
            
        Returns:
            DataFrame with columns: date, predicted_quantity, lower_bound, upper_bound
        """
        if product_id not in self.models:
            raise ValueError(f"Model for product {product_id} not trained")
        
        model_info = self.models[product_id]
        
        if model_info['type'] == 'prophet':
            return self._forecast_prophet(model_info['model'], periods)
        else:
            return self._forecast_simple(model_info['stats'], periods)
    
    def _forecast_prophet(self, model: 'Prophet', periods: int) -> pd.DataFrame:
        """Generate forecast using Prophet."""
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)
        
        # Predict
        forecast = model.predict(future)
        
        # Extract relevant columns
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).copy()
        result.columns = ['date', 'predicted_quantity', 'lower_bound', 'upper_bound']
        
        # Ensure non-negative predictions
        result['predicted_quantity'] = result['predicted_quantity'].clip(lower=0)
        result['lower_bound'] = result['lower_bound'].clip(lower=0)
        result['upper_bound'] = result['upper_bound'].clip(lower=0)
        
        return result.reset_index(drop=True)
    
    def _forecast_simple(self, stats: Dict, periods: int) -> pd.DataFrame:
        """Generate forecast using simple model."""
        forecasts = []
        
        for i in range(periods):
            date = datetime.now() + timedelta(days=i+1)
            day_of_week = date.weekday()
            
            # Get weekly pattern multiplier
            weekly_avg = sum(stats['weekly_pattern'].values()) / 7
            day_factor = stats['weekly_pattern'].get(day_of_week, weekly_avg) / weekly_avg if weekly_avg > 0 else 1
            
            # Calculate prediction
            predicted = stats['mean'] * day_factor
            
            # Add confidence intervals
            std = stats['std']
            
            forecasts.append({
                'date': date,
                'predicted_quantity': max(0, round(predicted, 1)),
                'lower_bound': max(0, round(predicted - 1.5 * std, 1)),
                'upper_bound': max(0, round(predicted + 1.5 * std, 1))
            })
        
        return pd.DataFrame(forecasts)
    
    def detect_stockout_risk(
        self, 
        product_id: str, 
        current_stock: int, 
        periods: int = 7,
        safety_factor: float = 1.2
    ) -> Dict:
        """
        Check if product will run out of stock in next N days.
        
        Args:
            product_id: Product identifier
            current_stock: Current inventory level
            periods: Days to forecast
            safety_factor: Multiplier for safety stock recommendation
            
        Returns:
            Dictionary with stockout risk analysis
        """
        forecast = self.forecast(product_id, periods)
        
        # Calculate cumulative demand
        cumulative_demand = forecast['predicted_quantity'].sum()
        upper_demand = forecast['upper_bound'].sum()  # Worst case
        
        stockout_risk = cumulative_demand > current_stock
        high_risk = upper_demand > current_stock
        
        days_until_stockout = None
        
        if stockout_risk:
            cumsum = 0
            for idx, row in forecast.iterrows():
                cumsum += row['predicted_quantity']
                if cumsum > current_stock:
                    days_until_stockout = idx + 1
                    break
        
        # Calculate recommended order quantity
        recommended_order = max(0, round(cumulative_demand * safety_factor - current_stock))
        
        # Generate recommendation message
        if high_risk:
            recommendation = f"URGENT: Order at least {recommended_order} units immediately"
        elif stockout_risk:
            recommendation = f"Order {recommended_order} units within {days_until_stockout - 1} days"
        else:
            remaining_after = current_stock - cumulative_demand
            if remaining_after < cumulative_demand * 0.3:
                recommendation = f"Consider ordering {recommended_order} units soon"
            else:
                recommendation = "Stock levels are sufficient"
        
        return {
            'stockout_risk': stockout_risk,
            'high_risk': high_risk,
            'days_until_stockout': days_until_stockout,
            'predicted_demand_7d': round(cumulative_demand, 1),
            'upper_bound_demand': round(upper_demand, 1),
            'current_stock': current_stock,
            'recommended_order': recommended_order,
            'recommendation': recommendation,
            'forecast_details': forecast.to_dict('records')
        }
    
    def get_trend_analysis(self, product_id: str) -> Dict:
        """
        Analyze demand trends for a product.
        
        Returns:
            Dictionary with trend analysis
        """
        if product_id not in self.training_data:
            return {'error': 'No training data available'}
        
        df = self.training_data[product_id]
        
        # Calculate basic statistics
        stats = {
            'avg_daily_sales': round(df['y'].mean(), 1),
            'max_daily_sales': int(df['y'].max()),
            'min_daily_sales': int(df['y'].min()),
            'std_deviation': round(df['y'].std(), 1),
            'total_days': len(df)
        }
        
        # Weekly pattern
        weekly = df.groupby(df['ds'].dt.dayofweek)['y'].mean()
        stats['weekly_pattern'] = {
            'Monday': round(weekly.get(0, 0), 1),
            'Tuesday': round(weekly.get(1, 0), 1),
            'Wednesday': round(weekly.get(2, 0), 1),
            'Thursday': round(weekly.get(3, 0), 1),
            'Friday': round(weekly.get(4, 0), 1),
            'Saturday': round(weekly.get(5, 0), 1),
            'Sunday': round(weekly.get(6, 0), 1)
        }
        
        # Peak day
        peak_day = weekly.idxmax()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        stats['peak_day'] = day_names[peak_day]
        
        # Trend direction (last 7 days vs previous 7 days)
        if len(df) >= 14:
            recent = df.tail(7)['y'].mean()
            previous = df.iloc[-14:-7]['y'].mean()
            trend_change = ((recent - previous) / previous * 100) if previous > 0 else 0
            
            if trend_change > 10:
                stats['trend'] = 'increasing'
            elif trend_change < -10:
                stats['trend'] = 'decreasing'
            else:
                stats['trend'] = 'stable'
            stats['trend_change_pct'] = round(trend_change, 1)
        else:
            stats['trend'] = 'insufficient data'
            stats['trend_change_pct'] = 0
        
        return stats
    
    def save_models(self, filepath_prefix: str):
        """Save all trained models to disk."""
        for product_id, model_info in self.models.items():
            filepath = f"{filepath_prefix}_{product_id}.pkl"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            save_data = {
                'model_info': model_info,
                'training_data': self.training_data.get(product_id)
            }
            joblib.dump(save_data, filepath)
        
        print(f"Saved {len(self.models)} models")
    
    def load_model(self, product_id: str, filepath: str):
        """Load model for a specific product from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        save_data = joblib.load(filepath)
        self.models[product_id] = save_data['model_info']
        
        if save_data.get('training_data') is not None:
            self.training_data[product_id] = save_data['training_data']
        
        print(f"Model loaded for product {product_id}")


# Example usage
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    base_demand = 100
    sales_data = []
    
    for date in dates:
        # Base demand with weekly pattern
        day_factor = 1.3 if date.weekday() >= 5 else 1.0  # Weekend spike
        
        # Add some noise
        demand = base_demand * day_factor * np.random.uniform(0.8, 1.2)
        
        sales_data.append({
            'date': date,
            'quantity': int(demand)
        })
    
    sales_df = pd.DataFrame(sales_data)
    
    # Train forecaster
    forecaster = DemandForecaster()
    forecaster.train('MILK_1L', sales_df)
    
    # Generate forecast
    print("\n7-Day Forecast:")
    print("=" * 50)
    forecast = forecaster.forecast('MILK_1L', periods=7)
    print(forecast.to_string(index=False))
    
    # Check stockout risk
    print("\nStockout Risk Analysis:")
    print("=" * 50)
    risk = forecaster.detect_stockout_risk('MILK_1L', current_stock=500)
    print(f"Stockout Risk: {risk['stockout_risk']}")
    print(f"Days Until Stockout: {risk['days_until_stockout']}")
    print(f"Predicted 7-day Demand: {risk['predicted_demand_7d']}")
    print(f"Recommendation: {risk['recommendation']}")
    
    # Trend analysis
    print("\nTrend Analysis:")
    print("=" * 50)
    trend = forecaster.get_trend_analysis('MILK_1L')
    print(f"Average Daily Sales: {trend['avg_daily_sales']}")
    print(f"Peak Day: {trend['peak_day']}")
    print(f"Trend: {trend['trend']} ({trend['trend_change_pct']}%)")
