# src/data_preprocessor.py
from pathlib import Path
import pandas as pd
import numpy as np
from src.data_loader import BrentDataLoader


class BrentDataPreprocessor:
    """
    OOP class for cleaning and feature engineering of Brent oil price data.
    
    Takes either a pre-loaded DataFrame or loads the data itself,
    then provides methods for cleaning and adding financial/time-series features.
    """

    def __init__(
        self,
        df: pd.DataFrame | None = None,
        data_path: str | Path | None = None,
    ):
        """
        Initialize preprocessor with either a DataFrame or a path to load from.
        
        Args:
            df: Pre-loaded pandas DataFrame (optional)
            data_path: Path to CSV file (optional). 
                       If None, defaults to ../data/BrentOilPrices.csv 
                       relative to this file's location.
        """
        if df is not None:
            self.df = df.copy()
        else:
            if data_path is None:
                # Resolve path relative to project structure: src/ → root → data/
                project_root = Path(__file__).resolve().parent.parent
                data_path = project_root / "data" / "BrentOilPrices.csv"

            loader = BrentDataLoader(data_path=str(data_path))
            self.df = loader.load()


    def clean(self) -> pd.DataFrame:
        """
        Perform basic data cleaning:
          - Check for non-positive prices
          - Remove duplicate index values (dates), keeping first occurrence
        
        Returns:
            Cleaned DataFrame (also stored in self.df)
        """
        if self.df['Price'].le(0).any():
            raise ValueError("Negative or zero prices detected in the data.")

        if self.df.index.duplicated().any():
            print("Removing duplicate dates (keeping first occurrence)...")
            self.df = self.df[~self.df.index.duplicated(keep='first')]

        return self.df


    def add_features(self, focus_period: str | None = None) -> pd.DataFrame:
        """
        Add common time-series features for financial analysis:
          - log_price
          - log_return (daily)
          - rolling_vol_30d (annualized 30-day rolling volatility)
        
        Optionally subset the data to start from focus_period (e.g. '2012-01-01').
        
        Args:
            focus_period: Start date for subsetting (inclusive), e.g. '2012-01-01'
        
        Returns:
            Processed DataFrame (also stored in self.df)
        """
        df = self.clean().copy()  # work on a copy to avoid side-effects

        df['log_price'] = np.log(df['Price'])
        df['log_return'] = df['log_price'].diff()

        # Annualized rolling volatility (assuming 252 trading days/year)
        df['rolling_vol_30d'] = (
            df['log_return']
            .rolling(window=30, min_periods=30)
            .std()
            * np.sqrt(252)
        )

        if focus_period is not None:
            try:
                df = df.loc[focus_period:]
                print(f"Subset to >= {focus_period}: {len(df)} observations remain")
            except KeyError:
                print(f"Warning: focus_period '{focus_period}' not found in index. "
                      "Returning full dataset.")

        self.df = df
        return df


    def get_processed(
        self,
        focus_period: str = '2012-01-01'
    ) -> pd.DataFrame:
        """
        Convenience method: run full cleaning + feature engineering pipeline.
        
        Args:
            focus_period: Start date for subsetting (default: '2012-01-01')
        
        Returns:
            Fully processed DataFrame
        """
        return self.add_features(focus_period=focus_period)