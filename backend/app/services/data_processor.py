"""
Data preprocessing pipeline for XGBoost model training.
Handles Kaggle crop recommendation dataset and feature engineering.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Comprehensive data preprocessing pipeline for crop recommendation dataset.
    Handles data loading, cleaning, feature engineering, and preparation for XGBoost.
    """
    
    def __init__(self):
        """Initialize data preprocessor."""
        self.feature_mappings = {
            # Kaggle dataset columns to our system columns
            'N': 'nitrogen',
            'P': 'phosphorus', 
            'K': 'potassium',
            'temperature': 'temperature',
            'humidity': 'humidity',
            'ph': 'soil_ph',
            'rainfall': 'rainfall',
            'label': 'crop'
        }
        
        # Feature ranges for validation
        self.feature_ranges = {
            'nitrogen': (0, 300),
            'phosphorus': (0, 150),
            'potassium': (0, 250),
            'temperature': (8, 50),
            'humidity': (10, 100),
            'soil_ph': (3.5, 10),
            'rainfall': (20, 300)
        }
        
        # Crop mapping for standardization
        self.crop_standardization = {
            'rice': 'Rice',
            'maize': 'Maize', 
            'chickpea': 'Chickpea',
            'kidneybeans': 'Kidney Beans',
            'pigeonpeas': 'Pigeon Peas',
            'mothbeans': 'Moth Beans',
            'mungbean': 'Mung Bean',
            'blackgram': 'Black Gram',
            'lentil': 'Lentil',
            'pomegranate': 'Pomegranate',
            'banana': 'Banana',
            'mango': 'Mango',
            'grapes': 'Grapes',
            'watermelon': 'Watermelon',
            'muskmelon': 'Muskmelon',
            'apple': 'Apple',
            'orange': 'Orange',
            'papaya': 'Papaya',
            'coconut': 'Coconut',
            'cotton': 'Cotton',
            'jute': 'Jute',
            'coffee': 'Coffee'
        }
        
        # Jharkhand-relevant crops mapping
        self.jharkhand_crop_mapping = {
            'Rice': 'Rice',
            'Maize': 'Maize',
            'Chickpea': 'Chickpea',
            'Pigeon Peas': 'Arhar',  # Common name in Jharkhand
            'Lentil': 'Masur',
            'Mung Bean': 'Moong',
            'Black Gram': 'Urad',
            'Cotton': 'Cotton',
            # Additional Jharkhand crops
            'Wheat': 'Wheat',
            'Sugarcane': 'Sugarcane',
            'Potato': 'Potato',
            'Onion': 'Onion',
            'Tomato': 'Tomato'
        }
        
        logger.info("DataPreprocessor initialized")
    
    def load_kaggle_dataset(self, csv_path: str) -> pd.DataFrame:
        """
        Load and validate Kaggle crop recommendation dataset.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Cleaned and validated DataFrame
        """
        logger.info(f"Loading dataset from {csv_path}")
        
        try:
            # Load the dataset
            df = pd.read_csv(csv_path)
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            
            # Display basic info
            logger.info(f"Columns: {list(df.columns)}")
            logger.info(f"Sample data:\n{df.head()}")
            
            # Validate expected columns
            expected_columns = set(self.feature_mappings.keys())
            actual_columns = set(df.columns)
            
            if not expected_columns.issubset(actual_columns):
                missing_cols = expected_columns - actual_columns
                logger.warning(f"Missing expected columns: {missing_cols}")
                
                # Try alternative column names
                df = self._handle_column_mapping(df)
            
            # Standardize column names
            df = df.rename(columns=self.feature_mappings)
            
            # Basic data validation
            df = self._validate_and_clean_data(df)
            
            logger.info(f"Dataset preprocessing complete. Final shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _handle_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle alternative column names in the dataset."""
        # Check for common alternative names
        alt_mappings = {
            'Nitrogen': 'N',
            'Phosphorus': 'P',
            'Potassium': 'K',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'pH': 'ph',
            'Rainfall': 'rainfall',
            'Label': 'label',
            'crop': 'label'
        }
        
        for alt_name, standard_name in alt_mappings.items():
            if alt_name in df.columns and standard_name not in df.columns:
                df = df.rename(columns={alt_name: standard_name})
                logger.info(f"Mapped column {alt_name} -> {standard_name}")
        
        return df
    
    def _validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean the dataset."""
        logger.info("Validating and cleaning data...")
        
        initial_rows = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        missing_counts = df.isnull().sum()
        if missing_counts.any():
            logger.warning(f"Missing values found:\n{missing_counts[missing_counts > 0]}")
            df = df.dropna()  # For simplicity, drop rows with missing values
        
        # Validate feature ranges
        for feature, (min_val, max_val) in self.feature_ranges.items():
            if feature in df.columns:
                outliers = (df[feature] < min_val) | (df[feature] > max_val)
                outlier_count = outliers.sum()
                if outlier_count > 0:
                    logger.warning(f"Found {outlier_count} outliers in {feature}")
                    # Cap outliers instead of removing them
                    df[feature] = df[feature].clip(min_val, max_val)
        
        # Standardize crop names
        if 'crop' in df.columns:
            df['crop'] = df['crop'].str.lower().map(self.crop_standardization)
            df = df.dropna(subset=['crop'])  # Remove unmapped crops
        
        logger.info(f"Data validation complete. Rows remaining: {len(df)}")
        return df
    
    def engineer_features(self, df: pd.DataFrame, include_weather: bool = False) -> pd.DataFrame:
        """
        Engineer additional features for better model performance.
        
        Args:
            df: Input DataFrame
            include_weather: Whether to include weather-based features
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        
        df_engineered = df.copy()
        
        # Basic nutrient ratios
        if all(col in df.columns for col in ['nitrogen', 'phosphorus', 'potassium']):
            df_engineered['npk_ratio'] = (
                df['nitrogen'] + df['phosphorus'] + df['potassium']
            ) / 3
            df_engineered['np_ratio'] = df['nitrogen'] / (df['phosphorus'] + 1)
            df_engineered['nk_ratio'] = df['nitrogen'] / (df['potassium'] + 1)
            df_engineered['pk_ratio'] = df['phosphorus'] / (df['potassium'] + 1)
        
        # Climate indices
        if all(col in df.columns for col in ['temperature', 'humidity']):
            df_engineered['temperature_humidity_index'] = (
                df['temperature'] * df['humidity'] / 100
            )
            
        if all(col in df.columns for col in ['rainfall', 'temperature']):
            df_engineered['rainfall_temperature_ratio'] = (
                df['rainfall'] / df['temperature']
            )
        
        # Soil suitability index
        if 'soil_ph' in df.columns:
            # Most crops prefer pH 6.0-7.5
            df_engineered['ph_optimality'] = 1 - abs(df['soil_ph'] - 6.75) / 3.25
            df_engineered['ph_optimality'] = df_engineered['ph_optimality'].clip(0, 1)
        
        # Water stress index
        if all(col in df.columns for col in ['rainfall', 'humidity', 'temperature']):
            df_engineered['water_stress_index'] = (
                (100 - df['humidity']) * df['temperature'] / df['rainfall']
            )
        
        # Growing degree days approximation
        if 'temperature' in df.columns:
            base_temp = 10  # Base temperature for most crops
            df_engineered['growing_degree_days'] = np.maximum(
                df['temperature'] - base_temp, 0
            )
        
        # Nutrient deficiency indicators
        if all(col in df.columns for col in ['nitrogen', 'phosphorus', 'potassium']):
            # Based on typical crop requirements
            df_engineered['nitrogen_adequacy'] = np.minimum(df['nitrogen'] / 80, 1)
            df_engineered['phosphorus_adequacy'] = np.minimum(df['phosphorus'] / 40, 1)
            df_engineered['potassium_adequacy'] = np.minimum(df['potassium'] / 50, 1)
        
        # Season categorization based on temperature and rainfall
        if all(col in df.columns for col in ['temperature', 'rainfall']):
            conditions = [
                (df['rainfall'] > 150) & (df['temperature'] > 25),  # Kharif-like
                (df['rainfall'] < 80) & (df['temperature'] < 25),   # Rabi-like
                (df['rainfall'] < 50) & (df['temperature'] > 30)    # Summer-like
            ]
            choices = ['kharif_like', 'rabi_like', 'summer_like']
            df_engineered['season_type'] = np.select(conditions, choices, default='moderate')
        
        new_features = set(df_engineered.columns) - set(df.columns)
        logger.info(f"Engineered {len(new_features)} new features: {list(new_features)}")
        
        return df_engineered
    
    def prepare_for_training(
        self, 
        df: pd.DataFrame, 
        target_column: str = 'crop',
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str], LabelEncoder]:
        """
        Prepare dataset for XGBoost training.
        
        Args:
            df: Preprocessed DataFrame
            target_column: Name of target column
            test_size: Fraction for test set
            random_state: Random state for reproducibility
            
        Returns:
            X_train, X_test, y_train, y_test, feature_names, label_encoder
        """
        logger.info("Preparing data for training...")
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Get feature names
        feature_names = list(X.columns)
        
        # Encode categorical features if any
        categorical_features = X.select_dtypes(include=['object']).columns
        for col in categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            logger.info(f"Encoded categorical feature: {col}")
        
        # Encode target variable
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X.values, y_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=y_encoded  # Ensure balanced split
        )
        
        logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
        logger.info(f"Features: {len(feature_names)}")
        logger.info(f"Classes: {len(label_encoder.classes_)}")
        logger.info(f"Crop classes: {list(label_encoder.classes_)}")
        
        return X_train, X_test, y_train, y_test, feature_names, label_encoder
    
    def augment_with_jharkhand_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Augment dataset with Jharkhand-specific data patterns.
        
        Args:
            df: Original dataset
            
        Returns:
            Augmented dataset with Jharkhand-specific patterns
        """
        logger.info("Augmenting with Jharkhand-specific data...")
        
        # Jharkhand climate characteristics
        jharkhand_modifiers = {
            'temperature': (20, 35),      # Typical temperature range
            'humidity': (60, 85),         # Higher humidity
            'rainfall': (800, 1400),      # Monsoon-dependent
            'soil_ph': (5.5, 7.5)        # Slightly acidic to neutral
        }
        
        # Generate Jharkhand-specific samples
        n_augment = min(500, len(df) // 4)  # Add 25% more data
        augmented_samples = []
        
        for crop in df['crop'].unique():
            if crop in self.jharkhand_crop_mapping.values():
                crop_data = df[df['crop'] == crop]
                n_crop_samples = max(10, n_augment // len(df['crop'].unique()))
                
                for _ in range(n_crop_samples):
                    # Sample base data from existing crop data
                    base_sample = crop_data.sample(1).iloc[0].copy()
                    
                    # Apply Jharkhand modifications
                    for feature, (min_val, max_val) in jharkhand_modifiers.items():
                        if feature in base_sample.index:
                            # Add some noise while keeping within Jharkhand ranges
                            current_val = base_sample[feature]
                            noise = np.random.normal(0, 0.1 * current_val)
                            new_val = np.clip(current_val + noise, min_val, max_val)
                            base_sample[feature] = new_val
                    
                    augmented_samples.append(base_sample)
        
        if augmented_samples:
            augmented_df = pd.DataFrame(augmented_samples)
            combined_df = pd.concat([df, augmented_df], ignore_index=True)
            logger.info(f"Added {len(augmented_samples)} Jharkhand-specific samples")
            return combined_df
        
        return df
    
    def get_feature_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive feature statistics."""
        stats = {
            'dataset_size': len(df),
            'feature_count': len(df.columns) - 1,  # Excluding target
            'crop_distribution': df['crop'].value_counts().to_dict() if 'crop' in df.columns else {},
            'feature_ranges': {},
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict()
        }
        
        # Calculate feature ranges for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col != 'crop':
                stats['feature_ranges'][col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
        
        return stats


# Create global instance for easy access
data_preprocessor = DataPreprocessor()