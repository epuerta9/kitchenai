# Introduction to Machine Learning

Machine learning (ML) is a subset of artificial intelligence (AI) that enables systems to learn and improve from experience without being explicitly programmed.

## Types of Machine Learning

1. **Supervised Learning**
   - Training with labeled data.
   - Examples: Linear Regression, Decision Trees, Neural Networks.

2. **Unsupervised Learning**
   - Training with unlabeled data.
   - Examples: K-Means Clustering, Principal Component Analysis (PCA).

3. **Reinforcement Learning**
   - Learning through interaction and rewards.
   - Examples: Q-Learning, Deep Q Networks (DQN).

---

## Key Concepts

### Features and Labels
- **Features:** The input variables used to make predictions.
- **Labels:** The output variable or target.

### Model Evaluation Metrics
- **Accuracy:** Proportion of correct predictions.
- **Precision:** Proportion of true positives among positive predictions.
- **Recall:** Proportion of true positives out of actual positives.
- **F1 Score:** Harmonic mean of precision and recall.

---

## Tools and Libraries
- **Python Libraries:** scikit-learn, TensorFlow, PyTorch
- **Cloud Platforms:** AWS SageMaker, Google Vertex AI, Azure ML

---

## Code Example (Python)

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict and evaluate
predictions = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, predictions))
