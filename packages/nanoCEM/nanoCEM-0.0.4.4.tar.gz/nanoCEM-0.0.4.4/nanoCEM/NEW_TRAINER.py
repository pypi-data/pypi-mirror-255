
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import xgboost
import shap
import torch
import torch.nn as nn
import torch.optim as optim


# 5 is time step 4 is the feature number
X = feature_matrix.values.reshape(-1,5,4)
y = label.values
X = torch.from_numpy(X)
y = torch.from_numpy(y).double()
print(1)


class RNNClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(RNNClassifier, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # RNN层
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True).double()
        # 全连接层
        self.fc = nn.Linear(hidden_size, output_size).double()

    def forward(self, x):
        out, _ = self.rnn(x)
        out = self.fc(out[:, -1, :])  # 只使用最后一个时间步的输出
        out = torch.sigmoid(out)
        return out



# 设置模型的输入、隐藏层大小、输出类别数
input_size = 4  # 输入特征的维度
hidden_size = 32  # 隐藏层大小
num_layers = 1  # RNN层数
output_size = 1

# 创建RNN分类器模型实例
model = RNNClassifier(input_size, hidden_size, num_layers, output_size)

# 准备数据和标签
# 定义损失函数和优化器
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)

# 训练模型
num_epochs = 100
batch_size = 32

for epoch in range(num_epochs):
    for i in range(0, len(X), batch_size):
        inputs = X[i:i+batch_size]
        labels = y[i:i+batch_size]

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}')
model.eval()
# 使用训练好的模型进行预测
with torch.no_grad():
    inputs = X  # 使用全部数据进行预测
    predictions = model(inputs)
    predicted_labels = torch.round(predictions).squeeze().long()

    # 计算准确率
    correct = (predicted_labels == y).sum().item()
    total = len(y)
    accuracy = correct / total

    print("Accuracy: "+str(accuracy))

# 打印预测结果
print(predicted_labels)



from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
kfold = KFold(n_splits=5)
# Perform k-fold cross-validation
accuracy_scores=[]
for train_index, test_index in kfold.split(X):
    # Split the data into training and testing sets for each fold
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # Create an XGBoost classifier
    model = xgboost.XGBClassifier()

    # Train the model on the training data
    model.fit(X_train, y_train)

    # Make predictions on the testing data
    y_pred = model.predict(X_test)

    # Calculate the accuracy score
    accuracy = accuracy_score(y_test, y_pred)

    # Store the accuracy score for this fold
    accuracy_scores.append(accuracy)

    # Calculate the average accuracy across all folds
avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
print(avg_accuracy)



y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
# explain the model's predictions using SHAP
# (same syntax works for LightGBM, CatBoost, scikit-learn, transformers, Spark, etc.)
print(accuracy)
y_pred = model.predict_proba(X_test)[:,1]
prediction_df = pd.DataFrame({'y_test': y_test.reshape(-1,), 'y_pred': y_pred})
prediction_df['y_test'] = prediction_df['y_test'].apply(lambda x: 'Sample' if x==1 else 'Control')
import plotnine as p9
category = pd.api.types.CategoricalDtype(categories=['Sample', "Control"], ordered=True)
prediction_df['y_test'] = prediction_df['y_test'].astype(category)
# visualize the first prediction's explanation
plot = p9.ggplot(prediction_df, p9.aes(x='y_test', y="y_pred",fill='y_test')) \
            +p9.scale_fill_manual(values={"Sample": "#F57070", "Control": "#9F9F9F", "Single": "#a3abbd"})\
           + p9.theme_bw() \
           + p9.labs(x='',y='Prediction')\
           + p9.geom_boxplot(width=0.6,alpha=0.7)\
           + p9.theme(
        figure_size=(4, 4),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='none',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),
    )
print(plot)
plot.save(filename=results_path + "/prediction_barplot.pdf", dpi=300)
plot = p9.ggplot(prediction_df, p9.aes(fill='y_test', x="y_pred")) \
    +p9.scale_fill_manual(values={"Sample": "#F57070", "Control": "#9F9F9F", "Single": "#a3abbd"})\
           + p9.theme_bw() \
           + p9.labs(x='Prediction',y='Density')\
           + p9.geom_density(alpha=0.7)\
           + p9.theme(
        figure_size=(4,4),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='bottom',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),
    )
print(plot)

plot.save(filename=results_path + "/prediction_distribution.pdf", dpi=300)


# 示例数据

