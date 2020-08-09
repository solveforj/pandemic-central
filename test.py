
from model.merge import merge
from model.train import train
from model.predict import predict

# Update data and merge into training dataset:
merge()

# Train model
train()

# Make predictions for website
predict()
