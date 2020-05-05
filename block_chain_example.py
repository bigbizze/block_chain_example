import hashlib
import time
from datetime import datetime
from typing import NamedTuple, Optional, Any

Block = NamedTuple("Block", (
    ("name", str),
    ("block_num", int),
    ("next", any),
    ("hash", Optional[str]),
    ("nonce", int),
    ("previous_hash", int),
    ("timestamp", any)
))


BlockChain = NamedTuple("BlockChain", (
    ("block_num", int),
    ("max_nonce", int),
    ("diff", int),
    ("target", int),
    ("block", Block),
    ("head", Block)
))


def print_block(block: Block, time_taken: float):
    print(f"""
Block Name: {block.name}
Block Hash: {str(hash_block(block))}
Block Number: {str(block.block_num)}
Hashes: {str(block.nonce)}
Time Taken: {str(time_taken)}
--------------""".lstrip())


def get_state_dict(prev_state, **kwargs):
    if len(kwargs.keys()) == 0:
        kwargs = prev_state
    if isinstance(prev_state, dict):
        return prev_state, kwargs
    assert hasattr(prev_state, "_asdict")
    return dict(prev_state._asdict()), kwargs


def reducer(_type, prev_state: Any, **kwargs):
    """
    Reduces a set of actions (denoted as type: payload for key: value in kwargs)
    to return the next state.

    :param _type: reference to NamedTuple to be returned
    :param prev_state: the previous state
    :param kwargs: a set of actions, keys are property names, values are their values
    :return: NamedTuple
    """
    prev_state_dict, kwargs = get_state_dict(prev_state, **kwargs)
    params = {}
    for key in prev_state_dict.keys():
        if key in kwargs.keys():
            value = kwargs[key]
        else:
            value = prev_state_dict[key]
        params = {(k, v) for k, v in params if k is not key}
        params.add((key, value))
    return _type(**dict(params))


def get_initial_block(name) -> Block:
    return reducer(Block, {
        "name": name,
        "block_num": 0,
        "next": None,
        "hash": None,
        "nonce": 0,
        "previous_hash": 0x0,
        "timestamp": datetime.now()
    })


def get_new_named_block(prev_block: Block = None, **kwargs) -> Block:
    return reducer(Block, prev_block, **kwargs)


def get_initial_block_chain(prev_block: Block) -> BlockChain:
    return reducer(BlockChain, {
        "block_num": 0,
        "max_nonce": 2 ** 32,
        "diff": 10,
        "target": 2 ** (256 - 10),
        "block": prev_block,
        "head": prev_block
    })


def update_block_chain_state(prev_block_chain: BlockChain, **kwargs) -> BlockChain:
    return reducer(BlockChain, prev_block_chain, **kwargs)


def hash_block(block: Block):
    h = hashlib.sha256()
    h.update(
        str(block.name).encode('utf-8') +
        str(block.nonce).encode('utf-8') +
        str(block.previous_hash).encode('utf-8') +
        str(block.timestamp).encode('utf-8') +
        str(block.block_num).encode('utf-8')
    )
    return h.hexdigest()


def add_block_to_blockchain(block: Block, block_chain: BlockChain):
    block_num = block_chain.block_num + 1
    new_block = get_new_named_block(
        block,
        name=f"Block #{block_num}",
        previous_hash=hash_block(block),
        block_num=block_num
    )
    return new_block, update_block_chain_state(
        block_chain,
        next=new_block,
        block_num=block_num
    )


def mine(nxt_block: Block, block_chain: BlockChain):
    t = time.time()
    print_block(nxt_block, time.time() - t)
    for n in range(block_chain.max_nonce):
        if int(hash_block(nxt_block), 16) <= block_chain.target:
            nxt_block, block_chain = add_block_to_blockchain(nxt_block, block_chain)
            print_block(nxt_block, time.time() - t)
            t = time.time()
        else:
            nxt_block = get_new_named_block(
                nxt_block,
                name=f"Block #{nxt_block.nonce}",
                nonce=nxt_block.nonce + 1
            )


def main():
    block = get_initial_block("Patient 0")
    block_chain = get_initial_block_chain(block)
    for n in range(100):
        mine(block, block_chain)


if __name__ == '__main__':
    main()
