# src/data_loader.py
import pandas as pd
from pathlib import Path


class BrentDataLoader:
    """
    OOP class for loading Brent oil price data.
    Handles path resolution, date parsing, and basic validation.
    """
    def __init__(self, data_path=None):
        """
        Initialize the loader.
        
        Args:
            data_path (str or Path, optional): Path to the CSV file.
                If None, defaults to ../data/BrentOilPrices.csv relative to this file.
        """
        if data_path is None:
            # Go from src/ → project root → data/BrentOilPrices.csv
            project_root = Path(__file__).resolve().parent.parent
            data_path = project_root / "data" / "BrentOilPrices.csv"
        
        self.data_path = Path(data_path)
        
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Data file not found at: {self.data_path}\n"
                f"Expected location: /root/data/BrentOilPrices.csv"
            )


    def load_raw(self) -> pd.DataFrame:
        """
        Load raw CSV with flexible date parsing.
        Returns: pd.DataFrame with 'Date' as index (not yet parsed).
        """
        df = pd.read_csv(self.data_path)
        print(f"Raw data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        return df


    def load(self) -> pd.DataFrame:
        """
        Load and parse dates properly.
        Handles mixed formats robustly:
          - Older: '20-May-87'     → %d-%b-%y
          - Newer: '"Jul 15, 2021"' → %b %d, %Y (after stripping quotes)
        """
        df = self.load_raw()

        # Keep cleaned original date strings for multiple parsing attempts
        cleaned_dates = df['Date'].astype(str).str.strip('"').str.strip()

        # First attempt: Older format (dd-mmm-yy)
        df['Date'] = pd.to_datetime(
            cleaned_dates,
            format='%d-%b-%y',
            errors='coerce'
        )

        # Mask for failed parses (mostly newer dates)
        mask = df['Date'].isna()

        if mask.any():
            # Second attempt on failed ones: Newer format (Month dd, yyyy)
            df.loc[mask, 'Date'] = pd.to_datetime(
                cleaned_dates[mask],
                format='%b %d, %Y',
                errors='coerce'
            )

        # Final diagnostic + check
        remaining_mask = df['Date'].isna()
        if remaining_mask.any():
            bad_dates = df.loc[remaining_mask, 'Date'].unique()
            print("WARNING: These date strings could not be parsed:")
            print(bad_dates)
            raise ValueError(
                f"Some dates could not be parsed. Examples: {bad_dates[:10]}"
            )

        # Sort, index, and finalize
        df = df.sort_values('Date').reset_index(drop=True)
        df = df.set_index('Date')

        print(
            f"Data loaded successfully: "
            f"{df.index.min().date()} to {df.index.max().date()}"
        )
        print(f"Total observations: {len(df)}")

        return df