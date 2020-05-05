import asyncio
import hashlib
from datetime import datetime
from typing import NamedTuple, Optional


Block = NamedTuple("Block", (
    ("name", str),
    ("block_num", int),
    ("data", Optional[int]),
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


def get_new_named_block(name, old_block: Block = None, **kwargs):
    if len(kwargs.keys()) == 0:
        return Block(
            name=name,
            block_num=0,
            data=None,
            next=None,
            hash=None,
            nonce=0,
            previous_hash=0x0,
            timestamp=datetime.now()
        )
    else:
        assert old_block is not None
        return Block(
            name=name,
            block_num=kwargs["block_num"] if "block_num" in kwargs.keys() else old_block.block_num,
            data=kwargs["data"] if "data" in kwargs.keys() else old_block.data,
            next=kwargs["next"] if "next" in kwargs.keys() else old_block.next,
            hash=kwargs["hash"] if "hash" in kwargs.keys() else old_block.hash,
            nonce=kwargs["nonce"] if "nonce" in kwargs.keys() else old_block.nonce,
            previous_hash=kwargs["previous_hash"] if "previous_hash" in kwargs.keys() else old_block.previous_hash,
            timestamp=datetime.now()
        )


def get_new_block_chain(old_block: Block = None, prev_block_chain: BlockChain = None, **kwargs):
    diff = 10
    if len(kwargs.keys()) == 0:
        return BlockChain(
            block_num=0,
            max_nonce=2 ** 32,
            diff=10,
            target=2 ** (256 - diff),
            block=old_block,
            head=old_block
        )
    else:
        assert old_block is not None
        return BlockChain(
            block_num=kwargs["block_num"] if "block_num" in kwargs.keys() else old_block.block_num,
            max_nonce=kwargs["max_nonce"] if "max_nonce" in kwargs.keys() else prev_block_chain.max_nonce,
            diff=kwargs["diff"] if "diff" in kwargs.keys() else prev_block_chain.diff,
            target=kwargs["target"] if "target" in kwargs.keys() else prev_block_chain.target,
            block=kwargs["block"] if "block" in kwargs.keys() else prev_block_chain.block,
            head=kwargs["head"] if "head" in kwargs.keys() else prev_block_chain.head
        )


def hash_block(block: Block):
    h = hashlib.sha256()
    h.update(
        str(block.nonce).encode('utf-8') +
        str(block.data).encode('utf-8') +
        str(block.previous_hash).encode('utf-8') +
        str(block.timestamp).encode('utf-8') +
        str(block.block_num).encode('utf-8')
    )
    return h.hexdigest()


def pr_block(block: Block):
    print("Block Hash: " + str(hash_block(block)) + "\nBlockNo: " + str(block.block_num) + "\nBlock Data: " + str(block.data) + "\nHashes: " + str(block.nonce) + "\n--------------")


def add_block_to_blockchain(block: Block, block_chain: BlockChain):
    previous_hash = hash_block(block)
    block_num = block_chain.block_num + 1
    new_block = get_new_named_block(
        f"Block #{block_num}",
        block,
        previous_hash=previous_hash,
        block_no=block_num
    )
    return new_block, get_new_block_chain(block, block_chain, next=new_block)


def mine(nxt_block: Block, block_chain: BlockChain):
    for n in range(block_chain.max_nonce):
        if int(hash_block(nxt_block), 16) <= block_chain.target:
            nxt_block, block_chain = add_block_to_blockchain(nxt_block, block_chain)
            pr_block(nxt_block)
        else:
            nxt_block = get_new_named_block(f"Block #{nxt_block.nonce}", nxt_block, nonce=nxt_block.nonce + 1)
    return nxt_block


def main():
    block_chain = get_new_block_chain()
    block = get_new_named_block("Genesis")
    for n in range(10):
        mine(block, block_chain)


if __name__ == '__main__':
    main()
