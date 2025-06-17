import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.difficulty = 4
        self.load_chain()

    def load_chain(self):
        # Initialize with empty data if file doesn't exist or is empty
        default_data = {"chain": [], "length": 0}
        
        try:
            if Path('data/blockchain.json').exists():
                with open('data/blockchain.json', 'r') as f:
                    try:
                        data = json.load(f)
                        if not data:  # Handle empty file
                            data = default_data
                    except json.JSONDecodeError:  # Handle invalid JSON
                        data = default_data
            else:
                data = default_data
                
            self.chain = data.get('chain', [])
            if not self.chain:  # If chain is empty, create genesis block
                self.create_genesis_block()
                
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            self.chain = []
            self.create_genesis_block()



    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': str(datetime.now()),
            'voter_token': '0',
            'candidate_id': '0',
            'previous_hash': '0',
            'nonce': 0,
            'hash': self.calculate_hash(0, '0', '0', '0', 0)
        }
        self.chain.append(genesis_block)
        self.save_chain()

    def calculate_hash(self, index, voter_token, candidate_id, previous_hash, nonce):
        value = f"{index}{voter_token}{candidate_id}{previous_hash}{nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    def proof_of_work(self, index, voter_token, candidate_id, previous_hash):
        nonce = 0
        while True:
            hash = self.calculate_hash(index, voter_token, candidate_id, previous_hash, nonce)
            if hash[:self.difficulty] == '0' * self.difficulty:
                return nonce, hash
            nonce += 1

    def add_vote(self, voter_token, candidate_id):
        previous_block = self.chain[-1]
        index = len(self.chain)
        previous_hash = previous_block['hash']
        
        nonce, hash = self.proof_of_work(index, voter_token, candidate_id, previous_hash)
        
        block = {
            'index': index,
            'timestamp': str(datetime.now()),
            'voter_token': voter_token,
            'candidate_id': candidate_id,
            'previous_hash': previous_hash,
            'nonce': nonce,
            'hash': hash
        }
        
        self.chain.append(block)
        self.save_chain()
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check hash integrity
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            
            # Verify proof of work
            hash = self.calculate_hash(
                current_block['index'],
                current_block['voter_token'],
                current_block['candidate_id'],
                current_block['previous_hash'],
                current_block['nonce']
            )
            
            if hash[:self.difficulty] != '0' * self.difficulty:
                return False
                
        return True

    def save_chain(self):
        data = {
            "chain": self.chain,
            "length": len(self.chain)
        }
        with open('data/blockchain.json', 'w') as f:
            json.dump(data, f, indent=4)

    def get_votes_for_candidate(self, candidate_id):
        return len([block for block in self.chain if block['candidate_id'] == candidate_id])

    def get_total_votes(self):
        return len(self.chain) - 1  # Exclude genesis block