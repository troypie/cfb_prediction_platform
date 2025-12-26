
# filetype imports
import json

# ML imports
import sklearn
from sklearn.model_selection import train_test_split


#custom imports
import get_data
import experiment_coverPredict as cover_experiment
import experiment_scorePredict_update
from eval_engine_sportsbetting import evaluate_experiment


def main():
    # Load embeddings
    filename = 'cfb_embeddings_from_gemini_check_format_correct.json'
    with open(filename, 'r') as file:
        embeddings = json.load(file)

    # Get the data from the API for a specific week
    games, lines = get_data.get_data_gameScores_Lines(2025)
    
    ## Process the data to extract the required information
    X_data, y_data = cover_experiment.prepare_classification_data(games, lines, embeddings)

    # initialize and train models
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)
    
    print("Training xgb_model...")
    xgb_model = cover_experiment.train_xgboost(X_train, y_train)
    print("Training attn_model...")
    attn_model = cover_experiment.train_attention_model(X_train, y_train)

    xgb_probs = xgb_model.predict_proba(X_test)
    attn_probs = cover_experiment.get_attn_probabailities(attn_model, X_test)
    
    breakpoint()
    xgb_preds = cover_experiment.get_predictions_fromProbs(xgb_probs)
    attn_preds = cover_experiment.get_predictions_fromProbs(attn_probs)

    
    # evaluate models
    #run_betting_experiment(models, X_test, y_test)
    evaluate_experiment(xgb_preds, y_test, model_name="XGBoost")
    evaluate_experiment(attn_preds, y_test, model_name="AttClassifier")

    # - Add method for inputting teams and outputting predictions - #
    print('Done')
    breakpoint()

if __name__ == "__main__":
    main()