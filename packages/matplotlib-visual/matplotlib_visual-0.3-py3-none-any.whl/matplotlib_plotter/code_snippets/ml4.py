# Importing libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
# Load the Iris dataset
iris = load_iris()
X = iris.data
y = iris.target
# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
# Create a Decision Tree classifier
classifier = DecisionTreeClassifier(random_state=42)
# Train the classifier on the training set
classifier.fit(X_train, y_train)
# Make predictions on the testing set
y_pred = classifier.predict(X_test)
# Evaluate the performance of the classifier
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)
# Display results
print(f"Accuracy: {accuracy:.2f}")
print("Confusion Matrix:")
print(conf_matrix)
print("Classification Report:")
print(class_report)
# Viiualize the Decision Tree (optional)
from sklearn.tree import plot_tree
plt.figure(figsize=(12, 8))
plot_tree(classifier, feature_names=iris.feature_names, class_names=iris.target_names, filled=True)
plt.show()