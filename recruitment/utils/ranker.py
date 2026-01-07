import joblib
import pandas as pd
import numpy as np
import os
import re
from django.conf import settings

class Ranker:
    def __init__(self):
        self.model_dir = os.path.join(settings.BASE_DIR, 'recruitment', 'data')
        self.model = None
        self.preprocessor = None
        self.tfidf = None
        self.label_encoder = None
        self.initialized = False
        self._load_models()

    def _load_models(self):
        try:
            rf_path = os.path.join(self.model_dir, 'rf_model.pkl')
            if os.path.exists(rf_path):
                self.model = joblib.load(rf_path)
                self.preprocessor = joblib.load(os.path.join(self.model_dir, 'preprocessor.pkl'))
                self.tfidf = joblib.load(os.path.join(self.model_dir, 'tfidf.pkl'))
                self.label_encoder = joblib.load(os.path.join(self.model_dir, 'label_encoder.pkl'))
                self.initialized = True
                print("Resume Ranking Models loaded successfully.")
            else:
                print("Resume Ranking Models not found. Please train the model first.")
        except Exception as e:
            print(f"Error loading models: {e}")

    def _extract_features(self, text):
        """
        Heuristic extraction of structured features from resume text.
        """
        text_lower = text.lower()
        
        # Education Extraction (Regex for common degrees)
        education_keywords = ['b.tech', 'm.tech', 'bca', 'mca', 'bsc', 'msc', 'phd', 'bachelor', 'master', 'diploma']
        education = 'Unknown'
        for deg in education_keywords:
            if deg in text_lower:
                education = deg.upper() # normalization might be needed to match training data
                break
        
        # Simple/Naive Job Role match (This should effectively be the target role)
        # For now, we return a placeholder. The model's OneHot will likely ignore it if unknown.
        job_role = 'Developer' 
        if 'data scientist' in text_lower: job_role = 'Data Scientist'
        elif 'python' in text_lower: job_role = 'Python Developer'
        elif 'java' in text_lower: job_role = 'Java Developer'
        elif 'web' in text_lower: job_role = 'Web Developer'
        
        return {
            'Education': education,
            'Certifications': 'None', # Difficult to extract without NER
            'Job Role': job_role,
            'Skills': text
        }

    def rank_resumes(self, resumes, requirements):
        """
        resumes: List of dictionaries [{'filename': 'name', 'text': 'content'}, ...]
        requirements: String containing job requirements (used here as context if needed)
        """
        if not resumes:
            return []

        # fallback if model not loaded
        if not self.initialized:
            print("Model not initialized, returning empty results.")
            return []

        results = []
        
        # Prepare Data for Prediction
        data_records = []
        for resume in resumes:
            features = self._extract_features(resume['text'])
            data_records.append(features)
        
        df = pd.DataFrame(data_records)
        
        try:
            # 1. TF-IDF feature generation
            # Transform 'Skills' using the loaded vectorizer
            skills_tfidf = self.tfidf.transform(df['Skills'])
            skills_tfidf_df = pd.DataFrame(
                skills_tfidf.toarray(), 
                columns=['skill_tfidf_' + col for col in self.tfidf.get_feature_names_out()]
            )
            
            # 2. Integrate features
            # Drop Skills as in training
            df_processed = pd.concat([df.drop('Skills', axis=1), skills_tfidf_df], axis=1)
            
            # 3. Preprocessing (OneHot + Passthrough)
            # The preprocessor expects the exact same columns as training (minus dropped ones)
            # We need to ensure df_processed has the columns the preprocessor expects.
            # ColumnTransformer is robust if columns map correctly by name.
            
            X_encoded = self.preprocessor.transform(df_processed)
            
            # 4. Prediction
            # Probabilities for class 1 (Hire)
            # Check classes_ to be sure index 1 is 'Hire' or similar positive class
            # Assuming encoded classes [0, 1] or ['Hire', 'Reject'] -> [0, 1]
            # Usually label encoder sorts alphabetically: Hire, Reject -> Hire=0, Reject=1?
            # Or Reject, Hire? 
            # Recruiter Decision: Hire, Reject. 
            # H comes before R. So 0=Hire, 1=Reject.
            # Wait, usually we want probability of "Hire".
            # If 0=Hire, we want proba[:, 0].
            # I should verify this mapping.
            
            # For now, assume a higher score is better.
            scores = self.model.predict_proba(X_encoded)
            
            # Determine which index corresponds to 'Hire' (or positive sentiment)
            # If label encoder classes are ['Hire', 'Reject'], then index 0 is Hire.
            # If we want "Hire" probability, we take index 0.
            # If ['Reject', 'Hire'], index 1 is Hire.
            # Let's inspect classes if possible, but safely assume we want the 'Hire' class.
            
            positive_idx = 0
            if 'Hire' in self.label_encoder.classes_:
                positive_idx = list(self.label_encoder.classes_).index('Hire')
            elif '1' in self.label_encoder.classes_:
                positive_idx = list(self.label_encoder.classes_).index('1')
            
            hire_probs = scores[:, positive_idx]
            
            for i, resume in enumerate(resumes):
                results.append({
                    'filename': resume['filename'],
                    'score': float(hire_probs[i]), # ensure native float
                    'text': resume['text']
                })
                
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            print(f"Prediction failed: {e}")
            return []

        return results