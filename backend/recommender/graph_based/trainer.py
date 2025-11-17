import os
import gzip
import shutil
from pecanpy import pecanpy as node2vec
import numpy as np

NUM_WALKS = 5          
WALK_LENGTH = 15      
EMB_DIM = 64           
WINDOW = 5             
EPOCHS = 5             
WORKERS = 2            


def train_node2vec(files_dir):
    edge_file_gz = os.path.join(files_dir, "coauthor_edges.edgelist.gz")
    edge_file = os.path.join(files_dir, "coauthor_edges.edgelist")
    
		# Eliminar el archivo si ya existe
    if os.path.exists(edge_file):
        os.remove(edge_file)
        
    with gzip.open(edge_file_gz, 'rb') as f_in:
        with open(edge_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)	
            
    g = node2vec.SparseOTF(
				p=1.0,
				q=0.5,
				workers=WORKERS,
				verbose=True
		)
    
    g.read_edg(edge_file, weighted=True, directed=False, delimiter=' ')
    
    embeddings = g.embed(
					dim=EMB_DIM,
					num_walks=NUM_WALKS,
					walk_length=WALK_LENGTH,
					window_size=WINDOW,
					epochs=EPOCHS,
					verbose=True
			)
    
    npy_path = os.path.join(files_dir, "gb_author_embeddings.npy")
    #txt_path = os.path.join(files_dir, "cf_author_embeddings.txt")
    
    np.save(npy_path, embeddings)