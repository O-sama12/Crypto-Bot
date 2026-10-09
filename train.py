
from features import df, feature_columns

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 1. Select features and target
X = df[feature_columns].copy()
y = df["target"].astype(int)

# 2. Split chronologically: older 80% for training,
#    newest 20% for testing
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\n--- TARGET DISTRIBUTION ---")
print("Training targets:")
print(y_train.value_counts().sort_index())
print("\nTesting targets:")
print(y_test.value_counts().sort_index())

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

# 3. Train a simple baseline for comparison
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)

baseline_predictions = baseline.predict(X_test)

# 4. Create and train our ML model
model = HistGradientBoostingClassifier(
    learning_rate=0.05,
    max_iter=100,
    max_leaf_nodes=7,
    l2_regularization=1.0,
    random_state=42,
)

model.fit(X_train, y_train)

# 5. Predict the test period
predictions = model.predict(X_test)


# Inspect model predictions
probabilities = model.predict_proba(X_test)

results = X_test.copy()
results["actual"] = y_test
results["predicted"] = predictions
results["probability_down"] = probabilities[:, 0]
results["probability_up"] = probabilities[:, 1]

print("\n--- PREDICTION COUNTS ---")
print(results["predicted"].value_counts().sort_index())

print("\n--- FIRST 15 TEST PREDICTIONS ---")
print(results[[
    "actual",
    "predicted",
    "probability_down",
    "probability_up",
]].head(15).round(4))

print("\n--- PREDICTION CONFIDENCE ---")
print(
    results[["probability_down", "probability_up"]]
    .max(axis=1)
    .describe()
    .round(4)
)

# 6. Evaluate the baseline and ML model
print("\n--- BASELINE RESULTS ---")
print("Accuracy:", round(
    accuracy_score(y_test, baseline_predictions), 4
))
print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, baseline_predictions), 4
))

print("\n--- ML MODEL RESULTS ---")
print("Accuracy:", round(
    accuracy_score(y_test, predictions), 4
))
print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, predictions), 4
))

print("\nClassification report:")
print(classification_report(
    y_test,
    predictions,
    labels=[0, 1],
    target_names=["Down or unchanged", "Up"],
    zero_division=0,
))

print("Confusion matrix:")
print(confusion_matrix(y_test, predictions, labels=[0, 1]))


# Train a Logistic Regression comparison model
logistic_model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=42),
)

logistic_model.fit(X_train, y_train)
logistic_predictions = logistic_model.predict(X_test)

print("\n--- LOGISTIC REGRESSION RESULTS ---")
print("Accuracy:", round(
    accuracy_score(y_test, logistic_predictions), 4
))
print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, logistic_predictions), 4
))
print("Confusion matrix:")
print(confusion_matrix(
    y_test,
    logistic_predictions,
    labels=[0, 1],
))