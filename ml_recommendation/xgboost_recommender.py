
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "mysecretpassword",
    "schema": "raw"
}

def get_db_connection():
    conn_str = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(conn_str)

def load_and_prep_data(engine):
    logger.info("Loading data for Gradient Boosting...")
    
    # 1. Fetch Order Items (Positive Interactions)
    # We join with fact_orders to get time context
    query = f"""
        SELECT 
            i.order_id,
            i.product_id,
            i.product_price,
            i.is_food_item,
            i.is_drink_item,
            o.ordered_at
        FROM {DB_CONFIG['schema']}.fact_order_items i
        JOIN {DB_CONFIG['schema']}.fact_orders o ON i.order_id = o.order_id
        LIMIT 20000 -- Limit for demo speed
    """
    df_pos = pd.read_sql(query, engine)
    df_pos['target'] = 1  # 1 = Purchased
    
    # Extract unique products for negative sampling
    unique_products = df_pos[['product_id', 'product_price', 'is_food_item', 'is_drink_item']].drop_duplicates()
    
    logger.info(f"Loaded {len(df_pos)} positive interactions.")
    
    # 2. Generate Negative Samples (Items NOT purchased in an order)
    # Strategy: For each order in df_pos, randomly sample N distinct products that weren't bought.
    logger.info("Generating negative samples...")
    
    neg_samples = []
    
    # Get set of purchased products per order to exclude
    purchased_map = df_pos.groupby('order_id')['product_id'].apply(set).to_dict()
    all_product_ids = unique_products['product_id'].values
    
    # We'll create a dataframe of just order contexts
    orders_unique = df_pos[['order_id', 'ordered_at']].drop_duplicates()
    
    for _, row in orders_unique.iterrows():
        oid = row['order_id']
        bought_items = purchased_map.get(oid, set())
        
        # Pick 2 random negative items per order
        candidates = [p for p in all_product_ids if p not in bought_items]
        if not candidates:
            continue
            
        # Sample with replacement if needed, but here simple choice
        chosen_neg = np.random.choice(candidates, size=min(len(candidates), 2), replace=False)
        
        for neg_pid in chosen_neg:
            # Get product features for this negative item
            prod_info = unique_products[unique_products['product_id'] == neg_pid].iloc[0]
            
            neg_samples.append({
                'order_id': oid,
                'product_id': neg_pid,
                'product_price': prod_info['product_price'],
                'is_food_item': prod_info['is_food_item'],
                'is_drink_item': prod_info['is_drink_item'],
                'ordered_at': row['ordered_at'],
                'target': 0 # 0 = Not Purchased
            })
            
    df_neg = pd.DataFrame(neg_samples)
    
    # Combine
    df_full = pd.concat([df_pos, df_neg], ignore_index=True)
    
    # 3. Feature Engineering
    logger.info("Feature Engineering...")
    # Time features
    df_full['ordered_at'] = pd.to_datetime(df_full['ordered_at'])
    df_full['hour_of_day'] = df_full['ordered_at'].dt.hour
    df_full['day_of_week'] = df_full['ordered_at'].dt.dayofweek
    df_full['is_weekend'] = df_full['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Drop non-feature columns
    features_df = df_full.drop(columns=['order_id', 'product_id', 'ordered_at'])
    
    # Handle boolean cols (true/false -> 1/0) just in case
    features_df['is_food_item'] = features_df['is_food_item'].astype(int)
    features_df['is_drink_item'] = features_df['is_drink_item'].astype(int)
    
    return features_df

def train_gboost(df):
    logger.info("Training Gradient Boosting Classifier (sklearn)...")
    
    X = df.drop(columns=['target'])
    y = df['target']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, proba)
    
    logger.info(f"Model Accuracy: {acc:.4f}")
    logger.info(f"Model AUC: {auc:.4f}")
    
    return model, X.columns.tolist()

def explain_model(model, feature_names):
    print("\n--- Feature Importance ---")
    importance = model.feature_importances_
    # Sort
    indices = np.argsort(importance)[::-1]
    for f in range(len(feature_names)):
        print(f"{feature_names[indices[f]]}: {importance[indices[f]]:.4f}")

def main():
    engine = get_db_connection()
    df = load_and_prep_data(engine)
    
    model, feature_names = train_gboost(df)
    
    explain_model(model, feature_names)
    
    print("\n--- Insight ---")
    print("This model predicts the probability of an item being purchased based on:")
    print("1. Product Attributes (Price, Type)")
    print("2. Context (Time of day, Day of week)")
    print("In a real production system, you would use this to re-rank candidate items")
    print("generated by the retrieval stage (e.g., Collaborative Filtering).")

if __name__ == "__main__":
    main()
