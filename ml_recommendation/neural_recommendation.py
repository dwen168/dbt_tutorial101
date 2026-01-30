
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sqlalchemy import create_engine
import sys
import logging
from sklearn.preprocessing import LabelEncoder

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
        # Load enough data to train
        query = f"SELECT order_id, product_name FROM {DB_CONFIG['schema']}.fact_order_items"
        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} rows.")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        sys.exit(1)

# PyTorch Dataset
class OrderItemDataset(Dataset):
    def __init__(self, user_ids, item_ids, targets):
        self.user_ids = torch.tensor(user_ids, dtype=torch.long)
        self.item_ids = torch.tensor(item_ids, dtype=torch.long)
        self.targets = torch.tensor(targets, dtype=torch.float32)

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, idx):
        return self.user_ids[idx], self.item_ids[idx], self.targets[idx]

# Neural Collaborative Filtering Model
class NCFModel(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=32):
        super(NCFModel, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        
        # Simple MLP to combine embeddings
        self.fc1 = nn.Linear(embedding_dim * 2, 64)
        self.fc2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, 1)
        self.activation = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, user_idx, item_idx):
        u_emb = self.user_embedding(user_idx)
        i_emb = self.item_embedding(item_idx)
        
        x = torch.cat([u_emb, i_emb], dim=1)
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.sigmoid(self.output(x))
        return x

class NeuralRecommender:
    def __init__(self, df):
        self.df = df
        self.model = None
        self.order_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()
        
        self._prepare_data()
        self._train_model()
        
    def _prepare_data(self):
        logger.info("Preprocessing data...")
        self.df['order_idx'] = self.order_encoder.fit_transform(self.df['order_id'])
        self.df['item_idx'] = self.item_encoder.fit_transform(self.df['product_name'])
        
        self.num_orders = len(self.order_encoder.classes_)
        self.num_items = len(self.item_encoder.classes_)
        logger.info(f"Num Orders: {self.num_orders}, Num Items: {self.num_items}")

        # Create Positive Samples
        user_ids = self.df['order_idx'].values
        item_ids = self.df['item_idx'].values
        targets = np.ones(len(self.df))
        
        # Simple Negative Sampling (1:1 ratio)
        # Randomly assign items to orders that didn't buy them
        # (Simplified: just random pairing, expecting collisions to be rare enough or handled)
        neg_user_ids = np.random.randint(0, self.num_orders, len(self.df))
        neg_item_ids = np.random.randint(0, self.num_items, len(self.df))
        neg_targets = np.zeros(len(self.df))
        
        self.all_users = np.concatenate([user_ids, neg_user_ids])
        self.all_items = np.concatenate([item_ids, neg_item_ids])
        self.all_targets = np.concatenate([targets, neg_targets])

    def _train_model(self, epochs=5, batch_size=64, embedding_dim=32):
        logger.info("Training Neural Network...")
        
        dataset = OrderItemDataset(self.all_users, self.all_items, self.all_targets)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.model = NCFModel(self.num_orders, self.num_items, embedding_dim)
        criterion = nn.BCELoss() # Binary Cross Entropy
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for u, i, t in dataloader:
                optimizer.zero_grad()
                predictions = self.model(u, i).squeeze()
                loss = criterion(predictions, t)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(dataloader):.4f}")
            
    def get_item_embeddings(self):
        """Extract learned item embeddings for similarity search"""
        self.model.eval()
        with torch.no_grad():
            embeddings = self.model.item_embedding.weight.data.numpy()
        return embeddings

    def recommend(self, product_name, top_n=5):
        """Recommend items based on cosine similarity of learned embeddings"""
        if product_name not in self.item_encoder.classes_:
            logger.warning(f"Product '{product_name}' not found in training data.")
            return []
            
        target_idx = self.item_encoder.transform([product_name])[0]
        embeddings = self.get_item_embeddings()
        
        target_emb = embeddings[target_idx]
        
        # Calculate Cosine Similarity
        # Sim(A, B) = (A . B) / (||A|| * ||B||)
        norms = np.linalg.norm(embeddings, axis=1)
        dot_products = np.dot(embeddings, target_emb)
        sims = dot_products / (norms * np.linalg.norm(target_emb))
        
        # Get Top N (excluding self)
        # Use argsort to get indices, convert to list, reverse, take top n+1
        top_indices = np.argsort(sims)[::-1][1:top_n+1] 
        
        recommendations = []
        for idx in top_indices:
            name = self.item_encoder.inverse_transform([idx])[0]
            score = sims[idx]
            recommendations.append((name, float(score)))
            
        return recommendations

def main():
    try:
        engine = get_db_connection()
        df = load_data(engine)
        
        logger.info("Initializing Deep Learning Recommender...")
        recommender = NeuralRecommender(df)
        
        test_product = "doctor stew"
        print(f"\nItems similar to '{test_product}' (learned via Neural Network):")
        recs = recommender.recommend(test_product)
        
        for rank, (item, score) in enumerate(recs, 1):
            print(f"{rank}. {item} (Similarity: {score:.4f})")
            
        # Another example
        test_product_2 = "mel-bun"
        print(f"\nItems similar to '{test_product_2}' (learned via Neural Network):")
        recs_2 = recommender.recommend(test_product_2)
        
        for rank, (item, score) in enumerate(recs_2, 1):
            print(f"{rank}. {item} (Similarity: {score:.4f})")

    except ImportError:
        logger.error("PyTorch not found. Please install torch: pip install torch")

if __name__ == "__main__":
    main()
