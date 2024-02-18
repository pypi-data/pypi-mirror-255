from .types import TraceTx
from typing import Callable, Optional, Dict
from treelib import Node, Tree
from tonpy import CellSlice
from .address import Address

__all__ = [
    "create_named_mapping_func",
    "defaultNamedFunction",
    "format_trace_tx",
    "pretty_print_trace_tx",
]

NamedFunction = Callable[[str], Optional[str]]


def truncateMiddlePart(address: Address, prefix: int, suffix: int) -> Optional[str]:
    """
    Truncate middle part of the address to make it more readable
    """
    address = address.to_string(True, is_test_only=False)
    return address[:prefix] + "..." + address[-suffix:] if len(address) > prefix + suffix else address


def defaultNamedFunction(address: Address, **kwargs) -> Optional[str]:
    """
    Truncate middle part of the address to make it more readable

    Parameters
    ----------
    address : str
        Address to be formatted
    prefix : int, optional
        Prefix length
    suffix : int, optional
        Suffix length
    """
    prefix = kwargs.get("prefix", 6)
    suffix = kwargs.get("suffix", 6)
    return truncateMiddlePart(address, prefix, suffix) if len(address) > prefix + suffix else address


def format_trace_tx(trace_tx: TraceTx, named_func: NamedFunction = defaultNamedFunction) -> str:
    """
    Format transaction trace in a pretty way
    A -> B (Value, Opcode)
    """
    raw_src = trace_tx.get("in_msg", {}).get("source", "")
    raw_dst = trace_tx.get("in_msg", {}).get("destination", "")
    src = Address(raw_src)
    dst = Address(raw_dst)
    value = int(trace_tx.get("in_msg", {}).get("value", "0")) / 1e9
    opcode = "invalid opcode"
    in_msg_data = trace_tx.get("in_msg", {}).get("msg_data", {})
    if in_msg_data.get("@type") == "msg.dataText":
        opcode = trace_tx.get("in_msg", {}).get("message")
    elif in_msg_data.get("@type") == "msg.dataRaw":
        cs = CellSlice(in_msg_data.get("body"))
        opcode = str(hex(cs.load_uint(32))).lower()
    return "{src} -> {dest} ({opcode}) [{value} TON]".format(
        src=named_func(src),
        dest=named_func(dst),
        value=value,
        opcode=opcode,
    )


def create_named_mapping_func(mapping: Dict[Address, str], truncate_address: bool = True) -> NamedFunction:
    """
    create a named function to map address to a more readable format
    For example, you can map address EQAuVtH68PRkM8qsMUh670ecNZPtqs5bANF3MD4dv-eBb2vD to "Alice" using this function
    if the address is not in the mapping, it will return the original address by default
    the original address can be truncated if truncate_address is True
    """

    def namedFunction(address: Address) -> Optional[str]:
        """
        Truncate middle part of the address to make it more readable
        """
        default = truncateMiddlePart(address, 6, 6) if truncate_address else address.to_string(True, is_test_only=False)
        return mapping.get(address, default)

    return namedFunction


def pretty_print_trace_tx(trace_tx: TraceTx, named_func: NamedFunction = defaultNamedFunction):
    """
    print transaction trace in a pretty way
    """

    def recursive_add_tx(tree: Tree, tx: TraceTx, parent: Optional[Node] = None):
        """
        Recursively add node to the tree
        """
        txhash = tx["transaction_id"]["hash"]
        tree.create_node(
            identifier=txhash,
            tag=format_trace_tx(tx, named_func),
            parent=parent,
        )
        for child in tx["children"]:
            recursive_add_tx(tree, child, txhash)

    tree = Tree()
    recursive_add_tx(tree, trace_tx)
    output = tree.show(stdout=False)
    print(output)
