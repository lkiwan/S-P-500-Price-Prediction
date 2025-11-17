"""
Database utilities for storing predictions persistently
Works with PostgreSQL on Render or falls back to CSV for local development
"""

import os
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class PredictionDatabase:
    """Handle prediction storage - PostgreSQL or CSV fallback"""

    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.use_postgres = bool(self.database_url)

        if self.use_postgres:
            # Fix for Render's postgres:// URL (psycopg2 needs postgresql://)
            if self.database_url.startswith('postgres://'):
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)

            logger.info("Using PostgreSQL for data storage")
            self._init_postgres()
        else:
            logger.info("Using CSV files for data storage (local mode)")
            self.predictions_file = 'predictions_history.csv'
            self.accuracy_file = 'predictions_with_accuracy.csv'

    def _init_postgres(self):
        """Initialize PostgreSQL tables"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    prediction_date TIMESTAMP NOT NULL,
                    data_date DATE NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    confidence FLOAT NOT NULL,
                    prob_up FLOAT NOT NULL,
                    prob_down FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create accuracy table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_accuracy (
                    id SERIAL PRIMARY KEY,
                    prediction_date TIMESTAMP NOT NULL,
                    data_date DATE NOT NULL,
                    predicted_direction VARCHAR(10) NOT NULL,
                    confidence FLOAT NOT NULL,
                    actual_direction VARCHAR(10),
                    actual_return FLOAT,
                    is_correct BOOLEAN,
                    current_price FLOAT,
                    next_price FLOAT,
                    next_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_data_date
                ON predictions(data_date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_accuracy_data_date
                ON prediction_accuracy(data_date)
            """)

            conn.commit()
            cursor.close()
            conn.close()

            logger.info("PostgreSQL tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing PostgreSQL: {e}")
            raise

    def save_prediction(self, prediction_data):
        """Save a new prediction"""
        if self.use_postgres:
            return self._save_prediction_postgres(prediction_data)
        else:
            return self._save_prediction_csv(prediction_data)

    def _save_prediction_postgres(self, data):
        """Save prediction to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO predictions
                (prediction_date, data_date, direction, confidence, prob_up, prob_down)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data['prediction_date'],
                data['data_date'],
                data['direction'],
                data['confidence'],
                data['prob_up'],
                data['prob_down']
            ))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Error saving prediction to PostgreSQL: {e}")
            return False

    def _save_prediction_csv(self, data):
        """Save prediction to CSV file"""
        try:
            new_record = pd.DataFrame([data])

            if os.path.exists(self.predictions_file):
                df = pd.read_csv(self.predictions_file)
                df = pd.concat([df, new_record], ignore_index=True)
            else:
                df = new_record

            df.to_csv(self.predictions_file, index=False)
            return True

        except Exception as e:
            logger.error(f"Error saving prediction to CSV: {e}")
            return False

    def get_predictions(self, limit=None):
        """Get prediction history"""
        if self.use_postgres:
            return self._get_predictions_postgres(limit)
        else:
            return self._get_predictions_csv(limit)

    def _get_predictions_postgres(self, limit=None):
        """Get predictions from PostgreSQL"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = "SELECT * FROM predictions ORDER BY prediction_date DESC"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Error fetching predictions from PostgreSQL: {e}")
            return pd.DataFrame()

    def _get_predictions_csv(self, limit=None):
        """Get predictions from CSV"""
        try:
            if os.path.exists(self.predictions_file):
                df = pd.read_csv(self.predictions_file)
                df = df.sort_values('prediction_date', ascending=False)
                if limit:
                    df = df.head(limit)
                return df
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error reading predictions from CSV: {e}")
            return pd.DataFrame()

    def save_accuracy(self, accuracy_data):
        """Save prediction accuracy data"""
        if self.use_postgres:
            return self._save_accuracy_postgres(accuracy_data)
        else:
            return self._save_accuracy_csv(accuracy_data)

    def _save_accuracy_postgres(self, data):
        """Save accuracy to PostgreSQL"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO prediction_accuracy
                (prediction_date, data_date, predicted_direction, confidence,
                 actual_direction, actual_return, is_correct, current_price, next_price, next_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['prediction_date'],
                data['data_date'],
                data['predicted_direction'],
                data['confidence'],
                data['actual_direction'],
                data['actual_return'],
                data['is_correct'],
                data['current_price'],
                data['next_price'],
                data['next_date']
            ))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Error saving accuracy to PostgreSQL: {e}")
            return False

    def _save_accuracy_csv(self, data):
        """Save accuracy to CSV"""
        try:
            new_record = pd.DataFrame([data])

            if os.path.exists(self.accuracy_file):
                df = pd.read_csv(self.accuracy_file)
                df = pd.concat([df, new_record], ignore_index=True)
            else:
                df = new_record

            df.to_csv(self.accuracy_file, index=False)
            return True

        except Exception as e:
            logger.error(f"Error saving accuracy to CSV: {e}")
            return False

    def get_accuracy_data(self):
        """Get prediction accuracy data"""
        if self.use_postgres:
            return self._get_accuracy_postgres()
        else:
            return self._get_accuracy_csv()

    def _get_accuracy_postgres(self):
        """Get accuracy from PostgreSQL"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("SELECT * FROM prediction_accuracy ORDER BY prediction_date DESC")
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Error fetching accuracy from PostgreSQL: {e}")
            return pd.DataFrame()

    def _get_accuracy_csv(self):
        """Get accuracy from CSV"""
        try:
            if os.path.exists(self.accuracy_file):
                return pd.read_csv(self.accuracy_file)
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error reading accuracy from CSV: {e}")
            return pd.DataFrame()

    def prediction_exists_today(self, data_date):
        """Check if prediction already exists for today"""
        if self.use_postgres:
            return self._prediction_exists_postgres(data_date)
        else:
            return self._prediction_exists_csv(data_date)

    def _prediction_exists_postgres(self, data_date):
        """Check PostgreSQL for existing prediction"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM predictions
                WHERE data_date = %s
                AND DATE(prediction_date) = CURRENT_DATE
            """, (data_date,))

            count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return count > 0

        except Exception as e:
            logger.error(f"Error checking existing prediction in PostgreSQL: {e}")
            return False

    def _prediction_exists_csv(self, data_date):
        """Check CSV for existing prediction"""
        try:
            if not os.path.exists(self.predictions_file):
                return False

            df = pd.read_csv(self.predictions_file)
            df['data_date'] = pd.to_datetime(df['data_date']).dt.date
            df['prediction_date'] = pd.to_datetime(df['prediction_date']).dt.date

            today = datetime.now().date()
            data_date_obj = pd.to_datetime(data_date).date()

            exists = ((df['data_date'] == data_date_obj) &
                     (df['prediction_date'] == today)).any()

            return exists

        except Exception as e:
            logger.error(f"Error checking existing prediction in CSV: {e}")
            return False
