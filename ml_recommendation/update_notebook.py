
import json

# Define the new cells to append
new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Part 3: Neural Collaborative Filtering (Deep Learning)\n",
            "\n",
            "We will use **PyTorch** to build a Neural Collaborative Filtering (NCF) model. \n",
            "This model learns latent vector representations (embeddings) for Orders and Products to predict the likelihood of a purchase."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import torch\n",
            "import torch.nn as nn\n",
            "import torch.optim as optim\n",
            "from torch.utils.data import Dataset, DataLoader\n",
            "from sklearn.preprocessing import LabelEncoder\n",
            "\n",
            "# PyTorch Dataset\n",
            "class OrderItemDataset(Dataset):\n",
            "    def __init__(self, user_ids, item_ids, targets):\n",
            "        self.user_ids = torch.tensor(user_ids, dtype=torch.long)\n",
            "        self.item_ids = torch.tensor(item_ids, dtype=torch.long)\n",
            "        self.targets = torch.tensor(targets, dtype=torch.float32)\n",
            "\n",
            "    def __len__(self):\n",
            "        return len(self.targets)\n",
            "\n",
            "    def __getitem__(self, idx):\n",
            "        return self.user_ids[idx], self.item_ids[idx], self.targets[idx]\n",
            "\n",
            "# Neural Network Model\n",
            "class NCFModel(nn.Module):\n",
            "    def __init__(self, num_users, num_items, embedding_dim=32):\n",
            "        super(NCFModel, self).__init__()\n",
            "        self.user_embedding = nn.Embedding(num_users, embedding_dim)\n",
            "        self.item_embedding = nn.Embedding(num_items, embedding_dim)\n",
            "        \n",
            "        # Simple MLP\n",
            "        self.fc1 = nn.Linear(embedding_dim * 2, 64)\n",
            "        self.fc2 = nn.Linear(64, 32)\n",
            "        self.output = nn.Linear(32, 1)\n",
            "        self.activation = nn.ReLU()\n",
            "        self.sigmoid = nn.Sigmoid()\n",
            "        \n",
            "    def forward(self, user_idx, item_idx):\n",
            "        u_emb = self.user_embedding(user_idx)\n",
            "        i_emb = self.item_embedding(item_idx)\n",
            "        x = torch.cat([u_emb, i_emb], dim=1)\n",
            "        x = self.activation(self.fc1(x))\n",
            "        x = self.activation(self.fc2(x))\n",
            "        x = self.sigmoid(self.output(x))\n",
            "        return x"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Data Preparation for Deep Learning\n",
            "\n",
            "# Re-load fresh data\n",
            "query = f\"SELECT order_id, product_name FROM {DB_CONFIG['schema']}.fact_order_items\"\n",
            "df_dl = pd.read_sql(query, engine)\n",
            "\n",
            "# Encode IDs\n",
            "order_encoder = LabelEncoder()\n",
            "item_encoder = LabelEncoder()\n",
            "df_dl['order_idx'] = order_encoder.fit_transform(df_dl['order_id'])\n",
            "df_dl['item_idx'] = item_encoder.fit_transform(df_dl['product_name'])\n",
            "\n",
            "num_orders = len(order_encoder.classes_)\n",
            "num_items = len(item_encoder.classes_)\n",
            "print(f\"Deep Learning Input: {num_orders} Orders, {num_items} Items\")\n",
            "\n",
            "# Create Samples (Positive + Negative)\n",
            "user_ids = df_dl['order_idx'].values\n",
            "item_ids = df_dl['item_idx'].values\n",
            "targets = np.ones(len(df_dl))\n",
            "\n",
            "# Negative Sampling (1:1)\n",
            "neg_user_ids = np.random.randint(0, num_orders, len(df_dl))\n",
            "neg_item_ids = np.random.randint(0, num_items, len(df_dl))\n",
            "neg_targets = np.zeros(len(df_dl))\n",
            "\n",
            "all_users = np.concatenate([user_ids, neg_user_ids])\n",
            "all_items = np.concatenate([item_ids, neg_item_ids])\n",
            "all_targets = np.concatenate([targets, neg_targets])"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train Loop\n",
            "dataset = OrderItemDataset(all_users, all_items, all_targets)\n",
            "dataloader = DataLoader(dataset, batch_size=64, shuffle=True)\n",
            "\n",
            "model_ncf = NCFModel(num_orders, num_items, embedding_dim=32)\n",
            "criterion = nn.BCELoss()\n",
            "optimizer = optim.Adam(model_ncf.parameters(), lr=0.001)\n",
            "\n",
            "print(\"Training Neural Network...\")\n",
            "epochs = 5\n",
            "for epoch in range(epochs):\n",
            "    total_loss = 0\n",
            "    for u, i, t in dataloader:\n",
            "        optimizer.zero_grad()\n",
            "        predictions = model_ncf(u, i).squeeze()\n",
            "        loss = criterion(predictions, t)\n",
            "        loss.backward()\n",
            "        optimizer.step()\n",
            "        total_loss += loss.item()\n",
            "    print(f\"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(dataloader):.4f}\")"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Visualize Learned Embeddings Similarity\n",
            "model_ncf.eval()\n",
            "with torch.no_grad():\n",
            "    item_embeddings = model_ncf.item_embedding.weight.data.numpy()\n",
            "\n",
            "def get_neural_recs(product_name, top_n=5):\n",
            "    if product_name not in item_encoder.classes_:\n",
            "        return []\n",
            "    \n",
            "    idx = item_encoder.transform([product_name])[0]\n",
            "    target_emb = item_embeddings[idx]\n",
            "    \n",
            "    # Cosine Sim\n",
            "    norms = np.linalg.norm(item_embeddings, axis=1)\n",
            "    dot_products = np.dot(item_embeddings, target_emb)\n",
            "    sims = dot_products / (norms * np.linalg.norm(target_emb))\n",
            "    \n",
            "    top_indices = np.argsort(sims)[::-1][1:top_n+1]\n",
            "    return [(item_encoder.inverse_transform([i])[0], sims[i]) for i in top_indices]\n",
            "\n",
            "print(\"Neural Recommendations for 'doctor stew':\")\n",
            "for item, score in get_neural_recs('doctor stew'):\n",
            "    print(f\"{item} (Sim: {score:.4f})\")"
        ]
    }
]

# Read existing notebook\n
with open('ml_recommendation/notebook.ipynb', 'r') as f:
    nb = json.load(f)

# Update Introduction
nb['cells'][0]['source'].append("\n    3. **Neural Collaborative Filtering**: Deep Learning approach using PyTorch.")

# Append new cells
nb['cells'].extend(new_cells)

# Write back
with open('ml_recommendation/notebook.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
