import torch
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns

def predict(model, dataloader):
    model.eval()
    
    predictions = []
    actuals = []
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred_scores = model(X)
            predicted, actual = pred_scores.argmax(1), y
            predictions.append(predicted.numpy())
            actuals.append(actual.numpy())

    df = pd.DataFrame({
        "predicted": np.concatenate(predictions),
        "actual": np.concatenate(actuals),
    })
    return df

def confusion(predictions, classes):
    cm = confusion_matrix(predictions["actual"], predictions["predicted"])

    plt.figure()
    ax = sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")

    return ax