from django.core.management.base import BaseCommand
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings

class Command(BaseCommand):
    help = 'Trains the Random Forest Resume Ranking Model'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting model training...")
        
        # Define paths
        base_dir = settings.BASE_DIR
        data_path = os.path.join(base_dir, 'recruitment', 'data', 'AI_Resume_Screening.csv')
        model_dir = os.path.join(base_dir, 'recruitment', 'data')
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f"Data file not found at {data_path}"))
            self.stdout.write(self.style.WARNING("Please upload 'AI_Resume_Screening.csv' to recruitment/data/"))
            return

        # 1. Load Data
        df = pd.read_csv(data_path)
        self.stdout.write(f"Loaded {len(df)} records.")

        # 2. TF-IDF on Skills
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        skills_tfidf_matrix = tfidf_vectorizer.fit_transform(df['Skills'])
        skills_tfidf_df = pd.DataFrame(
            skills_tfidf_matrix.toarray(), 
            columns=['skill_tfidf_' + col for col in tfidf_vectorizer.get_feature_names_out()]
        )

        # 3. Integrate Features
        df_processed = pd.concat([df.drop('Skills', axis=1), skills_tfidf_df], axis=1)

        # 4. Define X and y
        # Adjust features as per dataset
        drop_cols = ['Resume_ID', 'Name', 'Recruiter Decision']
        # Ensure these columns exist
        available_drop_cols = [col for col in drop_cols if col in df_processed.columns]
        X = df_processed.drop(available_drop_cols, axis=1)
        y = df_processed['Recruiter Decision']

        # 5. Encode Target
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # 6. Preprocessing (OneHot)
        # Fill missing
        X['Certifications'] = X['Certifications'].fillna('None')
        
        categorical_features = ['Education', 'Certifications', 'Job Role']
        # Filter categorical features that might not exist in X
        categorical_features = [col for col in categorical_features if col in X.columns]
        
        passthrough_features = [col for col in X.columns if col not in categorical_features]

        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
                ('passthrough', 'passthrough', passthrough_features)
            ]
        )

        X_processed = preprocessor.fit_transform(X)

        # 7. Train Model
        self.stdout.write("Training Random Forest Classifier...")
        model = RandomForestClassifier(random_state=42)
        model.fit(X_processed, y_encoded)

        # 8. Save Artifacts
        joblib.dump(model, os.path.join(model_dir, 'rf_model.pkl'))
        joblib.dump(preprocessor, os.path.join(model_dir, 'preprocessor.pkl'))
        joblib.dump(tfidf_vectorizer, os.path.join(model_dir, 'tfidf.pkl'))
        joblib.dump(label_encoder, os.path.join(model_dir, 'label_encoder.pkl'))
        
        # Save feature columns to help with inference alignment if needed
        # (Though column transformer handles most of it, we need to know input columns)
        joblib.dump(X.columns.tolist(), os.path.join(model_dir, 'feature_columns.pkl'))

        self.stdout.write(self.style.SUCCESS(f"Model trained and saved to {model_dir}"))
