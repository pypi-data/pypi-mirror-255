from typing import Dict

import numpy as np


def evaluate_graph_predictions(
    pred: np.ndarray,
    true: np.ndarray,
    num_stations: int,
) -> Dict[str, float]:
    """Evaluate the predictions for a single graph."""
    metrics = {
        "station_level": {},
        "index_level": {},
    }

    # get metrics across all stations
    station_preds = pred[:num_stations]
    station_true = true[:num_stations]
    valid_mask = station_true > 0

    # compute the mean absolute error
    mae = np.mean(np.abs(station_preds[valid_mask] - station_true[valid_mask]))
    # compute the root mean squared error
    rmse = np.sqrt(
        np.mean(np.square(station_preds[valid_mask] -
                          station_true[valid_mask])))
    # compute the mean absolute percentage error
    mape = np.mean(
        np.abs((station_preds[valid_mask] - station_true[valid_mask]) /
               station_true[valid_mask])) * 100
    # compute the r2 score
    r2 = 1 - (np.sum(
        np.square(station_preds[valid_mask] - station_true[valid_mask])) /
              np.sum(
                  np.square(station_true[valid_mask] -
                            np.mean(station_true[valid_mask]))))

    # update the metrics dictionary
    # get metrics across all h3 indices
    metrics["station_level"]["mae"] = mae
    metrics["station_level"]["rmse"] = rmse
    metrics["station_level"]["mape"] = mape
    metrics["station_level"]["r2"] = r2

    # get metrics across all h3 indices
    valid_mask = true > 0

    # compute the mean absolute error
    mae = np.mean(np.abs(pred[valid_mask] - true[valid_mask]))
    # compute the root mean squared error
    rmse = np.sqrt(np.mean(np.square(pred[valid_mask] - true[valid_mask])))
    # compute the mean absolute percentage error
    mape = np.mean(
        np.abs((pred[valid_mask] - true[valid_mask]) / true[valid_mask])) * 100
    # compute the r2 score
    r2 = 1 - (np.sum(np.square(pred[valid_mask] - true[valid_mask])) /
              np.sum(np.square(true[valid_mask] - np.mean(true[valid_mask]))))

    # update the metrics dictionary
    metrics["index_level"]["mae"] = mae
    metrics["index_level"]["rmse"] = rmse
    metrics["index_level"]["mape"] = mape
    metrics["index_level"]["r2"] = r2

    return metrics
