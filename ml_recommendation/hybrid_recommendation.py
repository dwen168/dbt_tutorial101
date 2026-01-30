
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
from mlxtend.frequent_patterns import apriori, association_rules
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database config
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

def load_data(engine):
    logger.info("Loading data from database...")
    try:
        query = f"SELECT * FROM {DB_CONFIG['schema']}.fact_order_items"
        df_items = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df_items)} rows from fact_order_items.")
        return df_items
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        sys.exit(1)

class WeightedHybridRecommender:
    def __init__(self, df, weights={'cf': 0.4, 'content': 0.3, 'rules': 0.2, 'pop': 0.1}):
        self.df = df
        self.weights = weights
        
        # Models
        self.basket_encoded = None
        self.item_sim_df = None # CF
        self.content_sim_df = None # Content
        self.rules = None # Rules
        self.global_pop_score = None # Popularity (normalized)
        
        self._train_models()
        
    def _train_models(self):
        logger.info("Training component models...")
        
        # 1. Global Popularity (Normalized 0-1)
        pop_counts = self.df['product_name'].value_counts()
        self.global_pop_score = (pop_counts - pop_counts.min()) / (pop_counts.max() - pop_counts.min())
        
        # 2. Collaborative Filtering (Item-Item)
        # Basket: Rows=Orders, Cols=Products
        basket = self.df.groupby(['order_id', 'product_name'])['product_name'].count().unstack().reset_index().fillna(0).set_index('order_id')
        self.basket_encoded = basket.map(lambda x: 1 if x >= 1 else 0)
        
        # Cosine Similarity between Items (Transposed basket)
        item_user_matrix = self.basket_encoded.T
        sim_matrix = cosine_similarity(item_user_matrix)
        self.item_sim_df = pd.DataFrame(sim_matrix, index=self.basket_encoded.columns, columns=self.basket_encoded.columns)
        
        # 3. Association Rules (Market Basket)
        # We use a slightly looser support here to get more rules for the weighted mix
        frequent_itemsets = apriori(self.basket_encoded.astype(bool), min_support=0.005, use_colnames=True)
        if not frequent_itemsets.empty:
            self.rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
            # Normalize lift to 0-1 range for consistent weighting
            self.rules['lift_norm'] = (self.rules['lift'] - self.rules['lift'].min()) / (self.rules['lift'].max() - self.rules['lift'].min())
        else:
            self.rules = pd.DataFrame()
            
        # 4. Content Based
        product_features = self.df[['product_name', 'product_price', 'is_food_item', 'is_drink_item']].drop_duplicates('product_name').set_index('product_name')
        # Normalize price
        product_features['product_price'] = (product_features['product_price'] - product_features['product_price'].mean()) / product_features['product_price'].std()
        content_sim = cosine_similarity(product_features.fillna(0))
        self.content_sim_df = pd.DataFrame(content_sim, index=product_features.index, columns=product_features.index)
        
        logger.info("Training complete.")

    def get_integrated_scores(self, product_name=None, basket_items=None):
        """
        Returns a dictionary of {product: score} aggregating all signals
        """
        all_products = self.global_pop_score.index.tolist()
        scores = {p: 0.0 for p in all_products}
        
        # 1. Popularity Score (Baseline)
        w_pop = self.weights.get('pop', 0.1)
        for p, score in self.global_pop_score.items():
            scores[p] += score * w_pop
            
        # 2. Collaborative Filtering Score (if product_name provided)
        # Meaning: "People who bought 'product_name' also bought X"
        if product_name and product_name in self.item_sim_df.index:
            w_cf = self.weights.get('cf', 0.4)
            sim_scores = self.item_sim_df[product_name]
            for p, score in sim_scores.items():
                if p == product_name: continue
                scores[p] += score * w_cf
                
        # 3. Content Based Score (if product_name provided)
        # Meaning: "X looks similar to 'product_name'"
        if product_name and product_name in self.content_sim_df.index:
            w_content = self.weights.get('content', 0.3)
            sim_scores = self.content_sim_df[product_name]
            for p, score in sim_scores.items():
                if p == product_name: continue
                scores[p] += score * w_content
                
        # 4. Association Rules Score (if basket entries exist)
        # Meaning: "Buying [Basket] implies buying X"
        if basket_items and not self.rules.empty:
            w_rules = self.weights.get('rules', 0.2)
            # Find rules where antecedents are in basket
            # Simplifying: find rules where ANY basket item is in antecedent
            # For strictness, you might want antecedent to be subset of basket.
            # Here we sum up 'lift' or 'confidence' signals for triggered rules.
            
            # Filter for relevant rules
            # We look for rules where antecedent is a subset of the current basket
            basket_set = set(basket_items)
            relevant_rules = self.rules[self.rules['antecedents'].apply(lambda x: x.issubset(basket_set))]
            
            for _, row in relevant_rules.iterrows():
                consequents = list(row['consequents'])
                # lift_norm or confidence
                signal = row['confidence'] 
                for item in consequents:
                    if item not in basket_set: # Don't recommend what they have
                        scores[item] += signal * w_rules

        # Remove input items from recommendation
        exclude = set()
        if product_name: exclude.add(product_name)
        if basket_items: exclude.update(basket_items)
        
        final_scores = {k: v for k, v in scores.items() if k not in exclude}
        return final_scores

    def recommend(self, product_name=None, basket_items=None, top_n=5):
        scores = self.get_integrated_scores(product_name, basket_items)
        
        # Sort desc
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

def main():
    engine = get_db_connection()
    df = load_data(engine)
    
    # Define Weights for the Hybrid Mix
    # You can tune these!
    # e.g. if you trust User behavior (CF) more than metadata, give CF higher weight.
    weights = {'cf': 0.4, 'content': 0.2, 'rules': 0.3, 'pop': 0.1}
    
    recommender = WeightedHybridRecommender(df, weights)
    
    print("\n" + "="*50)
    print("WEIGHTED HYBRID RECOMMENDATION DEMO")
    print(f"Weights: {weights}")
    print("="*50)
    
    # Test Scenarios
    scenarios = [
        ("Viewing 'doctor stew' (No basket)", "doctor stew", []),
        ("Basket has 'mel-bun' (No current view)", None, ["mel-bun"]),
        ("Basket 'mel-bun' AND viewing 'doctor stew'", "doctor stew", ["mel-bun"]),
        ("Cold Start (No view, No basket)", None, [])
    ]
    
    for desc, prod, basket in scenarios:
        print(f"\nScenario: {desc}")
        recs = recommender.recommend(prod, basket)
        print("Top Recommendations:")
        for rank, (item, score) in enumerate(recs, 1):
            print(f"  {rank}. {item} (Score: {score:.4f})")

if __name__ == "__main__":
    main()
