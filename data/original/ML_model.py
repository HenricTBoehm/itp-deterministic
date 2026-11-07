from typing import Any
import pandas as pd
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, StackingRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression, Perceptron, Ridge
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.multioutput import MultiOutputRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPRegressor
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor


def check_lengths(arrays: dict) -> None:
    lengths = {key: len(value) for key, value in arrays.items()}
    if len(set(lengths.values())) > 1:
        print(lengths)
        raise ValueError("All arrays must be of the same length")
    

def input_data() -> pd.DataFrame : 
    # Variablen für die Daten
    slab_thickness : int[30] = [150, 200, 200, 150, 200, 150, 200, 130, 130, 150, 
                       200, 130, 130, 150, 200, 130, 150, 150, 150, 150, 
                       150, 200, 130, 130, 200, 130, 150, 200, 130, 200]
    ceiling_thickness : int[30] = [11, 14, 14, 14, 14, 11, 16.5, 16.5, 14, 16.5, 
                          16.5, 11, 16.5, 11, 14, 14, 11, 11, 11, 11, 16.5, 
                          16.5, 14, 11, 11, 11, 16.5, 16.5, 14, 11]
    ex_wall_thickness : int[30] = [200, 150, 150, 150, 200, 200, 150, 200, 150, 200, 
                          250, 200, 200, 150, 200, 150, 250, 200, 200, 200, 
                          250, 200, 200, 150, 150, 150, 150, 150, 250, 250]
    in_wall_thickness : int[30] = [150, 150, 150, 100, 100, 100, 100, 150, 100, 200, 
                          100, 200, 200, 200, 100, 200, 200, 150, 200, 150, 
                          150, 150, 200, 150, 200, 150, 100, 150, 100, 200]
    ex_win_area : float[30] = [1.8, 1.8, 2.1, 2.1, 1.8, 1.8, 1.8, 1.8, 2.1, 1.8, 2.1, 
                    1.8, 1.8, 1.5, 2.1, 2.1, 1.8, 1.8, 1.8, 1.8, 1.5, 1.8, 
                    2.1, 2.1, 1.8, 1.8, 1.8, 1.8, 1.8, 1.5]
    ex_win_layers : int[30] = [2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 
                      2, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1]
    prim_door_area : float[30] = [3.96, 3.52, 4.4, 4.4, 3.96, 4.4, 4.4, 4.4, 3.96, 4.4, 
                       4.4, 3.96, 4.4, 3.96, 4.4, 4.4, 3.96, 3.96, 3.96, 3.96, 
                       3.52, 3.96, 3.52, 3.96, 3.96, 3.96, 3.96, 3.96, 3.96, 
                       3.96]
    sec_door_area : float[30] = [1.26, 1.68, 1.68, 1.26, 1.26, 1.26, 1.26, 1.26, 1.68, 
                      1.26, 1.68, 1.68, 1.26, 1.68, 1.68, 1.68, 1.68, 1.68, 
                      1.68, 1.68, 1.26, 1.68, 1.68, 1.68, 1.68, 1.68, 1.68, 
                      1.68, 1.68, 1.26]
    window_g_value : float[30] = [0.87, 0.87, 0.7, 0.7, 0.87, 0.7, 0.87, 0.87, 0.7, 0.7, 
                                  0.7, 0.87, 0.7, 0.87, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 
                                  0.87, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
    window_u_value : float[30] = [3.01, 3.01, 2.8, 2.8, 3.01, 2.8, 3.01, 3.01, 2.8, 2.8, 
                                  2.8, 3.01, 2.8, 3.01, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 
                                  3.01, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8, 2.8]

    # Erstellen eines DataFrames mit den Daten
    data  : dict[str, Any] = {
        'slab_thickness': slab_thickness,
        'ceiling_thickness': ceiling_thickness,
        'ex_wall_thickness': ex_wall_thickness,
        'in_wall_thickness': in_wall_thickness,
        'ex_win_area': ex_win_area,
        'ex_win_layers': ex_win_layers,
        'prim_door_area': prim_door_area,
        'sec_door_area': sec_door_area,
        'window_g_value': window_g_value,
        'window_u_value': window_u_value
    }

    # Überprüfen der Längen der Arrays
    check_lengths(data)
    
    df: pd.DataFrame = pd.DataFrame(data)

    # Exportieren des DataFrames in eine CSV-Datei
    df.to_csv('building_data.csv', index=False)

    return df


def input_output() -> pd.DataFrame : 
    # Die Werte für den Output
    energy_requirement : float[30] = [22688.102, 23861.6832, 23859.006, 25316.238, 23022.892, 23172.942, 
                               24983.143, 22550.133, 25357.733, 22772.907, 22679.721, 22308.465, 
                               22821.129, 23518.069, 23928.036, 23942.982, 24711.759, 22058.46, 
                               22214.658, 23678.067, 21817.472, 23159.262, 22189.173, 24079.786, 
                               24153.804, 24604.922, 23470.556, 24841.554, 21836.148, 21489.245]
    energy_losses : float[30] = [1282.381, 1408.189, 1597.467, 3245.01, 1327.051, 1276.432, 2705.106, 
                          1274.038, 3240.836, 2666.802, 3210.935, 1272.441, 2648.337, 1361.941, 
                          3224.918, 2160.649, 2747.71, 1469.074, 1279.267, 3219.737, 2070.682, 
                          2658.712, 1273.917, 1355.751, 2704.972, 1349.086, 3227.318, 2367.138, 
                          1220.4, 2076.622]
    heat_gain : float[30] = [1375.282, 1464.641, 1790.218, 4360.541, 1470.36, 1375.857, 3533.284, 
                      1375.121, 4631.209, 3536.087, 4371.967, 1373.461, 3525.179, 1373.831, 
                      4377.178, 2682.957, 3523.699, 1790.509, 1374.112, 4368.247, 2693.81, 
                      3530.605, 1373.8, 1374.222, 3515.808, 1374.984, 4369.871, 3055.922, 
                      1372.777, 2683.91]
    cO2_emission : float[30] = [245.302, 257.605, 257.577, 272.854, 248.812, 250.385, 269.362, 
                         243.855, 273.289, 246.191, 245.214, 241.322, 246.696, 254.003, 
                         258.301, 258.457, 266.517, 238.701, 240.339, 255.68, 236.175, 
                         250.241, 240.071, 259.892, 260.667, 265.397, 253.505, 267.877, 
                         236.37, 232.734]
    
    # Erstellen eines DataFrames für Y
    output  : dict[str, Any] = {
        'Energy_requirement': energy_requirement,
        'Energy_losses': energy_losses,
        'Heat_gain': heat_gain,
        'CO2_emission': cO2_emission
    }

    # Überprüfen der Längen der Arrays
    check_lengths(output)

    df_y = pd.DataFrame(output)

    # Speichern des DataFrames in eine CSV-Datei
    df_y.to_csv('output_values.csv', index=False)

    return df_y


def train_model(df, df_y):
    # Normalisieren der Eingangsmerkmale
    scaler_X = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(df)

    # Normalisieren der Zielvariablen
    scaler_y = MinMaxScaler()
    y_scaled = scaler_y.fit_transform(df_y)

    # Aufteilen der Daten in Trainings- und Testdaten
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

    # Definieren Sie den Parameterbereich, den Sie durchsuchen möchten
    param_grid = {
        'hidden_layer_sizes': [(50,50)],
        'learning_rate_init': [0.0135, 0.0125, 0.013],
        'solver': ['sgd'],
        'alpha': [0.002, 0.0025],
        'batch_size': [4],
    }

    # Initialisieren Sie Grid Search
    # grid_search = GridSearchCV(MLPRegressor(max_iter=500, random_state=42), param_grid, cv=5, scoring='neg_mean_squared_error')

    # Führen Sie Grid Search aus
    # grid_search.fit(X_train, y_train)

    # Finden Sie das Modell mit den besten Parametern
    # best_model = grid_search.best_estimator_
    # print(best_model)

    # Initialisieren und Trainieren des MLPRegressor mit angepassten Parametern
    model = MLPRegressor(hidden_layer_sizes=(50, 50), activation='tanh', solver='sgd', alpha=0.0025,
                         learning_rate='adaptive', learning_rate_init=0.0125, max_iter=500, batch_size=4, random_state=42)

    # model = LinearRegression() # Mean Squared Error: 0.08753638308025861
    
    # Erstellen eines Pipeline-Objekts, das einen StandardScaler und ein SVR-Modell enthält
    model = make_pipeline(LinearRegression()) # Mean Squared Error: 0.0875363830802587

    # Anwenden von Cross-Validation
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
    print(scores)

    # Training des Modells
    model.fit(X_train, y_train)

    # Auswertung des Modells
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')
    mae = mean_absolute_error(y_test, y_pred)
    print(f'Mean Absolute Error: {mae}')

    return model, scaler_X, scaler_y


def save_data(df_processed):
    # Speichern der verarbeiteten Daten
    df_processed.to_csv('processed_data.csv', index=False)
    print('Processed data has been saved.')


def main():
    # Laden der Daten
    df = input_data()
    df_y = input_output()

    # Trainieren des Modells
    model, scaler_X, scaler_y = train_model(df, df_y)

    # Neue Eingabedaten für die Schätzung
    new_input = pd.DataFrame({
        'slab_thickness': [150],
        'ceiling_thickness': [11],
        'ex_wall_thickness': [200],
        'in_wall_thickness': [150],
        'ex_win_area': [1.8],
        'ex_win_layers': [2],
        'prim_door_area': [3.96],
        'sec_door_area': [1.26],
        'window_g_value': [0.7],
        'window_u_value': [2.8]
    })

def main():
    # Laden der Daten
    df = input_data()
    df_y = input_output()

    # Trainieren des Modells
    model, scaler_X, scaler_y = train_model(df, df_y)

    # Neue Eingabedaten für die Schätzung
    new_input = pd.DataFrame({
        'slab_thickness': [200],
        'ceiling_thickness': [11],
        'ex_wall_thickness': [250],
        'in_wall_thickness': [250],
        'ex_win_area': [1.5],
        'ex_win_layers': [1],
        'prim_door_area': [3.96],
        'sec_door_area': [1.68],
        'window_g_value': [0.87],
        'window_u_value': [3.01]
    })

    # Normalisierung der neuen Eingabedaten
    normalized_new_input = scaler_X.transform(new_input)

    # Vorhersage für den Ausgabewert basierend auf den neuen Eingabedaten
    normalized_predicted_output = model.predict(normalized_new_input)

    # print("normalized_predicted_output shape:", normalized_predicted_output.shape)
    # print("scaler_y attributes:", scaler_y.scale_.shape)

    # Umkehrung der Normalisierung des Ausgabewerts, um den geschätzten Ausgabewert im ursprünglichen Skalierungsbereich zu erhalten
    estimated_output = scaler_y.inverse_transform(normalized_predicted_output)

    print("Predicted Output:", estimated_output)

    # Speichern des Modells und der Scaler
    joblib.dump(model, 'window_u_model.pkl')
    joblib.dump(scaler_X, 'scaler_X.pkl')
    joblib.dump(scaler_y, 'scaler_y.pkl')
    print('Model has been saved.')

    # Verarbeiten der Daten und Speichern
    # Hier würde die Verarbeitung der Daten stattfinden
    processed_data = df  # Placeholder für die verarbeiteten Daten, da keine Verarbeitung im Beispiel vorhanden ist
    save_data(processed_data)


if __name__ == "__main__":
    main()
