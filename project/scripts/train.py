# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse, os, json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

import matplotlib
matplotlib.use('Agg')

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()
    # add arguments
    parser.add_argument("--input_data", type=str, help="input data")
    parser.add_argument("--output_dir", type=str, help="output dir", default="./outputs")
    # parse args
    args = parser.parse_args()

    return args

# define functions
def main(args):
        
    lines = [
        f"Training data path: {args.input_data}",
        f"output dir path: {args.output_dir}"
    ]
    for line in lines:
        print(line)

    diabetes_data = np.loadtxt(args.input_data, delimiter=',',skiprows=1)
    X=diabetes_data[:,:-1]
    y=diabetes_data[:,-1]
    #columns = ['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    with mlflow.start_run():

        run_id = mlflow.active_run().info.run_id
        mlflow.autolog(log_models=False, exclusive=True)
        print('run_id = ', run_id)

        mlflow.log_metric("Training samples", len(X_train))
        mlflow.log_metric("Test samples", len(X_test))

        # Log the algorithm parameter alpha to the run
        mlflow.log_metric('alpha', 0.03)
        # Create, fit, and test the scikit-learn Ridge regression model
        regression_model = Ridge(alpha=0.03)
        regression_model.fit(X_train, y_train)
        preds = regression_model.predict(X_test)

        # Log mean squared error
        mse = mean_squared_error(y_test, preds)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, preds)

        mlflow.log_metric('mse', mse)
        mlflow.log_metric('rmse', rmse)
        mlflow.log_metric('R2', r2)

        # Plot actuals vs predictions and save the plot within the run
        plt.figure(figsize=(10, 7))

        #scatterplot of y_test and preds
        plt.scatter(y_test, preds) 
        plt.plot(y_test, y_test, color='r')

        plt.title('Actual VS Predicted Values (Test set)') 
        plt.xlabel('Actual Values') 
        plt.ylabel('Predicted Values')

        plt.savefig('actuals_vs_predictions.png')
        mlflow.log_artifact("actuals_vs_predictions.png")

        # Finally save the model to the outputs directory for capture
        os.makedirs(os.path.join(args.output_dir, 'models'), exist_ok=True)
        mlflow.sklearn.save_model(regression_model, os.path.join(args.output_dir, 'models'))

        metric = {}
        metric['run_id'] = run_id
        metric['RMSE'] = rmse
        metric['R2'] = r2
        print(metric)

        with open(os.path.join(args.output_dir, 'metric.json'), "w") as outfile:
            json.dump(metric, outfile)

        mlflow.log_artifacts(args.output_dir)

# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)
