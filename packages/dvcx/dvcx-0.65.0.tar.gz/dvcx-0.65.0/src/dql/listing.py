import os
from itertools import zip_longest
from typing import Iterable, List, Optional

from attrs import asdict
from fsspec.asyn import get_loop, sync
from sqlalchemy.sql import func
from tqdm import tqdm

from dql.catalog.datasource import DataSource
from dql.client import Client
from dql.data_storage import AbstractDataStorage
from dql.node import DirType, Node, NodeWithPath
from dql.storage import Storage
from dql.utils import suffix_to_number


class Listing:
    def __init__(
        self,
        storage: Storage,
        data_storage: AbstractDataStorage,
        client: Client,
    ):
        if not data_storage.uri:
            raise ValueError("data_storage.uri cannot be empty in Listing")
        self.storage = storage
        self.data_storage = data_storage
        self.client = client

    def clone(self) -> "Listing":
        return self.__class__(self.storage, self.data_storage.clone(), self.client)

    @property
    def id(self):
        return self.storage.id

    def fetch(self, start_prefix=""):
        results = {}
        sync(get_loop(), self.client.fetch, self, start_prefix, results)
        if not results.get("total_count"):
            raise FileNotFoundError(f"Unable to resolve remote path: {start_prefix}")

    @staticmethod
    async def _insert_dir(data_storage, name, time, parent):
        return await data_storage.insert_node(
            {
                "vtype": "",
                "is_dir": True,
                "parent": parent,
                "name": name,
                "last_modified": time,
                "checksum": "",
                "etag": "",
                "version": "",
                "is_latest": True,
                "size": 0,
                "owner_name": "",
                "owner_id": "",
            },
        )

    async def insert_dir(self, name, time, path, data_storage=None):
        return await Listing._insert_dir(
            data_storage or self.data_storage,
            name,
            time,
            path,
        )

    async def insert_file(self, name, time, parent):
        node = Node(
            0,
            "",
            DirType.FILE,
            None,
            parent,
            name,
            last_modified=time,
        )
        await self.insert_file_from_node(node)

    async def insert_file_from_node(self, node):
        await self.data_storage.insert_node(asdict(node))

    async def insert_root(self, data_storage=None) -> int:
        return await (data_storage or self.data_storage).insert_root()

    def expand_path(self, path) -> List[Node]:
        return self.data_storage.expand_path(path)

    def resolve_path(self, path) -> Node:
        return self.data_storage.get_node_by_path(path)

    def ls_path(self, node, fields):
        if node.vtype == "tar" or node.dir_type == DirType.TAR_ARCHIVE:
            return self.data_storage.select_node_fields_by_parent_path_tar(
                node.path, fields
            )
        return self.data_storage.select_node_fields_by_parent_path(node.path, fields)

    def collect_nodes_to_instantiate(
        self,
        sources: Iterable[DataSource],
        copy_to_filename: Optional[str],
        recursive=False,
        copy_dir_contents=False,
        relative_path=None,
        from_edql=False,
        from_dataset=False,
    ) -> List[NodeWithPath]:
        rel_path_elements = relative_path.split("/") if relative_path else []
        all_nodes: List[NodeWithPath] = []
        for src in sources:
            node = src.node
            if recursive and src.is_container():
                dir_path = []
                if not copy_dir_contents:
                    dir_path.append(node.name)
                subtree_nodes = src.find(sort=["parent", "name"])
                all_nodes.extend(
                    NodeWithPath(n.n, path=dir_path + n.path) for n in subtree_nodes
                )
            else:
                node_path = []
                if from_edql:
                    for rpe, npe in zip_longest(
                        rel_path_elements, node.path.split("/")
                    ):
                        if rpe == npe:
                            continue
                        if npe:
                            node_path.append(npe)
                elif copy_to_filename:
                    node_path = [os.path.basename(copy_to_filename)]
                elif from_dataset:
                    node_path = [
                        src.listing.client.name,
                        node.parent,
                        node.name,
                    ]
                else:
                    node_path = [node.name]
                all_nodes.append(NodeWithPath(node, path=node_path))
        return all_nodes

    def instantiate_nodes(
        self,
        all_nodes,
        output,
        total_files=None,
        force=False,
        shared_progress_bar=None,
    ):
        progress_bar = shared_progress_bar or tqdm(
            desc=f"Instantiating '{output}'",
            unit=" files",
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )

        counter = 0
        for node in all_nodes:
            dst = os.path.join(output, *node.path)
            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)
            uid = node.n.as_uid(self.client.uri)
            self.client.instantiate_object(uid, dst, progress_bar, force)
            counter += 1
            if counter > 1000:
                progress_bar.update(counter)
                counter = 0

        progress_bar.update(counter)

    def find(
        self,
        node,
        fields,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        type=None,
        order_by=None,
    ):
        n = self.data_storage.nodes
        conds = []
        if names:
            for name in names:
                conds.append(n.c.name.op("GLOB")(name))
        if inames:
            for iname in inames:
                conds.append(func.lower(n.c.name).op("GLOB")(iname.lower()))
        if paths:
            node_path = self.data_storage.path_expr(n)
            for path in paths:
                conds.append(node_path.op("GLOB")(path))
        if ipaths:
            node_path = self.data_storage.path_expr(n)
            for ipath in ipaths:
                conds.append(func.lower(node_path).op("GLOB")(ipath.lower()))

        if size is not None:
            size_limit = suffix_to_number(size)
            if size_limit >= 0:
                conds.append(n.c.size >= size_limit)
            else:
                conds.append(n.c.size <= -size_limit)

        return self.data_storage.find(
            node,
            fields,
            type=type,
            conds=conds,
            order_by=order_by,
        )

    def du(self, node: Node, count_files: bool = False):
        return self.data_storage.size(node, count_files)
