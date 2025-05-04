import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

def main():
    # Load training data
    df = pd.read_csv("../social_support_system/data/training_data.csv")

    # Drop rows with missing text or label
    df = df.dropna(subset=["text", "label"])

    X = df["text"]
    y = df["label"]

    # Build a pipeline: TF-IDF + SVM
    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=1000)),
        ("svm", SVC(kernel="linear", probability=True))
    ])

    # Train
    model.fit(X, y)
    print("✅ SVM Classifier trained.")

    # Save model
    with open("models/svm_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("✅ Model saved to models/svm_model.pkl")

if __name__ == "__main__":
    main()
